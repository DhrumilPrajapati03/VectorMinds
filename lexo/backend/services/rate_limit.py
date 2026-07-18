"""In-memory per-user rate limits for upload + analyze (TKT-036 / TKT-035)."""

from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from uuid import UUID

from fastapi import Depends, HTTPException

from models.tables import User
from services.auth_service import get_current_user

logger = logging.getLogger(__name__)

# TKT-035 placeholder thresholds.
UPLOAD_LIMIT_PER_HOUR = 20
ANALYZE_LIMIT_PER_HOUR = 10
WINDOW_SECONDS = 3600

# key: (action, user_id) → timestamps of successful checks within the window
_buckets: dict[tuple[str, UUID], deque[float]] = defaultdict(deque)


def _prune_and_check(user_id: UUID, action: str, limit: int, detail: str) -> None:
    key = (action, user_id)
    now = time.monotonic()
    bucket = _buckets[key]
    cutoff = now - WINDOW_SECONDS
    while bucket and bucket[0] <= cutoff:
        bucket.popleft()
    if len(bucket) >= limit:
        logger.info(
            "rate_limit_exceeded action=%s user_id=%s count=%s limit=%s",
            action,
            user_id,
            len(bucket),
            limit,
        )
        raise HTTPException(status_code=429, detail=detail)
    bucket.append(now)


async def enforce_upload_rate_limit(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency: JWT + 20 uploads/user/hour."""
    _prune_and_check(
        current_user.id,
        "upload",
        UPLOAD_LIMIT_PER_HOUR,
        (
            "Upload rate limit exceeded. You may upload up to "
            f"{UPLOAD_LIMIT_PER_HOUR} documents per hour. Please try again later."
        ),
    )
    return current_user


async def enforce_analyze_rate_limit(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency: JWT + 10 analyze triggers/user/hour."""
    _prune_and_check(
        current_user.id,
        "analyze",
        ANALYZE_LIMIT_PER_HOUR,
        (
            "Analyze rate limit exceeded. You may start analysis up to "
            f"{ANALYZE_LIMIT_PER_HOUR} times per hour. Please try again later."
        ),
    )
    return current_user
