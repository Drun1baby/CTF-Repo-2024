#!/bin/bash

set -e

if [ -z "$FLAG" ]; then
    echo "FLAG is not set"
    export FLAG="flag{test}"
fi

echo -n $FLAG > /flag
unset FLAG
chmod 400 /flag

# Terminate the processes after 15 minutes
su app -c 'python -m vulntagger' &
su bot -c 'python /app/bot.py' &
sleep 15m

# Kill all processes still running
kill -9 -1