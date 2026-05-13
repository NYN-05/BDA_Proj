#!/bin/sh
# Mapper using awk for better compatibility
awk -F';' '
NF >= 3 && $1 != "Date" {
    split($1, d, "/")
    split($2, t, ":")
    key = d[3] "-" d[2] "-" d[1] " " t[1]
    v = $3
    gsub(/\?/, "", v)
    if (v + 0 == v) {
        printf "%s\t%s\n", key, v
    }
}'
