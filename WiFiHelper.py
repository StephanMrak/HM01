#!/usr/bin/env python3
"""
WiFi Helper Class for Raspberry Pi Zero 2 W
Manages WiFi hotspot creation and configuration
"""

import os
import subprocess
import socket
import time
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging
import re

class WiFiHelper:
    """Helper class for managing WiFi hotspot on Raspberry Pi Zero 2 W"""
    
    def __init__(self, log_level=logging.INFO):
        """Initialize WiFi Helper
        
        Args:
            log_level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Configuration file paths
        self.hostapd_conf = Path("/etc/hostapd/hostapd.conf")
        self.dhcpcd_conf = Path("/etc/dhcpcd.conf")
        self.dnsmasq_conf = Path("/etc/dnsmasq.conf")
        self.sysctl_conf = Path("/etc/sysctl.conf")
        self.wpa_supplicant_conf = Path("/etc/wpa_supplicant/wpa_supplicant.conf")
        
        # Backup directory for config files
        self.backup_dir = Path("/var/backups/wifi_helper")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _backup_file(self, file_path: Path) -> Optional[Path]:
        """Create a backup of a configuration file
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to the backup file or None if backup failed
        """
        if not file_path.exists():
            return None
            
        backup_path = self.backup_dir / f"{file_path.name}.{int(time.time())}.bak"
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Backed up {file_path} to {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to backup {file_path}: {e}")
            return None
    
    def _restore_file(self, backup_path: Path, original_path: Path) -> bool:
        """Restore a configuration file from backup
        
        Args:
            backup_path: Path to the backup file
            original_path: Path where the file should be restored
            
        Returns:
            True if restoration was successful, False otherwise
        """
        try:
            shutil.copy2(backup_path, original_path)
            self.logger.info(f"Restored {original_path} from {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore {original_path}: {e}")
            return False
    
    def _file_contains_config(self, file_path: Path, config_lines: List[str]) -> bool:
        """Check if a file already contains specific configuration lines
        
        Args:
            file_path: Path to the configuration file
            config_lines: List of configuration lines to check
            
        Returns:
            True if all config lines are present, False otherwise
        """
        if not file_path.exists():
            return False
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check if all config lines are present
            for line in config_lines:
                if line.strip() and line.strip() not in content:
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return False
    
    def _write_config_safely(self, file_path: Path, content: str, append: bool = False) -> bool:
        """Safely write configuration to a file with backup
        
        Args:
            file_path: Path to the configuration file
            content: Content to write
            append: Whether to append or overwrite
            
        Returns:
            True if write was successful, False otherwise
        """
        # Create backup first
        backup_path = None
        if file_path.exists():
            backup_path = self._backup_file(file_path)
        
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(file_path, mode) as f:
                f.write(content)
            
            self.logger.info(f"Successfully wrote configuration to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write to {file_path}: {e}")
            
            # Attempt to restore from backup
            if backup_path and backup_path.exists():
                self._restore_file(backup_path, file_path)
            
            return False
    
    def _run_command(self, cmd: List[str], check: bool = True, use_sudo: bool = False) -> Tuple[bool, str, str]:
        """Run a system command safely
        
        Args:
            cmd: Command and arguments as list
            check: Whether to check return code
            use_sudo: Whether to prepend sudo to the command
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        # Check if setup has been completed
        if use_sudo and not self._check_setup_complete():
            self.logger.warning("Setup not complete. Run setup_wifi_helper.sh first!")
        
        # Prepend sudo if needed
        if use_sudo and cmd[0] != "sudo":
            cmd = ["sudo"] + cmd
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout if e.stdout else "", e.stderr if e.stderr else str(e)
        except Exception as e:
            return False, "", str(e)
    
    def _check_setup_complete(self) -> bool:
        """Check if the setup script has been run
        
        Returns:
            True if setup is complete, False otherwise
        """
        setup_marker = Path("/etc/wifi-helper/setup.marker")
        return setup_marker.exists()
    
    def check_internet_connection(self, host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
        """Check if there is an active internet connection
        
        Args:
            host: Host to check connectivity (default: Google DNS)
            port: Port to check (default: 53 for DNS)
            timeout: Connection timeout in seconds
            
        Returns:
            True if internet connection is available, False otherwise
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            self.logger.debug("Internet connection available")
            return True
        except Exception as e:
            self.logger.debug(f"No internet connection: {e}")
            return False
    
    def _configure_hostapd(self, ssid: str, password: str, country: str, 
                          channel: int = 7, hw_mode: str = 'g') -> bool:
        """Configure hostapd for access point
        
        Args:
            ssid: Network name
            password: Network password (min 8 characters)
            country: Country code (e.g., 'US', 'GB', 'DE')
            channel: WiFi channel (default: 7)
            hw_mode: Hardware mode (default: 'g' for 2.4GHz)
            
        Returns:
            True if configuration was successful
        """
        if len(password) < 8:
            self.logger.error("Password must be at least 8 characters long")
            return False
        
        hostapd_config = f"""# Hostapd configuration for Raspberry Pi Zero 2 W
interface=wlan0
driver=nl80211
ssid={ssid}
hw_mode={hw_mode}
channel={channel}
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={password}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
country_code={country.upper()}
ieee80211d=1
ieee80211h=0
"""
        
        # Check if configuration already exists
        config_lines = hostapd_config.strip().split('\n')
        if self._file_contains_config(self.hostapd_conf, config_lines):
            self.logger.info("Hostapd configuration already exists")
            return True
        
        return self._write_config_safely(self.hostapd_conf, hostapd_config)
    
    def _configure_dhcpcd(self) -> bool:
        """Configure dhcpcd for static IP on wlan0
        
        Returns:
            True if configuration was successful
        """
        dhcpcd_config = """
# Static IP configuration for wlan0 (Access Point)
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
"""
        
        # Check if configuration already exists
        if self._file_contains_config(self.dhcpcd_conf, ["static ip_address=192.168.4.1/24"]):
            self.logger.info("DHCPCD configuration already exists")
            return True
        
        return self._write_config_safely(self.dhcpcd_conf, dhcpcd_config, append=True)
    
    def _configure_dnsmasq(self) -> bool:
        """Configure dnsmasq for DHCP and DNS
        
        Returns:
            True if configuration was successful
        """
        dnsmasq_config = """# Dnsmasq configuration for Raspberry Pi Access Point
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/gw.wlan/192.168.4.1
"""
        
        # Check if configuration already exists
        config_lines = dnsmasq_config.strip().split('\n')
        if self._file_contains_config(self.dnsmasq_conf, ["dhcp-range=192.168.4.2,192.168.4.20"]):
            self.logger.info("Dnsmasq configuration already exists")
            return True
        
        return self._write_config_safely(self.dnsmasq_conf, dnsmasq_config, append=True)
    
    def _configure_ip_forwarding(self) -> bool:
        """Enable IP forwarding for NAT
        
        Returns:
            True if configuration was successful
        """
        # Use the wrapper script if available, otherwise fall back to direct command
        wrapper_script = Path("/usr/local/bin/wifi-sysctl-control")
        if wrapper_script.exists():
            success, _, _ = self._run_command(["sudo", "wifi-sysctl-control", "enable-forwarding"])
        else:
            # Fallback to direct command
            ip_forward_config = "net.ipv4.ip_forward=1"
            
            # Check if already configured
            if self._file_contains_config(self.sysctl_conf, [ip_forward_config]):
                self.logger.info("IP forwarding already enabled")
            else:
                if not self._write_config_safely(self.sysctl_conf, f"\n{ip_forward_config}\n", append=True):
                    return False
            
            # Apply the setting immediately
            success, _, _ = self._run_command(["sudo", "sysctl", "-w", ip_forward_config])
        
        return success
    
    def _configure_iptables_nat(self) -> bool:
        """Configure iptables for NAT
        
        Returns:
            True if configuration was successful
        """
        # Use the wrapper script if available
        wrapper_script = Path("/usr/local/bin/wifi-iptables-control")
        if wrapper_script.exists():
            success, _, _ = self._run_command(["sudo", "wifi-iptables-control", "enable-nat"])
        else:
            # Fallback to direct commands
            # Add NAT rule
            success, _, _ = self._run_command([
                "sudo", "iptables", "-t", "nat", "-A", "POSTROUTING",
                "-o", "eth0", "-j", "MASQUERADE"
            ])
            
            if not success:
                self.logger.error("Failed to add NAT rule")
                return False
            
            # Save iptables rules
            success, _, _ = self._run_command(["sudo", "sh", "-c", "iptables-save > /etc/iptables.ipv4.nat"])
            
            if not success:
                self.logger.error("Failed to save iptables rules")
                return False
        
        # Add rule to restore on boot in rc.local
        rc_local = Path("/etc/rc.local")
        restore_rule = "iptables-restore < /etc/iptables.ipv4.nat"
        
        if rc_local.exists() and not self._file_contains_config(rc_local, [restore_rule]):
            try:
                with open(rc_local, 'r') as f:
                    lines = f.readlines()
                
                # Insert before 'exit 0'
                for i, line in enumerate(lines):
                    if 'exit 0' in line:
                        lines.insert(i, f"{restore_rule}\n")
                        break
                
                self._write_config_safely(rc_local, ''.join(lines))
            except Exception as e:
                self.logger.error(f"Failed to update rc.local: {e}")
                return False
        
        return success
    
    def create_hotspot(self, ssid: str, password: str, country: str, 
                      channel: int = 7, enable_nat: bool = True) -> bool:
        """Create and configure a WiFi hotspot
        
        Args:
            ssid: Network name
            password: Network password (min 8 characters)
            country: Country code (e.g., 'US', 'GB', 'DE')
            channel: WiFi channel (default: 7)
            enable_nat: Enable NAT for internet sharing (default: True)
            
        Returns:
            True if hotspot was created successfully
        """
        self.logger.info(f"Creating hotspot: SSID={ssid}, Country={country}")
        
        # Validate country code
        if len(country) != 2:
            self.logger.error("Country code must be 2 characters (e.g., 'US', 'GB', 'DE')")
            return False
        
        # Configure hostapd
        if not self._configure_hostapd(ssid, password, country, channel):
            self.logger.error("Failed to configure hostapd")
            return False
        
        # Configure dhcpcd
        if not self._configure_dhcpcd():
            self.logger.error("Failed to configure dhcpcd")
            return False
        
        # Configure dnsmasq
        if not self._configure_dnsmasq():
            self.logger.error("Failed to configure dnsmasq")
            return False
        
        # Configure IP forwarding and NAT if requested
        if enable_nat:
            if not self._configure_ip_forwarding():
                self.logger.error("Failed to configure IP forwarding")
                return False
            
            if not self._configure_iptables_nat():
                self.logger.error("Failed to configure NAT")
                return False
        
        # Restart services
        services = ["dhcpcd", "dnsmasq", "hostapd"]
        for service in services:
            self.logger.info(f"Restarting {service} service...")
            # Use wrapper script if available
            wrapper_script = Path("/usr/local/bin/wifi-service-control")
            if wrapper_script.exists():
                success, _, err = self._run_command(["sudo", "wifi-service-control", service, "restart"])
            else:
                success, _, err = self._run_command(["sudo", "systemctl", "restart", service])
            
            if not success:
                self.logger.error(f"Failed to restart {service}: {err}")
                return False
            
            # Enable service to start on boot
            if wrapper_script.exists():
                success, _, _ = self._run_command(["sudo", "wifi-service-control", service, "enable"])
            else:
                success, _, _ = self._run_command(["sudo", "systemctl", "enable", service])
            
            if not success:
                self.logger.warning(f"Failed to enable {service} on boot")
        
        self.logger.info("Hotspot created successfully!")
        return True
    
    def stop_hotspot(self) -> bool:
        """Stop the WiFi hotspot
        
        Returns:
            True if hotspot was stopped successfully
        """
        self.logger.info("Stopping hotspot...")
        
        services = ["hostapd", "dnsmasq"]
        wrapper_script = Path("/usr/local/bin/wifi-service-control")
        
        for service in services:
            if wrapper_script.exists():
                success, _, err = self._run_command(["sudo", "wifi-service-control", service, "stop"])
            else:
                success, _, err = self._run_command(["sudo", "systemctl", "stop", service])
            
            if not success:
                self.logger.error(f"Failed to stop {service}: {err}")
                return False
        
        self.logger.info("Hotspot stopped successfully")
        return True
    
    def start_hotspot(self) -> bool:
        """Start the WiFi hotspot (assumes it's already configured)
        
        Returns:
            True if hotspot was started successfully
        """
        self.logger.info("Starting hotspot...")
        
        services = ["dhcpcd", "dnsmasq", "hostapd"]
        wrapper_script = Path("/usr/local/bin/wifi-service-control")
        
        for service in services:
            if wrapper_script.exists():
                success, _, err = self._run_command(["sudo", "wifi-service-control", service, "start"])
            else:
                success, _, err = self._run_command(["sudo", "systemctl", "start", service])
            
            if not success:
                self.logger.error(f"Failed to start {service}: {err}")
                return False
        
        self.logger.info("Hotspot started successfully")
        return True
    
    def get_hotspot_status(self) -> Dict[str, bool]:
        """Get the status of hotspot services
        
        Returns:
            Dictionary with service names as keys and running status as values
        """
        services = ["hostapd", "dnsmasq", "dhcpcd"]
        status = {}
        
        for service in services:
            success, stdout, _ = self._run_command(
                ["systemctl", "is-active", service],
                check=False
            )
            status[service] = stdout.strip() == "active"
        
        return status
    
    def get_connected_clients(self) -> List[Dict[str, str]]:
        """Get list of connected clients to the hotspot
        
        Returns:
            List of dictionaries containing client information
        """
        clients = []
        
        # Check ARP table for connected devices
        # Use sudo for arp command if needed
        success, stdout, _ = self._run_command(["sudo", "arp", "-n"])
        if success:
            lines = stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split()
                if len(parts) >= 3 and "192.168.4" in parts[0]:
                    clients.append({
                        "ip": parts[0],
                        "mac": parts[2] if parts[2] != "<incomplete>" else "Unknown",
                        "interface": parts[-1]
                    })
        
        return clients
    
    def scan_for_ssids(self) -> List[Dict[str, str]]:
        """Scan for available WiFi networks (works even in hotspot mode)
        
        Returns:
            List of dictionaries with SSID info: {'ssid': str, 'signal': int, 'encrypted': bool}
        """
        self.logger.info("Scanning for WiFi networks...")
        networks = []
        
        # Use iw for scanning (works better in AP mode than iwlist)
        # First try with iw (more reliable in AP mode)
        success, stdout, stderr = self._run_command(["sudo", "iw", "dev", "wlan0", "scan", "ap-force"])
        
        if not success:
            # Fallback to iwlist
            self.logger.debug("iw scan failed, trying iwlist...")
            success, stdout, stderr = self._run_command(["sudo", "iwlist", "wlan0", "scan"])
        
        if not success:
            self.logger.error(f"Failed to scan networks: {stderr}")
            return networks
        
        # Parse scan results
        current_network = {}
        for line in stdout.split('\n'):
            line = line.strip()
            
            # For iw output
            if 'BSS' in line and '(' in line:
                # Save previous network if exists
                if current_network.get('ssid'):
                    networks.append(current_network)
                current_network = {'ssid': '', 'signal': -100, 'encrypted': False}
            
            # SSID (iw format)
            if 'SSID:' in line:
                ssid = line.split('SSID:')[1].strip()
                if ssid and ssid != '\\x00':  # Ignore hidden networks
                    current_network['ssid'] = ssid
            
            # Signal strength (iw format)
            if 'signal:' in line and 'dBm' in line:
                try:
                    signal = int(float(line.split('signal:')[1].split('dBm')[0].strip()))
                    current_network['signal'] = signal
                except:
                    pass
            
            # Encryption (iw format)
            if 'WPA' in line or 'RSN' in line:
                current_network['encrypted'] = True
            
            # For iwlist output
            if 'Cell' in line and 'Address' in line:
                if current_network.get('ssid'):
                    networks.append(current_network)
                current_network = {'ssid': '', 'signal': -100, 'encrypted': False}
            
            # SSID (iwlist format)
            if 'ESSID:' in line:
                ssid = line.split('ESSID:')[1].strip('"')
                if ssid and ssid != '':
                    current_network['ssid'] = ssid
            
            # Signal strength (iwlist format)
            if 'Quality=' in line:
                try:
                    # Parse quality (e.g., "Quality=70/70")
                    quality_str = line.split('Quality=')[1].split()[0]
                    if '/' in quality_str:
                        current, maximum = quality_str.split('/')
                        signal_percent = int((float(current) / float(maximum)) * 100)
                        # Convert to approximate dBm
                        current_network['signal'] = -100 + signal_percent
                except:
                    pass
                
                # Also try to get Signal level if present
                if 'Signal level=' in line:
                    try:
                        signal = int(line.split('Signal level=')[1].split('dBm')[0].strip())
                        current_network['signal'] = signal
                    except:
                        pass
            
            # Encryption (iwlist format)
            if 'Encryption key:on' in line:
                current_network['encrypted'] = True
        
        # Add last network
        if current_network.get('ssid'):
            networks.append(current_network)
        
        # Remove duplicates and sort by signal strength
        seen_ssids = set()
        unique_networks = []
        for net in sorted(networks, key=lambda x: x['signal'], reverse=True):
            if net['ssid'] not in seen_ssids:
                seen_ssids.add(net['ssid'])
                unique_networks.append(net)
        
        self.logger.info(f"Found {len(unique_networks)} networks")
        return unique_networks
    
    def connect_to_network(self, ssid: str, password: Optional[str] = None, 
                          timeout: int = 30) -> bool:
        """Connect to a WiFi network (switches from hotspot to client mode)
        
        Args:
            ssid: Network SSID to connect to
            password: Network password (None for open networks)
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        self.logger.info(f"Attempting to connect to network: {ssid}")
        
        # First, stop the hotspot if it's running
        self.logger.info("Stopping hotspot services...")
        self.stop_hotspot()
        
        # Give services time to stop
        time.sleep(2)
        
        # Update wpa_supplicant configuration
        wpa_conf = self.wpa_supplicant_conf
        
        # Backup current wpa_supplicant.conf
        backup_path = self._backup_file(wpa_conf)
        
        try:
            # Read current configuration
            if wpa_conf.exists():
                with open(wpa_conf, 'r') as f:
                    content = f.read()
            else:
                # Create basic configuration
                content = """ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

"""
            
            # Check if network already configured
            if f'ssid="{ssid}"' not in content:
                # Add new network configuration
                self.logger.info("Adding network to wpa_supplicant configuration...")
                
                if password:
                    # For WPA/WPA2 networks
                    network_config = f"""
network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
"""
                else:
                    # For open networks
                    network_config = f"""
network={{
    ssid="{ssid}"
    key_mgmt=NONE
}}
"""
                
                content += network_config
                
                # Write updated configuration
                with open(wpa_conf, 'w') as f:
                    f.write(content)
                
                self.logger.info("Network configuration added")
            
            # Remove static IP configuration from dhcpcd if present
            self._remove_static_ip_config()
            
            # Restart networking services
            self.logger.info("Restarting network services...")
            
            # Enable and restart wpa_supplicant
            self._run_command(["sudo", "systemctl", "enable", "wpa_supplicant"])
            self._run_command(["sudo", "systemctl", "restart", "wpa_supplicant"])
            
            # Restart dhcpcd for DHCP
            self._run_command(["sudo", "systemctl", "restart", "dhcpcd"])
            
            # Force reconnection
            time.sleep(2)
            self._run_command(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"])
            
            # Wait for connection
            self.logger.info(f"Waiting for connection (timeout: {timeout}s)...")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check if connected
                success, stdout, _ = self._run_command(["iwgetid", "-r"])
                if success and stdout.strip() == ssid:
                    # Check for IP address
                    success, stdout, _ = self._run_command(["ip", "addr", "show", "wlan0"])
                    if success and "inet " in stdout:
                        # Check for valid IP (not link-local)
                        import re
                        ips = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', stdout)
                        for ip in ips:
                            if not ip.startswith("169.254."):
                                self.logger.info(f"Successfully connected to {ssid}")
                                self.logger.info(f"IP address: {ip}")
                                return True
                
                time.sleep(1)
            
            self.logger.error(f"Connection timeout - failed to connect to {ssid}")
            
            # If connection failed, restore backup
            if backup_path:
                self._restore_file(backup_path, wpa_conf)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error connecting to network: {e}")
            
            # Restore backup on error
            if backup_path:
                self._restore_file(backup_path, wpa_conf)
            
            return False
    
    def _remove_static_ip_config(self) -> bool:
        """Remove static IP configuration from dhcpcd.conf
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.dhcpcd_conf.exists():
                return True
            
            with open(self.dhcpcd_conf, 'r') as f:
                lines = f.readlines()
            
            # Remove hotspot static IP configuration
            new_lines = []
            skip_section = False
            
            for line in lines:
                if "# Static IP configuration for wlan0 (Access Point)" in line:
                    skip_section = True
                    continue
                elif skip_section:
                    if line.strip() == "" or (not line.startswith(" ") and not line.startswith("\t")):
                        skip_section = False
                    else:
                        continue
                
                if not skip_section:
                    new_lines.append(line)
            
            with open(self.dhcpcd_conf, 'w') as f:
                f.writelines(new_lines)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove static IP config: {e}")
            return False
    
    def get_current_mode(self) -> str:
        """Get current WiFi mode
        
        Returns:
            'hotspot', 'client', or 'unknown'
        """
        # Check if hostapd is running
        status = self.get_hotspot_status()
        if status.get("hostapd", False) and status.get("dnsmasq", False):
            return "hotspot"
        
        # Check if connected to a network
        success, stdout, _ = self._run_command(["iwgetid", "-r"])
        if success and stdout.strip():
            return "client"
        
        return "unknown"
    
    def get_current_ssid(self) -> Optional[str]:
        """Get currently connected SSID (in client mode)
        
        Returns:
            SSID string or None if not connected
        """
        success, stdout, _ = self._run_command(["iwgetid", "-r"])
        if success and stdout.strip():
            return stdout.strip()
        return None

    def get_current_network_credentials(self) -> Optional[Dict[str, str]]:
        """Get SSID, password, and encryption type for the current WiFi connection.
        Returns:
            Dict with keys: 'ssid', 'password', 'encryption' or None if not found.
        """
        ssid = self.get_current_ssid()
        if not ssid:
            return None
        
        creds = {"ssid": ssid, "password": None, "encryption": "nopass"}
        
        try:
            # Read wpa_supplicant.conf to find password and encryption
            if self.wpa_supplicant_conf.exists():
                with open(self.wpa_supplicant_conf, 'r') as f:
                    content = f.read()
                
                # Find the block for this SSID
                pattern = re.compile(r'network=\{([^}]*ssid="'+re.escape(ssid)+r'"[^}]*)\}', re.MULTILINE)
                match = pattern.search(content)
                if match:
                    block = match.group(1)
                    
                    # Password
                    psk_match = re.search(r'psk="([^"]+)"', block)
                    if psk_match:
                        creds["password"] = psk_match.group(1)
                        creds["encryption"] = "WPA"
                    
                    # Open network
                    elif re.search(r'key_mgmt=NONE', block):
                        creds["encryption"] = "nopass"
        
            return creds
        except Exception as e:
            self.logger.error(f"Error getting network credentials: {e}")
            return None

    def make_wifi_qr_string(self, ssid: str, password: Optional[str], encryption: str) -> str:
        """
        Create a Wi-Fi QR code string compatible with Android/iOS.
        """
        return f"WIFI:T:{encryption};S:{ssid};P:{password or ''};;"
