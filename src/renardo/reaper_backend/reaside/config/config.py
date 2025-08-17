"""Configuration module for reaside."""

from configparser import ConfigParser
import json
import os
import pathlib
import random
import string
import shutil
import platform
from renardo.logger import get_logger
import urllib.request
import urllib.error
from pathlib import Path

logger = get_logger('reaside.config.config')

# Default ports
WEB_INTERFACE_PORT = 8080
OSC_SEND_PORT = 8767  # Port for sending OSC messages to REAPER
OSC_RECEIVE_PORT = 8766  # Port for receiving OSC messages from REAPER

# API Paths
REASCRIPT_PATH = os.path.join('Scripts', 'reaside')

class CaseInsensitiveDict(dict):
    """Dictionary with case-insensitive keys."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dict = dict(*args, **kwargs)
        for key, value in self._dict.items():
            if isinstance(key, str):
                self._dict[key.lower()] = value

    def __contains__(self, key):
        if isinstance(key, str):
            return key.lower() in self._dict
        return key in self._dict

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._dict[key.lower()]
        return self._dict[key]

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if isinstance(key, str):
            self._dict[key.lower()] = value


class Config(ConfigParser):
    """Parser for REAPER .ini file."""

    def __init__(self, ini_file):
        super().__init__(
            strict=False, delimiters="=", dict_type=CaseInsensitiveDict
        )
        self.optionxform = str
        self.ini_file = ini_file
        if not os.path.exists(ini_file):
            pathlib.Path(ini_file).touch()
        self.read(self.ini_file, encoding='utf8')

    def write(self):
        # Backup config state before user has ever tried reapy
        before_reapy_file = self.ini_file + '.before-new-reapy.bak'
        if not os.path.exists(before_reapy_file):
            shutil.copy(self.ini_file, before_reapy_file)
        # Backup current config
        shutil.copy(self.ini_file, self.ini_file + '.bak')
        # Write config
        with open(self.ini_file, "w", encoding='utf8') as f:
            super().write(f, False)


def get_resource_path():
    """Get REAPER resource path based on platform."""
    if platform.system() == 'Windows':
        # Try common locations on Windows
        common_paths = [
            os.path.join(os.environ.get('APPDATA', ''), 'REAPER'),
            'C:\\Program Files\\REAPER',
            'C:\\Program Files (x86)\\REAPER',
        ]
        for path in common_paths:
            if os.path.isdir(path):
                return path
    elif platform.system() == 'Darwin':
        # macOS paths
        paths = [
            os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'REAPER'),
            '/Applications/REAPER.app/Contents/Resources'
        ]
        for path in paths:
            if os.path.isdir(path):
                return path
    else:
        # Linux paths
        paths = [
            os.path.join(os.path.expanduser('~'), '.config', 'REAPER'),
            '/opt/REAPER',
            '/usr/local/share/REAPER',
        ]
        for path in paths:
            if os.path.isdir(path):
                return path

    # If we get here, REAPER resource path couldn't be found
    raise FileNotFoundError("Could not locate REAPER resource path. Please specify it manually.")


def is_web_interface_enabled(port=WEB_INTERFACE_PORT):
    """Check if REAPER's web interface is enabled and accessible."""
    url = f"http://localhost:{port}/"
    try:
        response = urllib.request.urlopen(url, timeout=1)
        return response.status == 200
    except (urllib.error.URLError, ConnectionRefusedError):
        return False


def add_osc_device(resource_path, send_port=OSC_SEND_PORT, receive_port=OSC_RECEIVE_PORT):
    """Add OSC device configuration to REAPER."""
    config = Config(os.path.join(resource_path, "reaper.ini"))
    csurf_count = int(config["reaper"].get("csurf_cnt", "0"))
    
    # Check if OSC device already exists
    for i in range(csurf_count):
        key = f"csurf_{i}"
        if key not in config["reaper"]:
            continue
        string = config["reaper"][key]
        if string.startswith("OSC"):  # It's an OSC device
            existing_config = string.split(" ")
            if len(existing_config) >= 2:
                existing_name = existing_config[1]
                # Check if this is a "renardo" OSC device
                if existing_name == "renardo":
                    if len(existing_config) >= 7:
                        existing_send = existing_config[4]
                        existing_receive = existing_config[6]
                        if existing_send == str(send_port) and existing_receive == str(receive_port):
                            logger.info(f"OSC device 'renardo' already exists with ports {send_port}/{receive_port}")
                            return
                        else:
                            # Found renardo device but with different ports, update it
                            logger.info(f"Updating existing OSC device 'renardo' ports from {existing_send}/{existing_receive} to {send_port}/{receive_port}")
                            config["reaper"][key] = f"OSC renardo 127.0.0.1 {receive_port} 127.0.0.1 {send_port} '' 1"
                            config.write()
                            return
    
    # Add new OSC device
    csurf_count += 1
    config["reaper"]["csurf_cnt"] = str(csurf_count)
    key = f"csurf_{csurf_count - 1}"
    # OSC format: "OSC [name] [local_ip] [local_port] [remote_ip] [remote_port] [pattern_config] [feedback_enable]"
    config["reaper"][key] = f"OSC renardo 127.0.0.1 {receive_port} 127.0.0.1 {send_port} '' 1"
    config.write()
    logger.info(f"Added OSC device with send port {send_port} and receive port {receive_port}")


def osc_device_exists(resource_path, send_port=OSC_SEND_PORT, receive_port=OSC_RECEIVE_PORT):
    """Check if OSC device exists in REAPER configuration."""
    config = Config(os.path.join(resource_path, "reaper.ini"))
    csurf_count = int(config["reaper"].get("csurf_cnt", "0"))
    
    for i in range(csurf_count):
        key = f"csurf_{i}"
        if key not in config["reaper"]:
            continue
        string = config["reaper"][key]
        if string.startswith("OSC"):  # It's an OSC device
            config_parts = string.split(" ")
            if len(config_parts) >= 2:
                existing_name = config_parts[1]
                # Check specifically for "renardo" OSC device
                if existing_name == "renardo":
                    if len(config_parts) >= 7:
                        existing_send = config_parts[4]
                        existing_receive = config_parts[6]
                        if existing_send == str(send_port) and existing_receive == str(receive_port):
                            return True
    return False


def clean_duplicate_osc_devices(resource_path):
    """Remove duplicate 'renardo' OSC devices, keeping only the first one."""
    config = Config(os.path.join(resource_path, "reaper.ini"))
    csurf_count = int(config["reaper"].get("csurf_cnt", "0"))
    
    renardo_devices = []
    other_devices = []
    
    # Collect all devices and identify renardo ones
    for i in range(csurf_count):
        key = f"csurf_{i}"
        if key not in config["reaper"]:
            continue
        string = config["reaper"][key]
        if string.startswith("OSC"):
            config_parts = string.split(" ")
            if len(config_parts) >= 2 and config_parts[1] == "renardo":
                renardo_devices.append((key, string))
            else:
                other_devices.append((key, string))
        else:
            other_devices.append((key, string))
    
    # If we have multiple renardo devices, clean them up
    if len(renardo_devices) > 1:
        logger.info(f"Found {len(renardo_devices)} duplicate 'renardo' OSC devices, cleaning up...")
        
        # Remove all csurf entries
        for i in range(csurf_count):
            key = f"csurf_{i}"
            if key in config["reaper"]:
                del config["reaper"][key]
        
        # Re-add other devices first
        for i, (_, device_string) in enumerate(other_devices):
            config["reaper"][f"csurf_{i}"] = device_string
        
        # Add only the first renardo device
        if renardo_devices:
            config["reaper"][f"csurf_{len(other_devices)}"] = renardo_devices[0][1]
            logger.info("Kept the first 'renardo' OSC device, removed duplicates")
        
        # Update count
        config["reaper"]["csurf_cnt"] = str(len(other_devices) + (1 if renardo_devices else 0))
        config.write()
        
        return True
    
    return False


def add_reascript_lua(resource_path, script_path):
    """Add Lua ReaScript to *Actions* list in REAPER."""
    script_path = os.path.abspath(script_path)
    if not os.path.exists(script_path):
        raise FileNotFoundError(script_path)
    if os.path.splitext(script_path)[1] != '.lua':
        raise ValueError(f'{script_path} is not a Lua script.')
    
    ini_file = os.path.join(resource_path, "reaper-kb.ini")
    if not os.path.exists(ini_file):
        pathlib.Path(ini_file).touch()
    
    # Check if ReaScript already exists
    with open(ini_file) as f:
        content = f.read()
        lines = [line for line in content.split('\n') 
                if line.startswith("SCR 4 0 ")]
    
    for line in lines:
        if line.split(" ")[-1] == script_path:
            # Extract the action code
            code = line.split(" ")[3].strip('_')
            return f'"_{code}"'
    
    # If not, add it
    code = get_new_reascript_code(ini_file)
    script_name = os.path.basename(script_path)
    new_line = 'SCR 4 0 {} "Custom: {}" {}'
    with open(ini_file, "a") as f:
        f.write(new_line.format(code, script_name, script_path))
    return f'"_{code}"'


def add_web_interface(resource_path, port=WEB_INTERFACE_PORT):
    """Add a REAPER Web Interface at a specified port."""
    if web_interface_exists(resource_path, port):
        return
    
    config = Config(os.path.join(resource_path, "reaper.ini"))
    csurf_count = int(config["reaper"].get("csurf_cnt", "0"))
    csurf_count += 1
    config["reaper"]["csurf_cnt"] = str(csurf_count)
    key = f"csurf_{csurf_count - 1}"
    config["reaper"][key] = f"HTTP 0 {port} '' 'index.html' 0 ''"
    config.write()


def get_new_reascript_code(ini_file):
    """Return new ReaScript code for reaper-kb.ini."""
    def get_random_code():
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(40))
    
    with open(ini_file) as f:
        content = f.read()
    
    code = get_random_code()
    while code in content:
        code = get_random_code()
    
    return "RS" + code


def set_ext_state(section, key, value, resource_path):
    """Update REAPER external state."""
    config = Config(os.path.join(resource_path, 'reaper-extstate.ini'))
    if section not in config.sections():
        config.add_section(section)
    config[section][key] = value
    config.write()


def web_interface_exists(resource_path, port=WEB_INTERFACE_PORT):
    """Return whether a REAPER Web Interface exists at a given port."""
    config = Config(os.path.join(resource_path, "reaper.ini"))
    csurf_count = int(config["reaper"].get("csurf_cnt", "0"))
    for i in range(csurf_count):
        key = f"csurf_{i}"
        if key not in config["reaper"]:
            continue
        string = config["reaper"][key]
        if string.startswith("HTTP"):  # It's a web interface
            if string.split(" ")[2] == str(port):  # It's the one
                return True
    return False


def configure_lua_reascript(resource_path=None, install_path=None):
    """Configure REAPER for reaside using Lua ReaScript."""
    if not resource_path:
        resource_path = get_resource_path()
    
    if not os.path.isdir(resource_path):
        raise FileNotFoundError(f"REAPER resource path does not exist: {resource_path}")
    
    # Get path to reaside ReaScripts
    if not install_path:
        install_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reascripts')
    
    # Make sure ReaScripts directory exists
    scripts_dir = os.path.join(resource_path, 'Scripts')
    reaside_dir = os.path.join(scripts_dir, 'reaside')
    
    os.makedirs(reaside_dir, exist_ok=True)
    
    # Install Lua script
    lua_script = 'reaside_server.lua'
    
    logger.info("Installing reaside Lua script to REAPER...")
    
    src_path = os.path.join(install_path, lua_script)
    dst_path = os.path.join(reaside_dir, lua_script)
    
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"Could not find script: {src_path}")
    
    shutil.copy2(src_path, dst_path)
    logger.info(f"Installed {lua_script} to {dst_path}")
    
    # Add web interface if needed
    logger.info("Setting up REAPER web interface...")
    add_web_interface(resource_path, WEB_INTERFACE_PORT)
    
    # Clean up any duplicate OSC devices first
    logger.info("Checking for duplicate OSC devices...")
    clean_duplicate_osc_devices(resource_path)
    
    # Add OSC device if needed
    logger.info("Setting up REAPER OSC device...")
    add_osc_device(resource_path, OSC_SEND_PORT, OSC_RECEIVE_PORT)
    
    # Add Lua script to REAPER actions
    logger.info("Adding Lua script to REAPER's action list...")
    
    # Add the combined reaside_server.lua script
    api_script_path = os.path.join(reaside_dir, lua_script)
    api_action = add_reascript_lua(resource_path, api_script_path)
    set_ext_state("reaside", "activate_reaside_server", api_action, resource_path)
    set_ext_state("reaside", "api_action_id", api_action, resource_path)
    logger.info(f"Added {lua_script} to actions with ID: {api_action}")
    
    # Store additional configuration for automatic startup
    set_ext_state("reaside", "script_installed", "true", resource_path)
    set_ext_state("reaside", "config_version", "1.0", resource_path)
    set_ext_state("reaside", "osc_send_port", str(OSC_SEND_PORT), resource_path)
    set_ext_state("reaside", "osc_receive_port", str(OSC_RECEIVE_PORT), resource_path)
    
    # Check if web interface is enabled
    if not is_web_interface_enabled():
        logger.warning("REAPER web interface doesn't seem to be enabled.")
        logger.warning("Please enable it in REAPER: Preferences > Control/OSC/web")
    
    logger.info("Configuration complete!")
    logger.info("Please restart REAPER and make sure both web interface and OSC are enabled in:")
    logger.info("Preferences > Control/OSC/web")
    logger.info(f"OSC device configured for ports {OSC_SEND_PORT} (send) and {OSC_RECEIVE_PORT} (receive)")
    logger.info("After restarting REAPER, run the reaside_server.lua script from the Actions menu once")
    
    return True


def check_reaper_configuration():
    """Check if REAPER is properly configured for reaside."""
    # Check if web interface is enabled
    if not is_web_interface_enabled():
        return False
    
    # Check if ReaScripts are installed
    try:
        resource_path = get_resource_path()
        reaside_dir = os.path.join(resource_path, 'Scripts', 'reaside')
        
        if not os.path.isdir(reaside_dir):
            return False
        
        # Check for the essential script
        if not os.path.isfile(os.path.join(reaside_dir, 'reaside_server.lua')):
            return False
        
        return True
    except FileNotFoundError:
        return False