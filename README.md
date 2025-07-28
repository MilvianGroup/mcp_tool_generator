# OpenAPI to MCP Server Generator

A generic Python tool that automatically converts OpenAPI 3.0 specifications into fully functional TypeScript MCP (Model Context Protocol) servers.

## Overview

This tool takes any OpenAPI specification and generates:
- Complete TypeScript MCP server with all endpoints as tools
- TypeScript interfaces for all schemas
- Input validation based on OpenAPI constraints
- Authentication handling (API Key, etc.)
- Proper error handling and HTTP status code mapping

## Features

- ✅ **Generic**: Works with any OpenAPI 3.0 specification
- ✅ **Type Safe**: Generates TypeScript interfaces from schemas
- ✅ **Validation**: Automatic input validation from OpenAPI constraints
- ✅ **Authentication**: Supports API Key authentication
- ✅ **$ref Resolution**: Handles schema references properly
- ✅ **Error Handling**: Comprehensive HTTP error handling
- ✅ **Raw JSON Output**: Returns clean JSON responses

## Prerequisites

Before using this tool, ensure you have the following installed and configured:

### System Requirements

- **Python 3.7+**: Required to run the OpenAPI to MCP generator script
  - Check version: `python3 --version`
  - Install from: [python.org](https://www.python.org/downloads/)

- **Node.js 18+**: Required for TypeScript compilation and MCP server runtime
  - Check version: `node --version`
  - Install from: [nodejs.org](https://nodejs.org/) or use a version manager like [nvm](https://github.com/nvm-sh/nvm)

- **npm**: Comes with Node.js, used for package management
  - Check version: `npm --version`

### Development Tools

- **TypeScript**: Required for compiling the generated MCP server
  - Install globally: `npm install -g typescript`
  - Check version: `tsc --version`

- **MCP SDK**: The Model Context Protocol SDK for TypeScript
  - Installed automatically when using the MCP server template
  - Manual install: `npm install @modelcontextprotocol/sdk`

### Additional Dependencies

The generator creates servers that require these npm packages:

- **axios**: For making HTTP requests to your API
  - Install: `npm install axios`
  - Used for all API communication in generated servers

### Optional Tools

- **Git**: For version control and cloning the MCP server template
  - Check version: `git --version`
  - Install from: [git-scm.com](https://git-scm.com/)

- **Code Editor**: VS Code recommended for TypeScript development
  - Download from: [code.visualstudio.com](https://code.visualstudio.com/)
  - Useful extensions: TypeScript, JSON, REST Client

### Environment Setup

1. **API Access**: Ensure you have:
   - A valid OpenAPI 3.0 specification file
   - API credentials (API keys, tokens, etc.)
   - Network access to your API endpoints

2. **File Permissions**: The generator needs:
   - Read access to your OpenAPI specification file
   - Write access to create/modify TypeScript files
   - Execute permissions for running npm commands

### Verification Commands

Run these commands to verify your setup:

```bash
# Check Python
python3 --version

# Check Node.js and npm
node --version
npm --version

# Check TypeScript
tsc --version

# Check if you can create MCP servers
npx @modelcontextprotocol/create-server --help
```

### Common Installation Issues

- **Python not found**: Make sure Python 3.7+ is in your PATH
- **Node.js version conflicts**: Use nvm to manage multiple Node.js versions
- **Permission errors**: On macOS/Linux, you may need `sudo` for global npm installs
- **TypeScript compilation errors**: Ensure you're using a compatible TypeScript version (4.0+)

## Requirements (Legacy)

- Python 3.7+
- Node.js and npm
- TypeScript
- MCP SDK

## Usage

### 1. Prepare Your OpenAPI Specification

Ensure you have a valid OpenAPI 3.0 specification file (JSON format). The tool supports:
- Path operations (GET, POST, PUT, DELETE, PATCH)
- Request body schemas with $ref references
- Response schemas
- Authentication schemes (API Key)
- Parameter validation (min/max, enums, etc.)

### 2. Set Up MCP Server Directory

```bash
# Create a new MCP server using the official template
npx @modelcontextprotocol/create-server your-api-server
cd your-api-server

# Install dependencies
npm install
npm install axios  # For HTTP requests
```

### 3. Copy the Generator Script

Copy `openapi_to_mcp.py` to your server directory:

```bash
cp /path/to/openapi_to_mcp.py ./
```

### 4. Copy Your OpenAPI Specification

```bash
cp /path/to/your-openapi-spec.json ./
```

### 5. Generate the MCP Server

```bash
python openapi_to_mcp.py your-openapi-spec.json
```

This will:
- Parse your OpenAPI specification
- Generate TypeScript interfaces for all schemas
- Create MCP tools for each API endpoint
- Generate the complete server code in `src/index.ts`
- Display a summary of generated tools

### 6. Build the Server

```bash
npm run build
```

### 7. Configure MCP Settings

Add your server to the MCP settings file:

**For Cline (VSCode):**
Edit `/Users/[username]/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

**For Claude Desktop:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "your-api-server": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "node",
      "args": [
        "/full/path/to/your-api-server/build/index.js"
      ],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Generated Code Structure

The generator creates:

### TypeScript Interfaces
```typescript
interface YourRequestSchema {
  /** Field description from OpenAPI */
  field: "enum1" | "enum2" | "enum3";
  optionalField?: number;
}
```

### MCP Tools
Each OpenAPI operation becomes an MCP tool with:
- Proper input schema validation
- HTTP method and path mapping
- Authentication headers
- Error handling

### Server Class
A complete MCP server class with:
- Axios instance with base URL and auth headers
- Tool handlers for each endpoint
- Error handling and logging

## Example

### Input: OpenAPI Specification
```json
{
  "openapi": "3.0.3",
  "info": {
    "title": "My API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://api.example.com/v1"
    }
  ],
  "paths": {
    "/users": {
      "post": {
        "operationId": "createUser",
        "summary": "Create a new user",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CreateUserRequest"
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "CreateUserRequest": {
        "type": "object",
        "required": ["name", "email"],
        "properties": {
          "name": {
            "type": "string",
            "description": "User's full name"
          },
          "email": {
            "type": "string",
            "description": "User's email address"
          }
        }
      }
    }
  }
}
```

### Generated Output
- **Tool**: `createUser` with proper input validation
- **Interface**: `CreateUserRequest` TypeScript interface
- **Validation**: Required fields (name, email) enforced
- **HTTP**: POST request to `/users` with JSON body

## Authentication Support

The generator supports API Key authentication:

```json
{
  "security": [
    {
      "ApiKeyAuth": []
    }
  ],
  "components": {
    "securitySchemes": {
      "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key"
      }
    }
  }
}
```

This automatically generates the appropriate authentication headers in the axios instance.

## Validation Features

The generator extracts validation rules from your OpenAPI spec:

- **Enums**: Converted to TypeScript union types
- **Min/Max**: Applied to number fields
- **Required fields**: Enforced in JSON schema
- **Types**: Proper TypeScript type mapping

## Error Handling

Generated servers include comprehensive error handling:

```typescript
catch (error) {
  if (axios.isAxiosError(error)) {
    return {
      content: [{
        type: 'text',
        text: `API error: ${error.response?.data?.error || error.message}`,
      }],
      isError: true,
    };
  }
  throw error;
}
```

## Troubleshooting

### Common Issues

1. **Empty input schemas**: Check that your OpenAPI spec has proper `requestBody` definitions with `$ref` references
2. **Build errors**: Ensure all TypeScript dependencies are installed
3. **Server not connecting**: Verify the build path in MCP settings matches the actual build output
4. **Authentication errors**: Confirm API key is correctly set in environment variables

### Debug Tips

1. Check the generated `src/index.ts` for any syntax issues
2. Verify your OpenAPI spec is valid JSON
3. Test API endpoints manually with curl before generating
4. Check MCP server logs for connection issues

## Extending the Generator

The `openapi_to_mcp.py` script can be extended to support:
- Additional authentication methods (OAuth, Bearer tokens)
- Custom response formatting
- Additional OpenAPI features (callbacks, webhooks)
- Custom TypeScript type mappings

## Example Projects

This generator was successfully used to create:
- **ESP32 IoT Device API**: Controls IoT devices via AWS API Gateway
- **REST API Wrappers**: Convert existing REST APIs to MCP tools
- **Microservice Integration**: Connect microservices through MCP

## Contributing

To improve the generator:
1. Add support for more OpenAPI features
2. Enhance TypeScript type generation
3. Add more authentication methods
4. Improve error handling and validation

The generator is designed to be generic and extensible for various API integration needs.
