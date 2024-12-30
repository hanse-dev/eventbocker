#!/bin/bash

# Function to display usage information
show_usage() {
    echo "Usage: $0 [-d|--dev] [-p|--prod] [-h|--help]"
    echo "Options:"
    echo "  -d, --dev    Run in development mode"
    echo "  -p, --prod   Run in production mode"
    echo "  -h, --help   Show this help message"
    exit 1
}

# Function to stop running containers
stop_containers() {
    echo "Stopping any running containers..."
    docker-compose -f docker-compose.yml down 2>/dev/null
    docker-compose -f docker-compose.dev.yml down 2>/dev/null
}

# Check if no arguments provided
if [ $# -eq 0 ]; then
    show_usage
fi

# Parse command line arguments
while [ "$1" != "" ]; do
    case $1 in
        -d | --dev )
            MODE="dev"
            ;;
        -p | --prod )
            MODE="prod"
            ;;
        -h | --help )
            show_usage
            ;;
        * )
            echo "Invalid option: $1"
            show_usage
            ;;
    esac
    shift
done

# Stop any running containers
stop_containers

# Run the appropriate configuration
if [ "$MODE" = "dev" ]; then
    echo "Starting development environment..."
    docker-compose -f docker-compose.dev.yml up --build
elif [ "$MODE" = "prod" ]; then
    echo "Starting production environment..."
    docker-compose -f docker-compose.yml up --build
else
    show_usage
fi
