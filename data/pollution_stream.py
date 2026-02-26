import time
import random
from datetime import datetime
import csv
import os

CITIES = ["Delhi", "Mumbai", "Kanpur"]

def write_pollution_to_csv():

    # Write header only if file is empty
    if not os.path.exists("pollution.csv") or os.stat("pollution.csv").st_size == 0:
        with open("pollution.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["city", "pm25", "timestamp"])

    while True:
        print("Generating simulated pollution data...")

        with open("pollution.csv", "a", newline="") as f:
            writer = csv.writer(f)

            for city in CITIES:
                pm25_value = random.randint(50, 450)

                writer.writerow([
                    city,
                    pm25_value,
                    datetime.utcnow().isoformat()
                ])

                print(f"Writing row for {city}: {pm25_value}")

        time.sleep(10)
