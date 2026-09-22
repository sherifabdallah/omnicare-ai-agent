"""Aggregate all v1 controllers under one prefix."""

from fastapi import APIRouter

from app.api.v1.controllers import chat_controller, conversation_controller, health_controller

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_controller.router)
api_v1_router.include_router(chat_controller.router)
api_v1_router.include_router(conversation_controller.router)
