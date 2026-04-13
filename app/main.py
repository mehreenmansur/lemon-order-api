from fastapi import FastAPI, BackgroundTasks, HTTPException
from app.database import Base, engine, SessionLocal
from app.models import Order
from app.schemas import OrderCreate
from app.worker import start_worker
from app.exchange import place_order_at_exchange
from app.services import process_order_placement

app = FastAPI()

Base.metadata.create_all(bind=engine)
start_worker()


@app.post("/orders", status_code=201)
async def create_order(
    order: OrderCreate, 
    background_tasks: BackgroundTasks
):
    db = SessionLocal()

    key_str = str(order.uuid_key)

    existing_order = db.query(Order).filter(
        Order.uuid_key == key_str
    ).first()


    if existing_order:
        # If it exists, don't create a new one! 
        # Just return the existing one with a 200 OK (or its current status)
        return existing_order

    try:
        print("try")

        order_dict = order.dict()
        print(order_dict)

        order_dict['uuid_key'] = key_str
        print("2")

        print(order_dict)

        db_order = Order(**order_dict)
        print("3")

        print(db_order)

        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        background_tasks.add_task(process_order_placement, db_order.id, db)

        return db_order

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error while placing the order"},
        )
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    # Find orders stuck in PENDING from a previous session
    stuck_orders = db.query(Order).filter(Order.status == "PENDING").all()
    for order in stuck_orders:
        # Re-trigger the placement
        # BackgroundTasks.add_task(process_order_placement, order.id)
        BackgroundTasks.add_task(process_order_placement, order.id, db)

    db.close()