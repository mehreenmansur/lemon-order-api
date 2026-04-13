import random
import time

def place_order_at_exchange(order_id: int):
    # Simulate 0.5s latency
    time.sleep(0.5)
    # 10% failure rate
    if random.random() < 0.10:
        return False
    return True

class OrderPlacementError(Exception):
    pass

def place_order(order):
    if random.random() < 0.1:
        raise OrderPlacementError("Failed to place order")

    time.sleep(0.5)