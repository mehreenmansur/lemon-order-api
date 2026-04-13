from pydantic import BaseModel, validator, Field
from typing import Optional
from enum import Enum
import uuid
from uuid import UUID

class OrderSide(str, Enum):
    buy = "buy"
    sell = "sell"

class OrderType(str, Enum):
    market = "market"
    limit = "limit"

class OrderStatus(str, Enum):
    pending = "pending"
    placed = "placed"
    failed = "failed"

class OrderCreate(BaseModel):
    instrument: str = Field(..., examples=["DE000A0Q4RZ3"])
    side: OrderSide
    quantity: int = Field(..., examples=[10])
    type: OrderType
    limit_price: Optional[float] = Field(None, examples=[150.50])
    uuid_key: Optional[UUID] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Optional: If not provided, the server generates one. (But clients should provide it!)"
    )
    @validator("type")
    def validate_type(cls, v):
        if v not in ["market", "limit"]:
            raise ValueError("Invalid type")
        return v

    @validator("side")
    def validate_side(cls, v):
        if v not in ["buy", "sell"]:
            raise ValueError("Invalid side")
        return v

    @validator("limit_price", always=True)
    def validate_limit_price(cls, v, values):
        if values.get("type") == "limit" and v is None:
            raise ValueError("limit_price required for limit orders")
        return v
    
    class Config:
        use_enum_values = True
    

  