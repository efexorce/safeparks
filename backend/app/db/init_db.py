import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, Base
from app.models import camera, alarm, energy, user, footage

logger = logging.getLogger(__name__)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def create_timescaledb_hypertables(session: AsyncSession) -> None:
    hypertable_queries = [
        "SELECT create_hypertable('energy_readings', 'recorded_at', if_not_exists => TRUE);",
        "SELECT create_hypertable('camera_events', 'occurred_at', if_not_exists => TRUE);",
        "SELECT create_hypertable('bandwidth_usage', 'recorded_at', if_not_exists => TRUE);",
        "SELECT create_hypertable('alarm_logs', 'triggered_at', if_not_exists => TRUE);",
    ]
    for query in hypertable_queries:
        try:
            await session.execute(text(query))
            await session.commit()
        except Exception as e:
            logger.warning(f"Hypertable creation skipped: {e}")


from sqlalchemy import text
