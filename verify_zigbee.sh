#!/usr/bin/env bash
# Zigbee Integration Checklist & Verification Script
# Run this to verify all Zigbee integration files are in place

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Zigbee Smart Lighting - Integration Verification${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Track results
files_found=0
files_total=0

check_file() {
    files_total=$((files_total + 1))
    local file=$1
    local description=$2
    
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✓${NC} $description"
        files_found=$((files_found + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $description - ${RED}NOT FOUND${NC}"
        return 1
    fi
}

check_dir() {
    files_total=$((files_total + 1))
    local dir=$1
    local description=$2
    
    if [[ -d "$dir" ]]; then
        echo -e "${GREEN}✓${NC} $description"
        files_found=$((files_found + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $description - ${RED}NOT FOUND${NC}"
        return 1
    fi
}

echo -e "${BLUE}Modified Files:${NC}"
check_file "docker-compose.yml" "docker-compose.yml (Zigbee2MQTT service added)"
check_file "Readme.md" "Readme.md (Zigbee documentation updated)"

echo ""
echo -e "${BLUE}New Files:${NC}"
check_file ".env.example" ".env.example (Configuration template)"
check_file "setup_zigbee.sh" "setup_zigbee.sh (Setup helper script)"
check_file "ZIGBEE_QUICKSTART.md" "ZIGBEE_QUICKSTART.md (Quick start guide)"
check_file "ZIGBEE_INTEGRATION.md" "ZIGBEE_INTEGRATION.md (Integration summary)"

echo ""
echo -e "${BLUE}Zigbee2MQTT Configuration:${NC}"
check_dir "zigbee2mqtt" "zigbee2mqtt/ directory"
check_file "zigbee2mqtt/configuration.yaml" "zigbee2mqtt/configuration.yaml"
check_dir "zigbee2mqtt/data" "zigbee2mqtt/data/ (persistent volume)"
check_file "zigbee2mqtt/mqtt_bridge.py" "zigbee2mqtt/mqtt_bridge.py (optional bridge)"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "Files verified: ${GREEN}$files_found / $files_total${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ $files_found -eq $files_total ]]; then
    echo -e "${GREEN}✓ All Zigbee integration files are in place!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Plug in your Zigbee USB dongle"
    echo "2. Run: ${YELLOW}./setup_zigbee.sh detect${NC} (verify device detection)"
    echo "3. Run: ${YELLOW}./setup_zigbee.sh start${NC} (start all services)"
    echo "4. Visit: ${YELLOW}http://localhost:8080${NC} (Zigbee2MQTT UI)"
    echo "5. Pair your Zigbee smart device"
    echo "6. Test with MQTT commands"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "- Quick Start: ${YELLOW}ZIGBEE_QUICKSTART.md${NC}"
    echo "- Full Details: ${YELLOW}ZIGBEE_INTEGRATION.md${NC}"
    echo "- Project Info: ${YELLOW}Readme.md${NC}"
else
    echo -e "${RED}✗ Some files are missing!${NC}"
    echo "Please check the file list above and run setup again."
    exit 1
fi

echo ""
echo -e "${BLUE}Directory Structure:${NC}"
echo ""
tree -L 2 --charset ascii 2>/dev/null || find . -maxdepth 2 -not -path '*/\.*' -not -path '*/build/*' -not -path '*/install/*' -not -path '*/src/*' | sort | sed 's|[^/]*/|  |g'

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Zigbee integration is ready! 🚀${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
