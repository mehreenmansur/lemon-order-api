import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import uuid

# --- Setup a separate clean Test Database ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- Test Cases ---

def test_create_order_success():
    """Requirement 1 & 5: API returns 201 immediately."""
    payload = {
        "instrument": "DE000A0Q4RZ3",
        "side": "buy",
        "quantity": 10,
        "type": "market",
        "uuid_key": str(uuid.uuid4())
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "pending"

def test_idempotency_protection():
    """Ensures duplicate UUIDs do not create duplicate records."""
    shared_uuid = str(uuid.uuid4())
    payload = {
        "instrument": "DE000A0Q4RZ3",
        "side": "buy",
        "quantity": 5,
        "type": "market",
        "uuid_key": shared_uuid
    }
    
    # First request
    response1 = client.post("/orders", json=payload)
    assert response1.status_code == 201
    
    # Second request with same UUID
    response2 = client.post("/orders", json=payload)
    # Depending on your logic, return 200 or 201, but the key is the data remains the same
    assert response2.status_code == 200 or response2.status_code == 201
    assert response1.json()["id"] == response2.json()["id"]

def test_invalid_uuid_format():
    """FastAPI/Pydantic validation check."""
    payload = {
        "instrument": "DE000A0Q4RZ3",
        "side": "buy",
        "quantity": 10,
        "type": "market",
        "uuid_key": "not-a-uuid"
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

import time
import uuid
from app.database import SessionLocal
from app.models import Order

def test_order_status_transitions_to_final_state():
    """
    Normal Flow: Verifies an order moves from 'pending' to 'placed' or 'failed'.
    """
    # 1. Post a new order
    payload = {
        "instrument": "DE000A0Q4RZ3",
        "side": "buy",
        "quantity": 10,
        "type": "market",
        "uuid_key": str(uuid.uuid4())
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    order_id = response.json()["id"]
    
    # 2. Wait for the background task to complete (delay is 0.5s)
    time.sleep(1.0)
    
    # 3. Check the database for the updated status
    db = SessionLocal()
    db_order = db.query(Order).filter(Order.id == order_id).first()
    
    assert db_order.status in ["completed", "failed"]
    db.close()