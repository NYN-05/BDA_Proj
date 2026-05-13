import sys
from datetime import datetime

def safe_float(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split(";")
        if parts[0] == "Date":
            continue
        if len(parts) < 3:
            continue

        date_str, time_str = parts[0], parts[1]
        gap = safe_float(parts[2].replace("?", "")) if len(parts[2]) > 0 else None
        if gap is None:
            continue

        try:
            dt = datetime.strptime("{} {}".format(date_str, time_str), "%d/%m/%Y %H:%M:%S")
        except ValueError:
            continue

        key = dt.strftime("%Y-%m-%d %H")
        print("{}\t{}".format(key, gap))

if __name__ == "__main__":
    main()
