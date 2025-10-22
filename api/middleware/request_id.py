"""
Request ID Middleware

Generates a unique ID for each request and stores it in context
for log correlation and debugging.
"""

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from api.logging_config import set_request_id, get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and track request IDs

    Adds X-Request-ID header to responses and sets request ID in logging context
    """

    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID')
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store in context for logging
        set_request_id(request_id)

        # Log incoming request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={'extra_fields': {
                'method': request.method,
                'path': request.url.path,
                'query': str(request.url.query) if request.url.query else None,
                'client': request.client.host if request.client else None,
            }}
        )

        # Process request
        try:
            response = await call_next(request)

            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id

            # Log response
            logger.info(
                f"{request.method} {request.url.path} → {response.status_code}",
                extra={'extra_fields': {
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': response.status_code,
                }}
            )

            return response

        except Exception as e:
            # Log error
            logger.error(
                f"{request.method} {request.url.path} → ERROR",
                exc_info=e,
                extra={'extra_fields': {
                    'method': request.method,
                    'path': request.url.path,
                    'error_type': type(e).__name__,
                }}
            )
            raise
