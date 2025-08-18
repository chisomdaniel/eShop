import uuid
import datetime
from sqids import Sqids

def generate_order_id(timestamp: datetime.datetime, sqids: Sqids) -> str:
    # Format timestamp
    ts_str = timestamp.strftime("%y%-m%d%H%M")
    ts_int = int(ts_str)

    # Encode timestamp with Sqids and uppercase
    ts_encoded = sqids.encode([ts_int]).upper()

    # Take 6 hex chars from UUID4
    uuid_part = uuid.uuid4().hex[:6].upper()

    return f"{ts_encoded}{uuid_part}"

def simulate_orders_per_minute(year: int, orders_per_minute: int, retries: int = 3):
    sqids = Sqids(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_length=4)
    collisions = []
    checked_minutes = 0

    # Simulate every minute of the year
    start = datetime.datetime(year, 1, 1, 0, 0)
    end = datetime.datetime(year + 1, 1, 1, 0, 0)
    delta = datetime.timedelta(minutes=1)

    current = start
    while current < end:
        ids = set()
        minute_collisions = 0

        for _ in range(orders_per_minute):
            attempt = 0
            while attempt <= retries:
                new_id = generate_order_id(current, sqids)
                if new_id not in ids:
                    ids.add(new_id)
                    break
                else:
                    attempt += 1

            if attempt > retries:  # true collision after retries
                minute_collisions += 1

        if minute_collisions > 0:
            collisions.append((current.strftime("%Y-%m-%d %H:%M"), minute_collisions))

        checked_minutes += 1
        current += delta

    return collisions, checked_minutes

# Example usage
if __name__ == "__main__":
    year = 2025
    orders_per_minute = 100000  # change to 1000, 1000000, etc
    collisions, total_minutes = simulate_orders_per_minute(year, orders_per_minute)

    print(f"Simulated {total_minutes:,} minutes for year {year}")
    if collisions:
        print("Collisions found:")
        for day, count in collisions:
            print(f"{day} -> {count} collisions")
    else:
        print("No collisions found")
