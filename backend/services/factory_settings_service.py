from datetime import datetime, timezone

from sqlalchemy import text

from database import engine

DEFAULT_SETTINGS = {
    "company_name": "Manufactory Industrial LLC",
    "plant_name": "Dubai Manufacturing Plant",
    "location": "Dubai, UAE",
    "contact_person": "Maintenance Manager",
    "contact_detail": "+971 50 000 0000",
}


def initialize_factory_settings():
    """
    Create the factory_settings table if it does not exist and seed
    one default plant profile for a new database.
    """
    with engine.begin() as connection:
        connection.execute(text("""
                CREATE TABLE IF NOT EXISTS factory_settings (
                    id INTEGER PRIMARY KEY,
                    company_name VARCHAR(200) NOT NULL,
                    plant_name VARCHAR(200) NOT NULL,
                    location VARCHAR(200) NOT NULL,
                    contact_person VARCHAR(150),
                    contact_detail VARCHAR(150),
                    updated_at VARCHAR(50) NOT NULL
                )
                """))

        existing = connection.execute(
            text("SELECT id FROM factory_settings WHERE id = 1")
        ).first()

        if existing is None:
            connection.execute(
                text("""
                    INSERT INTO factory_settings (
                        id,
                        company_name,
                        plant_name,
                        location,
                        contact_person,
                        contact_detail,
                        updated_at
                    )
                    VALUES (
                        1,
                        :company_name,
                        :plant_name,
                        :location,
                        :contact_person,
                        :contact_detail,
                        :updated_at
                    )
                    """),
                {
                    **DEFAULT_SETTINGS,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )


def get_factory_settings():
    """Return the single active factory/plant profile."""
    initialize_factory_settings()

    with engine.connect() as connection:
        row = connection.execute(text("""
                SELECT
                    id,
                    company_name,
                    plant_name,
                    location,
                    contact_person,
                    contact_detail,
                    updated_at
                FROM factory_settings
                WHERE id = 1
                """)).mappings().first()

    if row is None:
        return None

    return dict(row)


def update_factory_settings(data):
    """
    Validate and update the active factory/plant profile.
    """
    if not isinstance(data, dict):
        raise ValueError("Settings data must be an object.")

    required_fields = (
        "company_name",
        "plant_name",
        "location",
    )

    cleaned = {}

    for field in required_fields:
        value = str(data.get(field, "")).strip()

        if not value:
            raise ValueError(f"{field} is required.")

        if len(value) > 200:
            raise ValueError(f"{field} is too long.")

        cleaned[field] = value

    contact_person = str(data.get("contact_person", "")).strip()

    contact_detail = str(data.get("contact_detail", "")).strip()

    if len(contact_person) > 150:
        raise ValueError("contact_person is too long.")

    if len(contact_detail) > 150:
        raise ValueError("contact_detail is too long.")

    initialize_factory_settings()

    updated_at = datetime.now(timezone.utc).isoformat()

    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE factory_settings
                SET
                    company_name = :company_name,
                    plant_name = :plant_name,
                    location = :location,
                    contact_person = :contact_person,
                    contact_detail = :contact_detail,
                    updated_at = :updated_at
                WHERE id = 1
                """),
            {
                **cleaned,
                "contact_person": contact_person,
                "contact_detail": contact_detail,
                "updated_at": updated_at,
            },
        )

    return get_factory_settings()
