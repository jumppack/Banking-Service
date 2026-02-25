import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

import uuid

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "Unknown"
        
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = uuid.uuid4().hex
            
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            
            # Inject it into response before finishing
            response.headers["X-Request-ID"] = request_id
            
            process_time = (time.time() - start_time) * 1000
            
            logger.info("Request completed", extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "status_code": response.status_code,
                "process_time_ms": round(process_time, 2),
                "request_id": request_id
            })
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error("Request failed with exception", extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "process_time_ms": round(process_time, 2),
                "error": str(e),
                "request_id": request_id
            })
            raise e
