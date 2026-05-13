#!/bin/sh
# Reducer using awk for better compatibility
awk -F'\t' '
{
    key = $1
    val = $2
    if (current_key != key && current_key != "") {
        if (count > 0) {
            printf "%s,%.6f\n", current_key, total/count
        }
        current_key = key
        total = 0
        count = 0
    }
    current_key = key
    total += val
    count++
}
END {
    if (count > 0) {
        printf "%s,%.6f\n", current_key, total/count
    }
}'
