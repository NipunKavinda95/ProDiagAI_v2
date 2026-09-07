from pathlib import Path

from sqlalchemy import event
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    Boolean,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'prodiag.db'}"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
)


@event.listens_for(engine, "connect")
def configure_sqlite(connection, record):
    cursor = connection.cursor()

    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")

    cursor.close()


SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    machine_id: Mapped[str] = mapped_column(String(50), index=True)
    machine_name: Mapped[str] = mapped_column(String(150))
    timestamp: Mapped[str] = mapped_column(String(50), index=True)

    temperature_c: Mapped[float] = mapped_column(Float)
    vibration_mm_s: Mapped[float] = mapped_column(Float)
    current_a: Mapped[float] = mapped_column(Float)
    rpm: Mapped[float] = mapped_column(Float)

    status: Mapped[str] = mapped_column(String(30))

    health_score: Mapped[int] = mapped_column(Integer)
    health_status: Mapped[str] = mapped_column(String(30))

    # --------------------------------------------------------
    # ML PREDICTIONS
    # --------------------------------------------------------

    ml_health_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ml_failure_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ml_failure_within_1h: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(String, nullable=False, index=True)
    machine_name = Column(String, nullable=False)

    severity = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    status = Column(String, nullable=False, default="OPEN")

    fault_type = Column(String, nullable=True)
    reasons = Column(Text, nullable=True)
    anomaly_score = Column(Float, nullable=True)

    # --------------------------------------------------------
    # ML PREDICTIONS
    # --------------------------------------------------------

    ml_failure_probability = Column(
        Float,
        nullable=True,
    )

    ml_failure_within_1h = Column(
        Boolean,
        nullable=True,
    )

    created_at = Column(String, nullable=False)
    last_seen = Column(String, nullable=False)
    resolved_at = Column(String, nullable=True)


class FaultEvent(Base):
    __tablename__ = "fault_events"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(String, nullable=False, index=True)
    machine_name = Column(String, nullable=False)

    previous_condition = Column(String, nullable=True)
    new_condition = Column(String, nullable=False)

    fault_type = Column(String, nullable=True)
    reason = Column(String, nullable=True)

    timestamp = Column(String, nullable=False)


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(String, nullable=False, index=True)
    machine_name = Column(String, nullable=False)

    status = Column(String, nullable=False, default="OPEN")
    priority = Column(String, nullable=False, default="MEDIUM")

    fault_type = Column(String, nullable=True)
    fault_event_id = Column(Integer, nullable=True)
    alert_id = Column(Integer, nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    ai_diagnosis = Column(Text, nullable=True)
    ai_recommendation = Column(Text, nullable=True)

    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    completed_at = Column(String, nullable=True)


# ============================================================
# DATABASE MIGRATION
# ============================================================


def migrate_database():
    """
    Safely add new ML columns to an existing SQLite database.

    Existing data is preserved.
    Running this function multiple times is safe.
    """

    migrations = {
        "sensor_readings": {
            "ml_health_score": "FLOAT",
            "ml_failure_probability": "FLOAT",
            "ml_failure_within_1h": "BOOLEAN",
        },
        "alerts": {
            "ml_failure_probability": "FLOAT",
            "ml_failure_within_1h": "BOOLEAN",
        },
    }

    with engine.begin() as connection:

        for table_name, columns in migrations.items():

            result = connection.execute(text(f"PRAGMA table_info({table_name})"))

            existing_columns = {row[1] for row in result.fetchall()}

            for column_name, column_type in columns.items():

                if column_name not in existing_columns:

                    connection.execute(
                        text(
                            f"ALTER TABLE {table_name} "
                            f"ADD COLUMN {column_name} {column_type}"
                        )
                    )

                    print(f"[DB MIGRATION] Added " f"{table_name}.{column_name}")


def initialize_database():
    """
    Create missing tables and apply database migrations.
    """

    Base.metadata.create_all(engine)

    migrate_database()


def save_sensor_reading(reading):

    with SessionLocal() as session:

        sensor_reading = SensorReading(
            machine_id=reading["machine_id"],
            machine_name=reading["machine_name"],
            timestamp=reading["timestamp"],
            temperature_c=reading["temperature_c"],
            vibration_mm_s=reading["vibration_mm_s"],
            current_a=reading["current_a"],
            rpm=reading["rpm"],
            status=reading["status"],
            health_score=reading["health_score"],
            health_status=reading["health_status"],
            # ------------------------------------------------
            # ML PREDICTIONS
            # ------------------------------------------------
            ml_health_score=reading.get("ml_health_score"),
            ml_failure_probability=reading.get("ml_failure_probability"),
            ml_failure_within_1h=reading.get("ml_failure_within_1h"),
        )

        session.add(sensor_reading)
        session.commit()
