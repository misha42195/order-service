import sys
import time
from pathlib import Path
import logging

import uvicorn
from fastapi import (
    FastAPI,
)

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request


from api.routs.products import router as products_router
from api.routs.orders import router as orders_router
from api.routs.users import router as users_router
from api.routs.login import router as login_router
from rest.main_views import router as views_router

# from api.routs.producer_test import router as test_router

sys.path.append(str(Path(__file__).parent.parent))
app = FastAPI(
    title="SFMShop API",
    description="API интернет-магазина SFMShop",
)  # объект приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно заменить на ["http://localhost:63342"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(test_router, prefix="/test")
app.include_router(products_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(login_router, prefix="/api/v1")
app.include_router(views_router, prefix="/api/v1")


logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_request(request: Request, call_next):
    """Логирование метода и пути запроса и статуса ответа"""
    start_time = time.time()
    method = request.method
    path_request = request.url.path
    response = await call_next(request)
    response_status_code = response.status_code
    end_time = time.time() - start_time
    logger.info(
        "Метод запроса %s, путь запроса %s, статус код %s, время ответа %s",
        method,
        path_request,
        response_status_code,
        end_time,
    )
    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
