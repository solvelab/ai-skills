from fastapi import FastAPI

from app.api.items import router as items_router
from app.core.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="inventory")
    register_exception_handlers(app)
    app.include_router(items_router)
    return app


app = create_app()
