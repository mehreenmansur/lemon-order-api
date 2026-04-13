import threading
import time
from app.database import SessionLocal
from app.models import Order
from app.exchange import place_order, OrderPlacementError

def worker_loop():
    while True:
        db = SessionLocal()
        orders = db.query(Order).filter(Order.status == "pending").all()

        for order in orders:
            try:
                place_order(order)
                order.status = "completed"
            except OrderPlacementError:
                # retry later
                continue
            except Exception:
                order.status = "failed"

            db.commit()

        db.close()
        time.sleep(1)


def start_worker():
    thread = threading.Thread(target=worker_loop, daemon=True)
    thread.start()