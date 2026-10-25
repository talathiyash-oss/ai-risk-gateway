"""Review path for blocked RMs (FR-34, decision D-7).

The block stands until a reviewer decides. Approval reruns the original request with only the
guardrail that blocked it skipped, and only at the stage where it blocked, so every other check
(including GR-01 document filtering and GR-02 redaction) still applies.
"""
from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass
from typing import Callable

from airg.pipeline import Gateway, GatewayResult


# Only GR-01 blocks can be reviewed. Releasing a GR-03 block would hand the system prompt and
# canary to the RM, and GR-04 / error blocks are not judgement calls.
REVIEWABLE_GUARDS = frozenset({"GR-01"})


class ReviewNotFound(LookupError):
    pass


class ReviewExpired(LookupError):
    pass


class ReviewAlreadyDecided(ValueError):
    pass


class ReviewInProgress(ValueError):
    pass


class SelfReviewNotAllowed(PermissionError):
    pass


_MESSAGES = {
    "pending": "Waiting for a reviewer (target {n} minutes).",
    "approved": "Approved.",
    "rejected": "The review was declined.",
    "rerun_blocked": "Approved, but the answer still couldn't be released. Please contact support with your reference.",
    "expired": "This request expired before review. Please ask your question again.",
    "deciding": "Being reviewed now.",
}


@dataclass
class Review:
    review_id: str
    request_id: str
    user_id: str
    client_id: str
    blocked_by: str
    created_at: float
    status: str = "pending"
    reviewer_id: str | None = None
    decided_at: float | None = None
    answer: str | None = None


@dataclass(frozen=True)
class _Held:
    user_id: str
    client_id: str
    message: str  # kept in memory only, never written to the audit log
    blocked_by: str
    blocked_stage: str
    held_at: float


class ReviewQueue:
    def __init__(self, gateway: Gateway, audit=None, target_minutes: int = 15,
                 clock: Callable[[], float] = time.time, id_factory: Callable[[], str] | None = None,
                 held_ttl_seconds: float = 86_400, max_held: int = 1_000):
        self._gateway = gateway
        self._audit = audit
        self.target_minutes = target_minutes
        self._clock = clock
        self._new_id = id_factory or (lambda: "rv-" + uuid.uuid4().hex[:10])
        self._held_ttl = held_ttl_seconds
        self._max_held = max_held
        self._lock = threading.Lock()
        self._held: dict[str, _Held] = {}  # insertion-ordered: oldest first
        self._reviews: dict[str, Review] = {}
        self._by_request: dict[str, str] = {}

    def _purge(self) -> None:
        """Drop expired held entries. Caller holds the lock."""
        cutoff = self._clock() - self._held_ttl
        for rid in [r for r, h in self._held.items() if h.held_at <= cutoff]:
            del self._held[rid]

    def hold(self, result: GatewayResult, user_id: str, client_id: str, message: str) -> bool:
        """Keep a blocked request for review. Returns True if it was held (i.e. it is reviewable)."""
        if result.http_status != 403 or result.blocked_by not in REVIEWABLE_GUARDS:
            return False
        with self._lock:
            self._purge()
            self._held.pop(result.request_id, None)
            self._held[result.request_id] = _Held(user_id, client_id, message, result.blocked_by,
                                                  result.blocked_stage, self._clock())
            while len(self._held) > self._max_held:
                del self._held[next(iter(self._held))]
        return True

    def request(self, request_id: str, user_id: str) -> Review:
        with self._lock:
            self._purge()
            existing_id = self._by_request.get(request_id)
            if existing_id is not None:
                existing = self._reviews[existing_id]
                if existing.user_id != user_id:
                    raise ReviewNotFound(f"No reviewable request {request_id} for {user_id}")
                return existing
            held = self._held.get(request_id)
            if held is None or held.user_id != user_id:
                raise ReviewNotFound(f"No reviewable request {request_id} for {user_id}")
            review = Review(self._new_id(), request_id, user_id, held.client_id, held.blocked_by, self._clock())
            self._reviews[review.review_id] = review
            self._by_request[request_id] = review.review_id
        self._log("review_requested", review_id=review.review_id, request_id=request_id,
                  user_id=user_id, target_minutes=self.target_minutes)
        return review

    def get(self, review_id: str, user_id: str) -> Review:
        with self._lock:
            review = self._reviews.get(review_id)
            if review is None or review.user_id != user_id:
                raise ReviewNotFound(f"No review {review_id} for {user_id}")
            return review

    def decide(self, review_id: str, reviewer_id: str, approve: bool) -> Review:
        with self._lock:
            review = self._reviews.get(review_id)
            if review is None:
                raise ReviewNotFound(f"No review {review_id}")
            if review.status == "deciding":
                raise ReviewInProgress(f"Review {review_id} is being processed")
            if review.status != "pending":
                raise ReviewAlreadyDecided(f"Review {review_id} already {review.status}")
            if reviewer_id == review.user_id:
                raise SelfReviewNotAllowed("A requester cannot decide their own review")
            self._purge()
            held = self._held.get(review.request_id)
            if approve and held is None:
                decided_at = self._clock()
                review.status = "expired"
                review.reviewer_id = reviewer_id
                review.decided_at = decided_at
                expired = True
            else:
                expired = False
                review.status = "deciding"
        if expired:
            self._log("review_decided", review_id=review_id, request_id=review.request_id,
                      reviewer_id=reviewer_id, decision="expired",
                      minutes_taken=round((decided_at - review.created_at) / 60, 2))
            raise ReviewExpired(f"Held request {review.request_id} is no longer available")

        rerun = None
        try:
            if approve:
                rerun = self._gateway.handle(held.user_id, held.client_id, held.message,
                                             skip_stages=frozenset({(held.blocked_by, held.blocked_stage)}),
                                             override_of=review.request_id)
        except BaseException:
            with self._lock:
                review.status = "pending"
            raise

        if not approve:
            status, answer = "rejected", None
        elif rerun.status == "ok":
            status, answer = "approved", rerun.answer
        else:
            status, answer = "rerun_blocked", None
        decided_at = self._clock()
        with self._lock:
            review.reviewer_id = reviewer_id
            review.decided_at = decided_at
            review.answer = answer
            review.status = status
            self._held.pop(review.request_id, None)
        fields = {}
        if rerun is not None:
            fields = {"rerun_request_id": rerun.request_id, "rerun_http_status": rerun.http_status}
        self._log("review_decided", review_id=review_id, request_id=review.request_id,
                  reviewer_id=reviewer_id, decision=status,
                  minutes_taken=round((decided_at - review.created_at) / 60, 2), **fields)
        return review

    def public_view(self, review: Review) -> dict:
        return {"review_id": review.review_id, "request_id": review.request_id, "status": review.status,
                "target_minutes": self.target_minutes,
                "answer": review.answer if review.status == "approved" else None,
                "message": _MESSAGES[review.status].format(n=self.target_minutes)}

    def _log(self, event: str, **fields) -> None:
        if self._audit is not None:
            self._audit.record_event(event, **fields)
