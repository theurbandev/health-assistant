from dataclasses import dataclass
from typing import Any, Protocol

from app.garmin.catalog import is_supported_endpoint
from app.storage import HealthCache


class GarminProvider(Protocol):
    def refresh(self) -> None: ...


@dataclass
class GarminDataAccess:
    """Read-only data access surface exposed to the model."""

    cache: HealthCache

    def get_data(
        self,
        *,
        endpoint: str,
        start: str | None = None,
        end: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        if endpoint == "sync_status":
            return {"endpoint": endpoint, "data": self.cache.sync_status()}
        if not is_supported_endpoint(endpoint):
            raise ValueError(f"Unsupported Garmin endpoint: {endpoint}")
        return {
            "endpoint": endpoint,
            "start": start,
            "end": end,
            "data": self.cache.query_endpoint(endpoint=endpoint, start=start, end=end, limit=limit),
        }

