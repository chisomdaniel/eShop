"""
You can use this script to simulate the use of our generate order id
logic and see how many times a collision occurs when a certain quantity
of order is placed in the same minute.
A retry policy is also set, so a collision will not be recorded unless 
the max retry limit exceeds and the collision still persist for that mins.
If you want to see what happens when no retry is happening at all (under
a no retry policy) you can set the default value for the function argument
`max_retries` to 1.
I recommend using a max_retry of 5 if the order quantity is expected to
exceed 5 in a single minute.
"""
import uuid
from datetime import datetime
import sqids


def generate_order_id(ts: datetime, sqids_encoder, max_retries=1):
    """
    Generate a unique order ID:
    - Encode timestamp with SQIDs
    - Append 6 chars from a UUID
    - Retry if collision
    """
    # Format timestamp
    ts_str = ts.strftime("%y%-m%d%H%M")  # e.g., '2508181430'
    ts_num = int(ts_str)

    for attempt in range(max_retries):
        # Encode timestamp with SQIDs
        encoded_ts = sqids_encoder.encode([ts_num]).upper()

        # Take 6 chars from a UUID
        uuid_suffix = uuid.uuid4().hex[:6].upper()

        # Combine
        order_id = f"{encoded_ts}{uuid_suffix}"

        if order_id not in seen_ids:
            seen_ids.add(order_id)
            return order_id

    # If still collides after retries
    collisions.append(order_id)
    return order_id


def simulate_orders_in_minute(order_count=1000, year=2025, month=8, day=18, hour=14, minute=30):
    global seen_ids, collisions
    seen_ids = set()
    collisions = []

    # Fix timestamp
    ts = datetime(year, month, day, hour, minute)

    # SQIDs encoder
    sqids_encoder = sqids.Sqids(
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        min_length=4  # You can tweak this
    )

    # Generate orders
    for _ in range(order_count):
        generate_order_id(ts, sqids_encoder)

    print(f"Simulated {order_count} orders in {ts.strftime('%Y-%m-%d %H:%M')}")
    print(f"Collisions after retries: {len(collisions)}")
    if collisions:
        print("Example collisions:", collisions[:5])


# Example usage
# simulate_orders_in_minute(order_count=1000)
simulate_orders_in_minute(order_count=1000000)
