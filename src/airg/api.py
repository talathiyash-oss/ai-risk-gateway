"""HTTP API for the gateway. Run: uvicorn airg.api:build_default_app --factory"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from airg.config import load_config
from airg.data import generate_clients, load_clients
from airg.pipeline import BLOCK_MESSAGE, NOT_REVIEWABLE_MESSAGE, RATE_LIMIT_MESSAGE
from airg.reviews import (ReviewAlreadyDecided, ReviewExpired, ReviewInProgress, ReviewNotFound,
                          SelfReviewNotAllowed)
from airg.services import Services, build_services


ERROR_MESSAGE = "Something went wrong. Reference: {request_id}. Please try again shortly."


class ChatRequest(BaseModel):
    user_id: str
    client_id: str
    message: str = Field(min_length=1, max_length=4000)


class ReviewRequest(BaseModel):
    request_id: str
    user_id: str


class ReviewDecision(BaseModel):
    reviewer_id: str
    approve: bool


def create_app(services: Services) -> FastAPI:
    app = FastAPI(title="AI Risk Gateway")
    gateway, reviews = services.gateway, services.reviews

    @app.exception_handler(RequestValidationError)
    def invalid_request(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"message": "Invalid request"})

    @app.post("/v1/chat")
    def chat(req: ChatRequest):
        result = gateway.handle(req.user_id, req.client_id, req.message)
        if result.status == "ok":
            return {"request_id": result.request_id, "status": "ok", "answer": result.answer}
        reviewable = reviews.hold(result, req.user_id, req.client_id, req.message)
        if result.http_status == 429:
            template = RATE_LIMIT_MESSAGE
        elif reviewable:
            template = BLOCK_MESSAGE
        elif result.http_status == 403:
            template = NOT_REVIEWABLE_MESSAGE
        else:
            template = ERROR_MESSAGE
        return JSONResponse(status_code=result.http_status, content={
            "request_id": result.request_id, "status": "blocked",
            "message": template.format(request_id=result.request_id),
            "review_available": reviewable})

    @app.post("/v1/reviews", status_code=201)
    def request_review(req: ReviewRequest):
        try:
            return reviews.public_view(reviews.request(req.request_id, req.user_id))
        except ReviewNotFound:
            raise HTTPException(status_code=404, detail="No reviewable request found")

    @app.get("/v1/reviews/{review_id}")
    def get_review(review_id: str, user_id: str):
        try:
            return reviews.public_view(reviews.get(review_id, user_id))
        except ReviewNotFound:
            raise HTTPException(status_code=404, detail="Review not found")

    @app.post("/v1/reviews/{review_id}/decision")
    def decide(review_id: str, body: ReviewDecision):
        # NOTE: reviewer identity is not authenticated in the prototype (auth/SSO out of scope, PRD §9).
        try:
            return reviews.public_view(reviews.decide(review_id, body.reviewer_id, body.approve))
        except ReviewNotFound:
            raise HTTPException(status_code=404, detail="Review not found")
        except ReviewExpired:
            raise HTTPException(status_code=410,
                                detail="This request has expired. Please ask the RM to resubmit it.")
        except ReviewAlreadyDecided:
            raise HTTPException(status_code=409, detail="Review already decided")
        except ReviewInProgress:
            raise HTTPException(status_code=409, detail="Review is being processed")
        except SelfReviewNotAllowed:
            raise HTTPException(status_code=403, detail="Reviewers cannot decide their own requests")

    return app


def build_default_app() -> FastAPI:
    config = load_config(os.environ.get("AIRG_CONFIG", "config/gateway.yaml"))
    data_path = Path(os.environ.get("AIRG_DATA", "data/clients.json"))
    records = load_clients(data_path) if data_path.exists() else generate_clients()
    return create_app(build_services(config, records))
