"""MCP server assembly — wires all primitives to the server instance."""

import mcp.server as mcp_server
import mcp.types as types

from research_server.observability.logging import get_logger
from research_server.primitives.prompts import PROMPT_DEFINITIONS, handle_prompt_get
from research_server.primitives.resources import (
    RESOURCE_TEMPLATES,
    STATIC_RESOURCES,
    handle_resource_read,
)
from research_server.primitives.tools import TOOL_DEFINITIONS, handle_tool_call

logger = get_logger(__name__)

SERVER_NAME = "research-intelligence-server"
SERVER_VERSION = "1.0.0"


def create_server() -> mcp_server.Server:
    """
    Create and configure the MCP server instance.
    Called once at startup by the transport runner.
    """
    server = mcp_server.Server(SERVER_NAME)

    @server.list_resources()
    async def list_resources() -> list[types.Resource]:
        logger.info("Request: resources/list")
        return STATIC_RESOURCES

    @server.list_resource_templates()
    async def list_resource_templates() -> list[types.ResourceTemplate]:
        logger.info("Request: resources/templates/list")
        return RESOURCE_TEMPLATES

    @server.read_resource()
    async def read_resource(uri: types.AnyUrl) -> list[types.ResourceContents]:
        logger.info("Request: resources/read", extra={"uri": str(uri)})
        return handle_resource_read(uri)

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        logger.info("Request: tools/list")
        return TOOL_DEFINITIONS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        logger.info("Request: tools/call", extra={"tool": name})
        content, is_error = handle_tool_call(name, arguments or {})
        if is_error:
            raise types.ToolError(content[0].text if content else "Tool execution failed")
        return content

    @server.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        logger.info("Request: prompts/list")
        return PROMPT_DEFINITIONS

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
        logger.info("Request: prompts/get", extra={"prompt": name})
        return handle_prompt_get(name, arguments or {})

    logger.info(
        "Server created",
        extra={
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "tools": len(TOOL_DEFINITIONS),
            "resources": len(STATIC_RESOURCES),
            "templates": len(RESOURCE_TEMPLATES),
            "prompts": len(PROMPT_DEFINITIONS),
        },
    )

    return server