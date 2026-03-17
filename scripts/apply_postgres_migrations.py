from __future__ import annotations

import os
import re
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "database" / "migrations"
SCHEMA_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def get_config() -> dict[str, str | int]:
    load_dotenv(ROOT / ".env")

    schema = os.getenv("POSTGRES_SCHEMA", "public")
    if not SCHEMA_NAME_RE.fullmatch(schema):
        raise ValueError(
            "POSTGRES_SCHEMA must be a simple PostgreSQL identifier like public or clarus_app."
        )

    return {
        "host": os.getenv("POSTGRES_HOST"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "dbname": os.getenv("POSTGRES_DB"),
        "schema": schema,
    }


def validate_config(config: dict[str, str | int]) -> None:
    missing = [
        key
        for key in ("host", "user", "password", "dbname")
        if not config.get(key)
    ]
    if missing:
        joined = ", ".join(f"POSTGRES_{key.upper()}" for key in missing)
        raise ValueError(f"Missing required PostgreSQL environment variables: {joined}")


def ensure_schema_and_migrations_table(connection, schema: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
        cursor.execute(f'SET search_path TO "{schema}"')
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    connection.commit()


def get_applied_migrations(connection) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT filename FROM schema_migrations")
        return {row[0] for row in cursor.fetchall()}


def apply_migration(connection, filename: str, sql_text: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(sql_text)
        cursor.execute(
            "INSERT INTO schema_migrations (filename) VALUES (%s)",
            (filename,),
        )
    connection.commit()


def main() -> None:
    config = get_config()
    validate_config(config)

    connection = psycopg2.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        dbname=config["dbname"],
    )

    try:
        ensure_schema_and_migrations_table(connection, str(config["schema"]))
        applied = get_applied_migrations(connection)

        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        if not migration_files:
            print("No SQL migrations found.")
            return

        for migration_path in migration_files:
            if migration_path.name in applied:
                print(f"Skipping {migration_path.name} (already applied)")
                continue

            print(f"Applying {migration_path.name}...")
            sql_text = migration_path.read_text(encoding="utf-8")
            apply_migration(connection, migration_path.name, sql_text)
            print(f"Applied {migration_path.name}")

        print("PostgreSQL migrations are up to date.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
