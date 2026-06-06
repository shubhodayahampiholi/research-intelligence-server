"""stdio transport runner."""

import asyncio
import os
import sys

from mcp.server.stdio import stdio_server

from research_server.observability.logging import configure_logging, get_logger
from research_server.server import SERVER_NAME, SERVER_VERSION, create_server

logger = get_logger(__name__)


async def run() -> None:
    server = create_server()
    logger.info(
        "Starting stdio transport",
        extra={"server": SERVER_NAME, "version": SERVER_VERSION}
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    configure_logging(level=os.environ.get("LOG_LEVEL", "INFO"))
    logger.info("Research Intelligence Server starting", extra={"transport": "stdio"})
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error("Server terminated", extra={"error": str(e)}, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()