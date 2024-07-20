import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(level=logging.INFO)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int, window: int):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.request_times = defaultdict(list)

    async def dispatch(self, request, call_next):
        client_ip = self.get_client_ip(request)
        current_time = datetime.utcnow()
        request_times = self.request_times[client_ip]

        # Remove old timestamps
        request_times = [time for time in request_times if (current_time - time).total_seconds() < self.window]
        self.request_times[client_ip] = request_times

        if len(request_times) >= self.max_requests:
            logging.info(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                content={"detail": "Rate limit exceeded"},
                status_code=429
            )

        # Record current request timestamp
        request_times.append(current_time)
        response = await call_next(request)
        return response

    def get_client_ip(self, request):
        # Extract client IP address from request
        return request.client.host
