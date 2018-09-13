# This script spawns a server and client process.
# USAGE: ./run.sh 'PORT'
#
#!/bin/bash

set -eu

server_pid=
client_pid=

trap cleanup INT

cleanup() {
    kill $server_pid $client_pid
}

main() {
    PORT=$1
    TIMEOUT=2  # timeout to allow the server to start

    # TODO: figure out a way of retrieving server_pid from the spawned subshell,
    # to avoid cd'ing in and out.
    cd server
    python -O server.py -p $PORT &
    server_pid=$!
    cd ..

    sleep $TIMEOUT

    cd client
    python client.py -p $PORT
    client_pid=$!
}

if [ $# -ne 1 ]; then
    echo "Usage: ./run.sh 'PORT'"
    exit 1
fi

main $1
