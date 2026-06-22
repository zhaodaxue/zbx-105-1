from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db_data(db):
    from app.models import User, Role
    from app.auth import get_password_hash

    existing_users = db.query(User).count()
    if existing_users > 0:
        return

    users = [
        User(
            username="vendor1",
            hashed_password=get_password_hash("vendor123"),
            full_name="张摊主",
            role=Role.VENDOR,
        ),
        User(
            username="vendor2",
            hashed_password=get_password_hash("vendor123"),
            full_name="李摊主",
            role=Role.VENDOR,
        ),
        User(
            username="electrician1",
            hashed_password=get_password_hash("elec123"),
            full_name="王电工",
            role=Role.ELECTRICIAN,
        ),
        User(
            username="planner1",
            hashed_password=get_password_hash("plan123"),
            full_name="赵筹备",
            role=Role.PLANNER,
        ),
    ]
    db.add_all(users)
    db.commit()
