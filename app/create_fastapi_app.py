"""
FastAPI application factory with custom documentation and lifespan management.

This module provides a factory function for creating FastAPI applications with
customized Swagger UI and ReDoc documentation, async lifespan management,
and ORJSON response serialization.
"""
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse, JSONResponse, ORJSONResponse

from app.api import api_router
from app.core import db_helper
from app.core.exceptions import InsufficientStockError, NomenclatureNotFoundError, OrderNotFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Async context manager for FastAPI application lifecycle.

    Handles startup and shutdown events for the application, including
    database connection management.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control passes to the application runtime.

    """
    yield
    await db_helper.dispose()


def register_static_docs_routes(app: FastAPI) -> None:
    """
    Register custom static documentation routes for Swagger UI and ReDoc.

    This function sets up custom endpoints for API documentation with
    configurable CDN URLs for JavaScript and CSS resources.

    Args:
        app: FastAPI application instance to register routes on.

    Endpoints Created:
        - GET /docs: Custom Swagger UI interface
        - GET /oauth2-redirect.html: OAuth2 redirect handler for Swagger UI
        - GET /redoc: Custom ReDoc interface

    """

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        """
        Custom Swagger UI HTML endpoint.

        Returns:
            HTMLResponse: Rendered Swagger UI interface.

        Configuration:
            - Uses external CDN for Swagger UI assets
            - Includes OAuth2 redirect support
            - Custom title with application name
        """
        openapi_url = app.openapi_url or ""
        oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url or ""

        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url or "/oauth2-redirect.html"

    @app.get(oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect() -> HTMLResponse:
        """
        OAuth2 redirect handler for Swagger UI.

        Returns:
            HTMLResponse: OAuth2 redirect page for Swagger UI authentication.
        """
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html() -> HTMLResponse:
        """
        Custom ReDoc HTML endpoint.

        Returns:
            HTMLResponse: Rendered ReDoc interface.

        Configuration:
            - Uses external CDN for ReDoc assets
            - Custom title with application name
        """

        openapi_url = app.openapi_url or ""

        return get_redoc_html(
            openapi_url=openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
        )


def create_app(
    create_custom_static_urls: bool = False,
) -> FastAPI:
    """
    Factory function for creating configured FastAPI applications.

    Creates a FastAPI application with:
    - ORJSON response serialization for performance
    - Async lifespan management
    - Optional custom documentation endpoints

    Args:
        create_custom_static_urls: If True, registers custom documentation
                                  routes instead of using FastAPI defaults.

    Returns:
        FastAPI: Configured application instance.
    """

    app = FastAPI(
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url=None if create_custom_static_urls else "/docs",
        redoc_url=None if create_custom_static_urls else "/redoc",
    )

    @app.exception_handler(InsufficientStockError)
    async def insufficient_stock_exception_handler(request: Request, exc: InsufficientStockError) -> JSONResponse:
        """
        Handles InsufficientStockError exceptions globally within the FastAPI application.

        Logs the error and returns a 400 Bad Request JSON response to the client.

        Args:
            request: The incoming FastAPI request object.
            exc: The InsufficientStockError instance raised.

        Returns:
            A JSONResponse with HTTP status 400.
        """
        logger.error(f"Обработка InsufficientStockError для запроса {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(OrderNotFoundError)
    async def order_not_found_exception_handler(request: Request, exc: OrderNotFoundError) -> JSONResponse:
        """
        Handles OrderNotFoundError exceptions globally within the FastAPI application.

        Logs the error and returns a 404 Not Found JSON response to the client.

        Args:
            request: The incoming FastAPI request object.
            exc: The OrderNotFoundError instance raised.

        Returns:
            A JSONResponse with HTTP status 404.
        """
        logger.error(f"Обработка OrderNotFoundError для запроса {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(NomenclatureNotFoundError)
    async def nomenclature_not_found_exception_handler(request: Request,
                                                       exc: NomenclatureNotFoundError) -> JSONResponse:
        """
        Handles NomenclatureNotFoundError exceptions globally within the FastAPI application.

        Logs the error and returns a 404 Not Found JSON response to the client.

        Args:
            request: The incoming FastAPI request object.
            exc: The NomenclatureNotFoundError instance raised.

        Returns:
            A JSONResponse with HTTP status 404.
        """
        logger.error(f"Обработка NomenclatureNotFoundError для запроса {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    app.include_router(api_router)

    if create_custom_static_urls:
        register_static_docs_routes(app)

    return app
