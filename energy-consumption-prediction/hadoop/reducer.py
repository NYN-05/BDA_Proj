import sys

def emit(key, total, count):
    if count == 0:
        return
    avg = total / count
    print("{},{:.6f}".format(key, avg))

def main():
    current_key = None
    total = 0.0
    count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            key, value = line.split("\t", 1)
            value = float(value)
        except ValueError:
            continue

        if current_key is None:
            current_key = key

        if key != current_key:
            emit(current_key, total, count)
            current_key = key
            total = 0.0
            count = 0

        total += value
        count += 1

    if current_key is not None:
        emit(current_key, total, count)

if __name__ == "__main__":
    main()
