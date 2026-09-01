from pathlib import Path

from sqlalchemy import DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'prodiag.db'}"

engine = create_engine(DATABASE_URL)
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


def initialize_database():
    Base.metadata.create_all(engine)


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
            health_status=reading["health_status"]
        )

        session.add(sensor_reading)
        session.commit()