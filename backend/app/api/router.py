from fastapi import APIRouter

from .brands import router as brands_router
from .categories import router as categories_router
from .compare import router as compare_router
from .trends import router as trends_router
from .events import router as events_router
from .import_ import router as import_router
from .data_sources import router as data_sources_router
from .search import router as search_router
from .stats import router as stats_router
from .export import router as export_router
from .admin import router as admin_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(brands_router)
api_router.include_router(categories_router)
api_router.include_router(compare_router)
api_router.include_router(trends_router)
api_router.include_router(events_router)
api_router.include_router(import_router)
api_router.include_router(data_sources_router)
api_router.include_router(search_router)
api_router.include_router(stats_router)
api_router.include_router(export_router)
api_router.include_router(admin_router)
