#!/bin/bash
# Zigbee Setup Helper Script
# This script helps with Docker setup, USB device detection, and initial configuration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

function print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function print_error() {
    echo -e "${RED}✗ $1${NC}"
}

function detect_usb_device() {
    print_info "Detecting Zigbee USB devices..."
    
    # Check for USB serial devices
    if [[ ! -d "/dev/serial/by-id" ]]; then
        print_error "No USB serial devices found"
        return 1
    fi
    
    devices=$(ls /dev/serial/by-id/ 2>/dev/null || true)
    
    if [[ -z "$devices" ]]; then
        print_error "No USB devices detected. Please plug in your Zigbee USB dongle."
        return 1
    fi
    
    print_info "Found USB devices:"
    for device in $devices; do
        actual_device=$(readlink -f "/dev/serial/by-id/$device")
        echo "  - /dev/serial/by-id/$device -> $actual_device"
    done
    
    # Also check ttyUSB
    tty_devices=$(ls /dev/ttyUSB* 2>/dev/null || true)
    if [[ -n "$tty_devices" ]]; then
        print_info "Also found direct ttyUSB devices:"
        for device in $tty_devices; do
            echo "  - $device"
        done
    fi
    
    return 0
}

function check_docker() {
    print_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        return 1
    fi
    
    print_success "Docker found: $(docker --version)"
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        return 1
    fi
    
    print_success "Docker Compose ready"
    return 0
}

function show_usage() {
    cat << EOF
${BLUE}Zigbee Smart Lighting - Setup Helper${NC}

Usage: ./setup_zigbee.sh [COMMAND]

Commands:
    detect          Detect USB Zigbee dongle
    check           Check Docker and dependencies
    start           Start Docker services
    stop            Stop Docker services
    logs            View Docker logs
    status          Check service status
    help            Show this help message

Examples:
    ./setup_zigbee.sh detect        # Find your USB dongle
    ./setup_zigbee.sh check         # Verify Docker setup
    ./setup_zigbee.sh start         # Launch all services
    ./setup_zigbee.sh logs          # Follow service logs
    ./setup_zigbee.sh status        # Check if services are running

EOF
}

function start_services() {
    print_info "Starting Docker services..."
    
    if ! check_docker; then
        print_error "Docker check failed"
        return 1
    fi
    
    # Check if device exists
    if [[ ! -e "/dev/ttyUSB0" ]] && [[ ! -L "/dev/serial/by-id/"* ]]; then
        print_warning "USB device not found at /dev/ttyUSB0"
        print_info "Available USB devices:"
        detect_usb_device
        print_warning "Update docker-compose.yml devices section if needed"
    fi
    
    print_info "Pulling latest images..."
    docker compose pull
    
    print_info "Building project image..."
    docker compose build
    
    print_info "Starting services (docker compose up -d)..."
    docker compose up -d
    
    sleep 2
    
    print_success "Services started!"
    print_info "Checking service status..."
    docker compose ps
    
    print_info "Zigbee2MQTT UI: http://localhost:8080"
    print_info "MQTT Broker: localhost:1883"
    
    return 0
}

function stop_services() {
    print_info "Stopping Docker services..."
    docker compose down
    print_success "Services stopped"
}

function show_logs() {
    print_info "Showing live logs (Ctrl+C to exit)..."
    docker compose logs -f
}

function show_status() {
    print_info "Service status:"
    docker compose ps
    
    print_info "\nContainer details:"
    docker compose ps -a
}

# Main logic
case "${1:-help}" in
    detect)
        detect_usb_device
        ;;
    check)
        check_docker && detect_usb_device
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
