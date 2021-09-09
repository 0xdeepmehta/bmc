from fastapi import APIRouter

# user related endpoints
from app.api.v1.endpoints.user import router as user_router

# initializing endpoints
router = APIRouter()

# integrating components endpoint to main router
router.include_router(user_router)