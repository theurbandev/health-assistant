from typing import Final

# These are local normalized endpoint names. Exact upstream Garmin API routes and response
# mappings will be filled in once the Garmin developer application is approved.
GARMIN_ENDPOINTS: Final[dict[str, str]] = {
    "daily_health": "Daily health summaries such as steps, calories, stress, and Body Battery.",
    "heart_rate": "Heart-rate observations and summaries.",
    "sleep": "Sleep sessions and sleep-stage summaries.",
    "activities": "Recorded activities and activity details.",
    "body_composition": "Weight and body-composition measurements.",
    "sync_status": "Garmin synchronization freshness and provider status.",
}


def is_supported_endpoint(endpoint: str) -> bool:
    return endpoint in GARMIN_ENDPOINTS

