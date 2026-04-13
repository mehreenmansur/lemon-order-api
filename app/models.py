from sqlalchemy import Column, Integer, String, Float, Index
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    instrument = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    side = Column(String, nullable=False)
    limit_price = Column(Float, nullable=True)
    status = Column(String, index=True, default="pending")  # pending, completed, failed
    uuid_key = Column(String, unique=True, index=True, nullable=False)

    # Composite Index: if you often search for 'buy' orders of a specific 'ISIN'
    __table_args__ = (Index('ix_instrument_side', 'instrument', 'side'),)