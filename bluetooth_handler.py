#!/usr/bin/env python3
"""
Bluetooth Handler for Navigation Assistant
Manages Bluetooth connections for audio streaming and device pairing
"""

import bluetooth
import subprocess
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BluetoothHandler:
    def __init__(self):
        self.connected_devices = []
        self.audio_device = None
        
    def scan_devices(self, duration=8):
        """Scan for nearby Bluetooth devices"""
        logger.info("Scanning for Bluetooth devices...")
        try:
            devices = bluetooth.discover_devices(
                duration=duration,
                lookup_names=True,
                flush_cache=True
            )
            logger.info(f"Found {len(devices)} devices")
            return devices
        except Exception as e:
            logger.error(f"Error scanning devices: {e}")
            return []
    
    def pair_device(self, device_address):
        """Pair with a specific Bluetooth device"""
        try:
            logger.info(f"Attempting to pair with {device_address}")
            # Use bluetoothctl for pairing on Raspberry Pi
            subprocess.run(['bluetoothctl', 'pair', device_address], check=True)
            subprocess.run(['bluetoothctl', 'trust', device_address], check=True)
            subprocess.run(['bluetoothctl', 'connect', device_address], check=True)
            logger.info(f"Successfully paired with {device_address}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pair: {e}")
            return False
    
    def connect_audio_device(self, device_address=None):
        """Connect to Bluetooth audio device (headphones/speaker)"""
        if device_address:
            self.audio_device = device_address
            return self.pair_device(device_address)
        else:
            # Auto-connect to first available audio device
            devices = self.scan_devices()
            for addr, name in devices:
                if any(keyword in name.lower() for keyword in ['headphone', 'speaker', 'earbuds', 'airpods']):
                    logger.info(f"Found audio device: {name}")
                    if self.pair_device(addr):
                        self.audio_device = addr
                        return True
            return False
    
    def disconnect_device(self, device_address):
        """Disconnect from a Bluetooth device"""
        try:
            subprocess.run(['bluetoothctl', 'disconnect', device_address], check=True)
            logger.info(f"Disconnected from {device_address}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to disconnect: {e}")
            return False
    
    def set_as_audio_output(self):
        """Set connected Bluetooth device as default audio output"""
        try:
            # Set Bluetooth as default audio sink on Raspberry Pi
            subprocess.run([
                'pactl', 'set-default-sink', 
                'bluez_sink.{}'.format(self.audio_device.replace(':', '_'))
            ], check=True)
            logger.info("Bluetooth device set as audio output")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set audio output: {e}")
            return False
    
    def get_connected_devices(self):
        """Get list of currently connected devices"""
        try:
            result = subprocess.run(
                ['bluetoothctl', 'devices', 'Connected'],
                capture_output=True,
                text=True
            )
            devices = []
            for line in result.stdout.split('\n'):
                if line.startswith('Device'):
                    parts = line.split()
                    if len(parts) >= 3:
                        addr = parts[1]
                        name = ' '.join(parts[2:])
                        devices.append((addr, name))
            return devices
        except Exception as e:
            logger.error(f"Error getting connected devices: {e}")
            return []


if __name__ == "__main__":
    # Test Bluetooth functionality
    bt = BluetoothHandler()
    print("Scanning for devices...")
    devices = bt.scan_devices()
    for addr, name in devices:
        print(f"  {name} - {addr}")

