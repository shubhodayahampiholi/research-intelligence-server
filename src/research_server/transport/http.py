"""Streamable HTTP transport runner."""

import contextlib
import os

import uvicorn
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount

from research_server.observability.logging import configure_logging, get_logger
from research_server.server import SERVER_NAME, SERVER_VERSION, create_server

logger = get_logger(__name__)


def create_app() -> Starlette:
    """
    Create the Starlette app with Streamable HTTP transport mounted at /mcp.

    Stateless mode: no session state is maintained between requests.
    Every request is handled independently — correct for a read-only server.
    """
    server = create_server()

    session_manager = StreamableHTTPSessionManager(
        app=server,
        event_store=None,        # No resumability needed for stateless operation
        json_response=True,      # Return JSON rather than SSE streams for responses
        stateless=True,          # Each request is independent — no session tracking
    )

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with session_manager.run():
            logger.info(
                "Streamable HTTP transport ready",
                extra={"server": SERVER_NAME, "version": SERVER_VERSION},
            )
            yield

    return Starlette(
        routes=[Mount("/mcp", app=session_manager.handle_request)],
        lifespan=lifespan,
    )


def main() -> None:
    configure_logging(level=os.environ.get("LOG_LEVEL", "INFO"))
    logger.info("Research Intelligence Server starting", extra={"transport": "streamable-http"})

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    main()