#!/bin/bash

# WiFi Helper Setup Script for Raspberry Pi Zero 2 W
# Run this once with sudo to set up permissions
# Usage: sudo bash setup_wifi_helper.sh [username]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the username (default to current sudo user)
TARGET_USER=${1:-$SUDO_USER}
if [ -z "$TARGET_USER" ]; then
    echo -e "${RED}Error: Could not determine target user${NC}"
    echo "Usage: sudo bash setup_wifi_helper.sh [username]"
    exit 1
fi

echo -e "${GREEN}Setting up WiFi Helper for user: $TARGET_USER${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p /etc/hostapd
mkdir -p /etc/wifi-helper
mkdir -p /var/backups/wifi_helper
mkdir -p /var/log/wifi-helper

# Create a dedicated group for wifi management
echo -e "${YELLOW}Creating wifi-admin group...${NC}"
groupadd -f wifi-admin
usermod -a -G wifi-admin $TARGET_USER

# Set up configuration file permissions
echo -e "${YELLOW}Setting up configuration files...${NC}"

# Create empty config files if they don't exist
touch /etc/hostapd/hostapd.conf
touch /etc/dnsmasq.conf
touch /etc/dhcpcd.conf

# Set ownership and permissions for config files
chown root:wifi-admin /etc/hostapd/hostapd.conf
chmod 664 /etc/hostapd/hostapd.conf

chown root:wifi-admin /etc/dnsmasq.conf
chmod 664 /etc/dnsmasq.conf

chown root:wifi-admin /etc/dhcpcd.conf
chmod 664 /etc/dhcpcd.conf

# Set permissions for backup directory
chown -R root:wifi-admin /var/backups/wifi_helper
chmod -R 775 /var/backups/wifi_helper

# Set permissions for log directory
chown -R root:wifi-admin /var/log/wifi-helper
chmod -R 775 /var/log/wifi-helper

# Create a wrapper script for systemctl commands
echo -e "${YELLOW}Creating systemctl wrapper...${NC}"
cat > /usr/local/bin/wifi-service-control << 'EOF'
#!/bin/bash
# Wrapper script for WiFi service control
# This script is called by the Python WiFi helper

ALLOWED_SERVICES="hostapd dnsmasq dhcpcd"
ALLOWED_ACTIONS="start stop restart enable disable status is-active"

SERVICE=$1
ACTION=$2

# Validate service
if [[ ! " $ALLOWED_SERVICES " =~ " $SERVICE " ]]; then
    echo "Error: Service $SERVICE not allowed"
    exit 1
fi

# Validate action
if [[ ! " $ALLOWED_ACTIONS " =~ " $ACTION " ]]; then
    echo "Error: Action $ACTION not allowed"
    exit 1
fi

# Execute systemctl command
systemctl $ACTION $SERVICE
EOF

chmod 755 /usr/local/bin/wifi-service-control

# Create wrapper for iptables commands
echo -e "${YELLOW}Creating iptables wrapper...${NC}"
cat > /usr/local/bin/wifi-iptables-control << 'EOF'
#!/bin/bash
# Wrapper script for iptables control
# This script handles NAT configuration for the WiFi helper

ACTION=$1

case $ACTION in
    "enable-nat")
        iptables -t nat -C POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null || \
        iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
        iptables-save > /etc/iptables.ipv4.nat
        ;;
    "disable-nat")
        iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null
        iptables-save > /etc/iptables.ipv4.nat
        ;;
    "save")
        iptables-save > /etc/iptables.ipv4.nat
        ;;
    "restore")
        iptables-restore < /etc/iptables.ipv4.nat
        ;;
    *)
        echo "Error: Unknown action $ACTION"
        exit 1
        ;;
esac
EOF

chmod 755 /usr/local/bin/wifi-iptables-control

# Create wrapper for sysctl commands
echo -e "${YELLOW}Creating sysctl wrapper...${NC}"
cat > /usr/local/bin/wifi-sysctl-control << 'EOF'
#!/bin/bash
# Wrapper script for sysctl control

ACTION=$1

case $ACTION in
    "enable-forwarding")
        sysctl -w net.ipv4.ip_forward=1
        # Ensure it's persistent
        if ! grep -q "^net.ipv4.ip_forward=1" /etc/sysctl.conf; then
            echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
        fi
        ;;
    "disable-forwarding")
        sysctl -w net.ipv4.ip_forward=0
        ;;
    *)
        echo "Error: Unknown action $ACTION"
        exit 1
        ;;
esac
EOF

chmod 755 /usr/local/bin/wifi-sysctl-control

# Set up sudoers rules for the wifi-admin group
echo -e "${YELLOW}Setting up sudoers rules...${NC}"
cat > /etc/sudoers.d/wifi-helper << EOF
# Sudoers rules for WiFi Helper
# Members of wifi-admin group can run these commands without password

# Service control
%wifi-admin ALL=(root) NOPASSWD: /usr/local/bin/wifi-service-control
%wifi-admin ALL=(root) NOPASSWD: /usr/local/bin/wifi-iptables-control
%wifi-admin ALL=(root) NOPASSWD: /usr/local/bin/wifi-sysctl-control

# Direct systemctl commands (backup)
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl start hostapd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl stop hostapd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl restart hostapd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl enable hostapd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl disable hostapd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl status hostapd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl is-active hostapd

%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl start dnsmasq
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl stop dnsmasq
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl restart dnsmasq
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl enable dnsmasq
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl disable dnsmasq
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl status dnsmasq
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl is-active dnsmasq

%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl start dhcpcd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl stop dhcpcd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl restart dhcpcd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl enable dhcpcd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl disable dhcpcd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl status dhcpcd
%wifi-admin ALL=(root) NOPASSWD: /bin/systemctl is-active dhcpcd

# arp command for getting connected clients
%wifi-admin ALL=(root) NOPASSWD: /usr/sbin/arp -n
EOF

# Validate sudoers file
visudo -c -f /etc/sudoers.d/wifi-helper
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Sudoers file validation failed${NC}"
    rm /etc/sudoers.d/wifi-helper
    exit 1
fi

chmod 440 /etc/sudoers.d/wifi-helper

# Install required packages if not already installed
echo -e "${YELLOW}Checking required packages...${NC}"
PACKAGES="hostapd dnsmasq iptables-persistent"
for pkg in $PACKAGES; do
    if ! dpkg -l | grep -q "^ii  $pkg"; then
        echo -e "${YELLOW}Installing $pkg...${NC}"
        apt-get update
        apt-get install -y $pkg
    fi
done

# Stop and disable hostapd and dnsmasq by default
echo -e "${YELLOW}Configuring services...${NC}"
systemctl stop hostapd 2>/dev/null || true
systemctl stop dnsmasq 2>/dev/null || true

# Unmask hostapd if it's masked
systemctl unmask hostapd 2>/dev/null || true

# Create a marker file to indicate setup is complete
echo "$(date): Setup completed for user $TARGET_USER" > /etc/wifi-helper/setup.marker
chown root:wifi-admin /etc/wifi-helper/setup.marker
chmod 664 /etc/wifi-helper/setup.marker

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}WiFi Helper setup completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "1. User '$TARGET_USER' has been added to the 'wifi-admin' group"
echo "2. You need to logout and login again for group changes to take effect"
echo "   Or run: newgrp wifi-admin"
echo "3. The Python WiFi helper can now be run without sudo"
echo ""
echo -e "${GREEN}Setup complete!${NC}"