from typing import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session, sessionmaker

from app.common.dependencies import get_db
from app.common.test_factories import UserFactory
from app.common.utilities import get_user_model
from app.core.config import settings
from app.core.db import Base
from app.core.main import app

User = get_user_model()

db_name = "db_for_tests"

DATABASE_URL = (
    f"postgresql+psycopg://{settings.database_user}:{settings.database_password}@"
    f"{settings.database_host}:{settings.database_port}/{db_name}"
)

admin_engine = create_engine(settings.database_url, isolation_level="AUTOCOMMIT")

engine_for_tests = create_engine(DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_for_tests)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db  # noqa


def create_test_database():
    with admin_engine.connect() as connection:
        connection.commit()
        try:
            connection.execute(text(f"CREATE DATABASE {db_name}"))
        except ProgrammingError:
            print("Database already exists, skipping creation...")


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    create_test_database()
    Base.metadata.create_all(bind=engine_for_tests)
    yield
    Base.metadata.drop_all(bind=engine_for_tests)


@pytest.fixture(autouse=True)
def setup_factories(session: Session):
    factories = (UserFactory,)

    for factory in factories:
        factory.set_sqlalchemy_session(session)


@pytest.fixture(scope="function")
def session() -> Generator[Session, None, None]:
    with engine_for_tests.connect() as connection:
        with connection.begin():
            with TestingSessionLocal(bind=connection) as session:
                yield session


@pytest.fixture
def user() -> User:
    return UserFactory()
