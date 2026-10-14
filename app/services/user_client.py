"""HTTP Client for inter-service communication with User Service."""
import logging
from typing import Any, Dict, Optional
import httpx
from fastapi import HTTPException, status
from app.core.config import settings

logger = logging.getLogger(__name__)


class UserClient:
    """Handles external HTTP calls to the User Service."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.USER_SERVICE_URL).rstrip("/")

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetches user info from User Service.
        Returns user data dictionary or None if user not found.
        Raises HTTPException 503 if User Service is unreachable.
        """
        url = f"{self.base_url}/users/{user_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == status.HTTP_200_OK:
                    return response.json()
                elif response.status_code == status.HTTP_404_NOT_FOUND:
                    return None
                else:
                    logger.warning(
                        f"User Service returned status {response.status_code} for user {user_id}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Failed to communicate properly with User Service.",
                    )
        except httpx.RequestError as exc:
            logger.error(f"Cannot reach User Service at {url}: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User Service is temporarily unavailable. Could not verify user registration status.",
            )
