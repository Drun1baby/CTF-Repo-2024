#!/bin/bash -xve

log_dir="./logs"
mkdir -p $log_dir

while true; do
    log_file="$log_dir/$(date +%Y-%m-%d_%H-%M-%S).log"
    timeout 15m docker compose up --build 2>&1 | tee $log_file
    docker compose down -v -t 5 2>&1 | tee -a $log_file
    sleep 5
    echo "Restarting"
done