#!/usr/bin/env python3
"""
Generic OpenAPI to MCP Server Generator

This script parses an OpenAPI specification and generates TypeScript code
for MCP (Model Context Protocol) tools that correspond to the API endpoints.
"""

import json
import sys
import os
from typing import Dict, Any, List, Optional
import re

class OpenAPIToMCP:
    def __init__(self, openapi_spec: Dict[str, Any]):
        self.spec = openapi_spec
        self.info = openapi_spec.get('info', {})
        self.servers = openapi_spec.get('servers', [])
        self.paths = openapi_spec.get('paths', {})
        self.components = openapi_spec.get('components', {})
        self.security = openapi_spec.get('security', [])
        
    def generate_typescript_interfaces(self) -> str:
        """Generate TypeScript interfaces from OpenAPI schemas"""
        interfaces = []
        schemas = self.components.get('schemas', {})
        
        for schema_name, schema_def in schemas.items():
            interface = self._generate_interface(schema_name, schema_def)
            if interface:
                interfaces.append(interface)
        
        return '\n\n'.join(interfaces)
    
    def _generate_interface(self, name: str, schema: Dict[str, Any]) -> str:
        """Generate a single TypeScript interface from a schema"""
        if schema.get('type') != 'object':
            return ""
        
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        interface_lines = [f"interface {name} {{"]
        
        for prop_name, prop_def in properties.items():
            prop_type = self._get_typescript_type(prop_def)
            optional = "" if prop_name in required else "?"
            description = prop_def.get('description', '')
            
            if description:
                interface_lines.append(f"  /** {description} */")
            interface_lines.append(f"  {prop_name}{optional}: {prop_type};")
        
        interface_lines.append("}")
        return '\n'.join(interface_lines)
    
    def _get_typescript_type(self, schema: Dict[str, Any]) -> str:
        """Convert OpenAPI schema type to TypeScript type"""
        schema_type = schema.get('type', 'any')
        
        if schema_type == 'string':
            enum_values = schema.get('enum')
            if enum_values:
                return ' | '.join(f'"{val}"' for val in enum_values)
            return 'string'
        elif schema_type == 'integer' or schema_type == 'number':
            return 'number'
        elif schema_type == 'boolean':
            return 'boolean'
        elif schema_type == 'array':
            items = schema.get('items', {})
            item_type = self._get_typescript_type(items)
            return f'{item_type}[]'
        elif schema_type == 'object':
            return 'any' # Could be more specific but keeping it simple
        else:
            return 'any'
    
    def generate_tools(self) -> List[Dict[str, Any]]:
        """Generate MCP tool definitions from OpenAPI paths"""
        tools = []
        
        for path, path_item in self.paths.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    tool = self._generate_tool(path, method.upper(), operation)
                    if tool:
                        tools.append(tool)
        
        return tools
    
    def _generate_tool(self, path: str, method: str, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a single MCP tool from an OpenAPI operation"""
        operation_id = operation.get('operationId')
        if not operation_id:
            # Generate operation ID from path and method
            operation_id = self._generate_operation_id(path, method)
        
        summary = operation.get('summary', '')
        description = operation.get('description', summary)
        
        # Generate input schema from parameters and request body
        input_schema = self._generate_input_schema(operation)
        
        return {
            'name': operation_id,
            'method': method,
            'path': path,
            'summary': summary,
            'description': description,
            'input_schema': input_schema,
            'responses': operation.get('responses', {}),
            'request_body': operation.get('requestBody')
        }
    
    def _generate_operation_id(self, path: str, method: str) -> str:
        """Generate operation ID from path and method"""
        # Remove path parameters and convert to camelCase
        clean_path = re.sub(r'\{[^}]+\}', '', path)
        parts = [part for part in clean_path.split('/') if part]
        
        if method.lower() == 'get':
            prefix = 'get'
        elif method.lower() == 'post':
            prefix = 'create' if 'create' in path.lower() else 'post'
        elif method.lower() == 'put':
            prefix = 'update'
        elif method.lower() == 'delete':
            prefix = 'delete'
        else:
            prefix = method.lower()
        
        if parts:
            name = prefix + ''.join(word.capitalize() for word in parts)
        else:
            name = prefix + 'Root'
        
        return name
    
    def _generate_input_schema(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON Schema for tool input from operation parameters and request body"""
        schema = {
            'type': 'object',
            'properties': {},
            'required': []
        }
        
        # Add path parameters
        parameters = operation.get('parameters', [])
        for param in parameters:
            if param.get('in') == 'path':
                param_schema = param.get('schema', {'type': 'string'})
                schema['properties'][param['name']] = {
                    'type': param_schema.get('type', 'string'),
                    'description': param.get('description', '')
                }
                if param.get('required', False):
                    schema['required'].append(param['name'])
        
        # Add query parameters
        for param in parameters:
            if param.get('in') == 'query':
                param_schema = param.get('schema', {'type': 'string'})
                schema['properties'][param['name']] = {
                    'type': param_schema.get('type', 'string'),
                    'description': param.get('description', '')
                }
                if param.get('required', False):
                    schema['required'].append(param['name'])
        
        # Add request body properties
        request_body = operation.get('requestBody')
        if request_body:
            content = request_body.get('content', {})
            json_content = content.get('application/json', {})
            body_schema = json_content.get('schema', {})
            
            # Handle $ref references
            if '$ref' in body_schema:
                ref_path = body_schema['$ref']
                if ref_path.startswith('#/components/schemas/'):
                    schema_name = ref_path.split('/')[-1]
                    body_schema = self.components.get('schemas', {}).get(schema_name, {})
            
            if body_schema.get('type') == 'object':
                properties = body_schema.get('properties', {})
                required = body_schema.get('required', [])
                
                for prop_name, prop_def in properties.items():
                    schema['properties'][prop_name] = {
                        'type': prop_def.get('type', 'string'),
                        'description': prop_def.get('description', ''),
                        'enum': prop_def.get('enum'),
                        'minimum': prop_def.get('minimum'),
                        'maximum': prop_def.get('maximum')
                    }
                    # Remove None values
                    schema['properties'][prop_name] = {k: v for k, v in schema['properties'][prop_name].items() if v is not None}
                
                schema['required'].extend(required)
        
        return schema
    
    def get_base_url(self) -> str:
        """Get the base URL from servers"""
        if self.servers:
            return self.servers[0]['url']
        return ''
    
    def get_security_info(self) -> Dict[str, Any]:
        """Extract security information"""
        security_schemes = self.components.get('securitySchemes', {})
        return {
            'schemes': security_schemes,
            'requirements': self.security
        }
    
    def generate_mcp_server_code(self) -> str:
        """Generate complete TypeScript MCP server code"""
        tools = self.generate_tools()
        interfaces = self.generate_typescript_interfaces()
        base_url = self.get_base_url()
        security_info = self.get_security_info()
        
        # Generate the main server code
        server_code = f'''#!/usr/bin/env node
import {{ Server }} from '@modelcontextprotocol/sdk/server/index.js';
import {{ StdioServerTransport }} from '@modelcontextprotocol/sdk/server/stdio.js';
import {{
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
}} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';

// Generated interfaces from OpenAPI spec
{interfaces}

// Configuration
const BASE_URL = '{base_url}';
const API_KEY = process.env.API_KEY;

if (!API_KEY) {{
  throw new Error('API_KEY environment variable is required');
}}

class {self._to_pascal_case(self.info.get('title', 'API'))}Server {{
  private server: Server;
  private axiosInstance;

  constructor() {{
    this.server = new Server(
      {{
        name: '{self.info.get('title', 'API').lower().replace(' ', '-')}-server',
        version: '{self.info.get('version', '1.0.0')}',
      }},
      {{
        capabilities: {{
          tools: {{}},
        }},
      }}
    );

    this.axiosInstance = axios.create({{
      baseURL: BASE_URL,
      headers: {{
        'Content-Type': 'application/json',
        {self._generate_auth_headers(security_info)}
      }},
    }});

    this.setupToolHandlers();
    
    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {{
      await this.server.close();
      process.exit(0);
    }});
  }}

  private setupToolHandlers() {{
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({{
      tools: [
{self._generate_tool_list(tools)}
      ],
    }}));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {{
      switch (request.params.name) {{
{self._generate_tool_handlers(tools)}
        default:
          throw new McpError(
            ErrorCode.MethodNotFound,
            `Unknown tool: ${{request.params.name}}`
          );
      }}
    }});
  }}

{self._generate_tool_methods(tools)}

  async run() {{
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('{self.info.get('title', 'API')} MCP server running on stdio');
  }}
}}

const server = new {self._to_pascal_case(self.info.get('title', 'API'))}Server();
server.run().catch(console.error);
'''
        
        return server_code
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase"""
        return ''.join(word.capitalize() for word in re.sub(r'[^a-zA-Z0-9]', ' ', text).split())
    
    def _generate_auth_headers(self, security_info: Dict[str, Any]) -> str:
        """Generate authentication headers based on security schemes"""
        schemes = security_info.get('schemes', {})
        
        for scheme_name, scheme in schemes.items():
            if scheme.get('type') == 'apiKey':
                header_name = scheme.get('name', 'X-API-Key')
                return f"'{header_name}': API_KEY,"
        
        return ""
    
    def _generate_tool_list(self, tools: List[Dict[str, Any]]) -> str:
        """Generate the tools array for ListToolsRequestSchema"""
        tool_definitions = []
        
        for tool in tools:
            input_schema_json = json.dumps(tool['input_schema'], indent=10)
            tool_def = f'''        {{
          name: '{tool['name']}',
          description: '{tool['description']}',
          inputSchema: {input_schema_json}
        }},'''
            tool_definitions.append(tool_def)
        
        return '\n'.join(tool_definitions)
    
    def _generate_tool_handlers(self, tools: List[Dict[str, Any]]) -> str:
        """Generate switch cases for tool handlers"""
        cases = []
        
        for tool in tools:
            case = f'''        case '{tool['name']}':
          return await this.{tool['name']}(request.params.arguments);'''
            cases.append(case)
        
        return '\n'.join(cases)
    
    def _generate_tool_methods(self, tools: List[Dict[str, Any]]) -> str:
        """Generate individual tool methods"""
        methods = []
        
        for tool in tools:
            request_config = self._generate_request_config(tool)
            method = f'''  private async {tool['name']}(args: any) {{
    try {{
      const response = await this.axiosInstance({{
        method: '{tool['method'].lower()}',
        url: '{tool['path']}',{request_config}
      }});

      return {{
        content: [
          {{
            type: 'text',
            text: JSON.stringify(response.data, null, 2),
          }},
        ],
      }};
    }} catch (error) {{
      if (axios.isAxiosError(error)) {{
        return {{
          content: [
            {{
              type: 'text',
              text: `API error: ${{error.response?.data?.error || error.response?.data?.message || error.message}}`,
            }},
          ],
          isError: true,
        }};
      }}
      throw error;
    }}
  }}'''
            methods.append(method)
        
        return '\n\n'.join(methods)
    
    def _generate_request_config(self, tool: Dict[str, Any]) -> str:
        """Generate axios request configuration for a tool"""
        config_parts = []
        
        # Handle request body for POST/PUT/PATCH
        if tool.get('request_body') and tool['method'].upper() in ['POST', 'PUT', 'PATCH']:
            config_parts.append("        data: args,")
        
        # For GET requests, we don't need additional config since there's no request body or query params in this API
        
        return '\n' + '\n'.join(config_parts) if config_parts else ""


def main():
    if len(sys.argv) != 2:
        print("Usage: python openapi_to_mcp.py <openapi_spec.json>")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    
    if not os.path.exists(spec_file):
        print(f"Error: File {spec_file} not found")
        sys.exit(1)
    
    try:
        with open(spec_file, 'r') as f:
            openapi_spec = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
    
    generator = OpenAPIToMCP(openapi_spec)
    
    # Generate TypeScript code
    typescript_code = generator.generate_mcp_server_code()
    
    # Write to index.ts
    output_file = 'src/index.ts'
    with open(output_file, 'w') as f:
        f.write(typescript_code)
    
    print(f"Generated MCP server code in {output_file}")
    print(f"Server info: {generator.info.get('title')} v{generator.info.get('version')}")
    print(f"Base URL: {generator.get_base_url()}")
    print(f"Generated {len(generator.generate_tools())} tools")

if __name__ == '__main__':
    main()
