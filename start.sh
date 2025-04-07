#!/bin/bash

FRONTEND_DIR="frontend"
BACKEND_DIR="backend"
BACKEND_PORT=5005
FRONTEND_PORT=3000
FRONTEND_URL="http://localhost:$FRONTEND_PORT"
BACKEND_URL="http://localhost:$BACKEND_PORT"
FRONTEND_PID_FILE=".frontend.pid"
BACKEND_PID_FILE=".backend.pid"
PROJECT_ROOT=$(pwd)

print_urls() {
    echo "Frontend URL: $FRONTEND_URL"
    echo "Backend URL: $BACKEND_URL"
}

get_pid() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        cat "$pid_file"
    else
        echo ""
    fi
}

is_running() {
    local pid=$1
    if [ -n "$pid" ] && ps -p "$pid" > /dev/null; then
        return 0
    else
        return 1
    fi
}

kill_process_on_port() {
    local port=$1
    local pids=$(lsof -ti:"$port")
    if [ -n "$pids" ]; then
        echo "Killing processes on port $port: $pids"
        for pid in $pids; do
            kill -9 "$pid" 2>/dev/null || true
        done
        # Wait a bit for the port to be released
        sleep 1
    else
        echo "No processes found on port $port"
    fi
    # verify that the port is released
    if lsof -ti:"$port" > /dev/null; then
        echo "Warning: Port $port is still in use"
        lsof -i:"$port"
        exit 1
    else
        echo "Port $port is released"
    fi
}

start_servers() {
    # Start backend
    backend_pid=$(get_pid "$BACKEND_PID_FILE")
    if ! is_running "$backend_pid"; then
        echo "Starting backend server..."
        kill_process_on_port "$BACKEND_PORT"
        PYTHONPATH="." uvicorn backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" > backend.log 2>&1 &
        echo $! > "$BACKEND_PID_FILE"
    else
        echo "Backend server is already running"
    fi

    # Start frontend
    frontend_pid=$(get_pid "$FRONTEND_PID_FILE")
    if ! is_running "$frontend_pid"; then
        echo "Starting frontend server..."
        kill_process_on_port "$FRONTEND_PORT"
        cd "$FRONTEND_DIR" || exit 1
        npm run dev > ../frontend.log 2>&1 &
        echo $! > "../$FRONTEND_PID_FILE"
        cd ..
        sleep 2
        open "$FRONTEND_URL"
    else
        echo "Frontend server is already running"
    fi

    print_urls
}

stop_servers() {
    echo "Stopping servers..."

    # Kill backend
    backend_pid=$(get_pid "$BACKEND_PID_FILE")
    if is_running "$backend_pid"; then
        echo "Killing backend process $backend_pid"
        kill -9 "$backend_pid" 2>/dev/null || true
        rm "$BACKEND_PID_FILE"
    fi
    kill_process_on_port "$BACKEND_PORT"

    # Kill frontend
    frontend_pid=$(get_pid "$FRONTEND_PID_FILE")
    if is_running "$frontend_pid"; then
        echo "Killing frontend process $frontend_pid"
        kill -9 "$frontend_pid" 2>/dev/null || true
        rm "$FRONTEND_PID_FILE"
    fi
    kill_process_on_port "$FRONTEND_PORT"

    # Double check and force kill any remaining processes
    pkill -f "uvicorn backend.main:app" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true

    # Final check for any remaining processes
    if lsof -ti:"$BACKEND_PORT" > /dev/null; then
        echo "Warning: Some processes still running on port $BACKEND_PORT"
        lsof -i:"$BACKEND_PORT"
    fi
    if lsof -ti:"$FRONTEND_PORT" > /dev/null; then
        echo "Warning: Some processes still running on port $FRONTEND_PORT"
        lsof -i:"$FRONTEND_PORT"
    fi
}

restart_servers() {
    stop_servers
    start_servers
}

check_status() {
    backend_pid=$(get_pid "$BACKEND_PID_FILE")
    if is_running "$backend_pid"; then
        echo "Backend server: Running (PID: $backend_pid)"
    else
        echo "Backend server: Stopped"
    fi

    frontend_pid=$(get_pid "$FRONTEND_PID_FILE")
    if is_running "$frontend_pid"; then
        echo "Frontend server: Running (PID: $frontend_pid)"
    else
        echo "Frontend server: Stopped"
    fi
}

show_help() {
    echo "Usage: $0 [OPTION]"
    echo "Manage frontend and backend servers"
    echo
    echo "Options:"
    echo "  --start    Start both servers"
    echo "  --stop     Stop both servers"
    echo "  --restart  Restart both servers (default)"
    echo "  --status   Show server status"
    echo "  --help     Show this help message"
    echo
    echo "The script will automatically:"
    echo "  - Start servers in background"
    echo "  - Open frontend in default browser"
    echo "  - Print server URLs"
}

case "$1" in
    --start)
        start_servers
        ;;
    --stop)
        stop_servers
        ;;
    --restart)
        restart_servers
        ;;
    --status)
        check_status
        ;;
    --help)
        show_help
        ;;
    *)
        restart_servers
        ;;
esac