# app/main.py (or services.py)
from sqlalchemy.orm import Session
from .exchange import place_order_at_exchange # Your dummy function
from .models import Order
import time

def process_order_placement(order_id: int, db: Session):
    # 1. Retrieve the order from the DB
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        return

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 2. Call the dummy exchange (Requirement 2 & 3)
            success = place_order_at_exchange(order_id)
            
            if success:
                order.status = "completed"
                db.commit()
                return
            else:
                # This handles the 10% failure rate
                order.status = "failed"
                
        except Exception:
            order.status = "FAILED"
        time.sleep(1)

    order.status = "FAILED"
    db.commit()
    
    # 3. Save the final result
    