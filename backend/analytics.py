import csv
from statistics import mean

from db.session import get_session
from db.models import BatteryData, Metrics

def compute_metrics(file_path: str, battery_data_id: int):
    voltages, currents, temps = [], [], []

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                voltages.append(float(row["voltage"]))
                currents.append(float(row["current"]))
                temps.append(float(row["temperature"]))
            except (ValueError, KeyError):
                continue

    metrics = Metrics(
        battery_data_id=battery_data_id,
        avg_voltage=mean(voltages) if voltages else None,
        min_voltage=min(voltages) if voltages else None,
        max_voltage=max(voltages) if voltages else None,
        avg_current=mean(currents) if currents else None,
        avg_temperature=mean(temps) if temps else None,
    )

    with get_session() as s:
        s.add(metrics)
        s.flush()

    return metrics
