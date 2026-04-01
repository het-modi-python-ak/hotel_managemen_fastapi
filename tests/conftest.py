import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.database import Base, get_db
from app.core.dependencies import get_current_user

# Setup SQLite in-memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 1. Define the fixture with the @pytest.fixture decorator
@pytest.fixture
def client():
    # Dependency overrides
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    class MockUser:
        id = 2
        email = "pe@gmail.com"

    def override_get_current_user():
        return MockUser()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Yield the client to the test
    with TestClient(app) as c:
        yield c
    
    # Drop tables after test is done
    Base.metadata.drop_all(bind=engine)
