import json
import sqlite3
from collections.abc import Mapping
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class HealthCache:
    """Small local cache for normalized Garmin API responses.

    The cache is deliberately accessed through named, read-only endpoint methods. The model
    never receives a database connection or credentials.
    """

    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS garmin_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    source_record_id TEXT NOT NULL UNIQUE,
                    recorded_at TEXT,
                    payload_json TEXT NOT NULL,
                    ingested_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_garmin_records_endpoint_time
                    ON garmin_records(endpoint, recorded_at);

                CREATE TABLE IF NOT EXISTS sync_state (
                    provider TEXT PRIMARY KEY,
                    last_successful_sync TEXT,
                    cursor TEXT,
                    status TEXT NOT NULL DEFAULT 'never_synced'
                );
                """
            )

    def put_record(
        self,
        *,
        endpoint: str,
        source_record_id: str,
        payload: Mapping[str, Any],
        recorded_at: datetime | None = None,
    ) -> None:
        ingested_at = datetime.now(UTC).isoformat()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO garmin_records(endpoint, source_record_id, recorded_at, payload_json, ingested_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source_record_id) DO UPDATE SET
                    endpoint=excluded.endpoint,
                    recorded_at=excluded.recorded_at,
                    payload_json=excluded.payload_json,
                    ingested_at=excluded.ingested_at
                """,
                (
                    endpoint,
                    source_record_id,
                    recorded_at.isoformat() if recorded_at else None,
                    json.dumps(payload, separators=(",", ":")),
                    ingested_at,
                ),
            )

    def query_endpoint(
        self,
        *,
        endpoint: str,
        start: str | None = None,
        end: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        clauses = ["endpoint = ?"]
        values: list[Any] = [endpoint]
        if start:
            clauses.append("recorded_at >= ?")
            values.append(start)
        if end:
            clauses.append("recorded_at <= ?")
            values.append(end)

        query = f"""
            SELECT source_record_id, recorded_at, payload_json, ingested_at
            FROM garmin_records
            WHERE {' AND '.join(clauses)}
            ORDER BY recorded_at ASC
            LIMIT ?
        """
        values.append(limit)

        with self._connection() as connection:
            rows = connection.execute(query, values).fetchall()

        return [
            {
                "source_record_id": row["source_record_id"],
                "recorded_at": row["recorded_at"],
                "ingested_at": row["ingested_at"],
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]

    def sync_status(self) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT provider, last_successful_sync, cursor, status FROM sync_state WHERE provider = ?",
                ("garmin",),
            ).fetchone()
        if row is None:
            return {"provider": "garmin", "status": "never_synced", "last_successful_sync": None}
        return dict(row)
