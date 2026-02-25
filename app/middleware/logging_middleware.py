import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "Unknown"
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            logger.info("Request completed", extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "status_code": response.status_code,
                "process_time_ms": round(process_time, 2)
            })
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error("Request failed with exception", extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "process_time_ms": round(process_time, 2),
                "error": str(e)
            })
            raise e
