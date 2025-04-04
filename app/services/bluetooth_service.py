"""
Bluetooth service implementation for Signal Catcher app.
Handles Bluetooth device discovery, recording, and transmission.
"""
import time
import uuid
from kivy.utils import platform
from app.models.signal_model import SignalModel
from app.services.storage_service import StorageService

class BluetoothService:
    """
    Service for Bluetooth operations.
    Handles device scanning, signal recording, and transmission.
    """
    def __init__(self):
        """Initialize the Bluetooth service."""
        self.initialized = False
        self.available = False
        self.adapter = None
        self.storage_service = StorageService()
        
    def initialize(self):
        """Initialize the Bluetooth adapter and check availability."""
        if self.initialized:
            return
            
        try:
            if platform == 'android':
                self._initialize_android_bluetooth()
            else:
                self._initialize_generic_bluetooth()
                
            self.initialized = True
            
        except Exception as e:
            print(f"Bluetooth initialization error: {str(e)}")
            self.available = False
            
    def _initialize_android_bluetooth(self):
        """Initialize Bluetooth on Android."""
        from jnius import autoclass
        
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.adapter = BluetoothAdapter.getDefaultAdapter()
        
        if self.adapter and self.adapter.isEnabled():
            self.available = True
        else:
            self.available = False
            
    def _initialize_generic_bluetooth(self):
        """Initialize Bluetooth on non-Android platforms."""
        try:
            import bluetooth
            self.adapter = True  # Just a flag for availability
            self.available = True
        except ImportError:
            print("PyBluez not available on this platform")
            self.adapter = None
            self.available = False
            
    def is_initialized(self):
        """
        Check if the service is initialized.
        
        Returns:
            Boolean indicating if the service is initialized
        """
        return self.initialized
        
    def is_available(self):
        """
        Check if Bluetooth is available.
        
        Returns:
            Boolean indicating if Bluetooth is available
        """
        return self.available
        
    def scan_devices(self, duration=10):
        """
        Scan for Bluetooth devices.
        
        Args:
            duration: Scan duration in seconds
            
        Returns:
            List of dictionaries containing device information
        """
        if not self.available:
            return []
            
        devices = []
        
        try:
            if platform == 'android':
                devices = self._scan_android_devices(duration)
            else:
                devices = self._scan_generic_devices(duration)
                
        except Exception as e:
            print(f"Bluetooth scan error: {str(e)}")
            
        return devices
        
    def _scan_android_devices(self, duration):
        """
        Scan for Bluetooth devices on Android.
        
        Args:
            duration: Scan duration in seconds
            
        Returns:
            List of dictionaries containing device information
        """
        from jnius import autoclass
        import time
        
        BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        
        # Start discovery
        self.adapter.startDiscovery()
        
        # Wait for specified duration
        time.sleep(duration)
        
        # Get discovered devices
        paired_devices = self.adapter.getBondedDevices().toArray()
        
        # Stop discovery
        self.adapter.cancelDiscovery()
        
        # Convert to device list
        devices = []
        for device in paired_devices:
            devices.append({
                'name': device.getName() or "Unknown Device",
                'address': device.getAddress(),
                'type': 'bluetooth',
                'rssi': 0,  # RSSI not directly available
                'bonded': True
            })
            
        return devices
        
    def _scan_generic_devices(self, duration):
        """
        Scan for Bluetooth devices on non-Android platforms.
        
        Args:
            duration: Scan duration in seconds
            
        Returns:
            List of dictionaries containing device information
        """
        import bluetooth
        
        # Discover nearby devices
        nearby_devices = bluetooth.discover_devices(
            duration=duration,
            lookup_names=True,
            lookup_class=False,
            device_id=-1,
            scan_type='bredr'
        )
        
        # Convert to device list
        devices = []
        for addr, name in nearby_devices:
            devices.append({
                'name': name or "Unknown Device",
                'address': addr,
                'type': 'bluetooth',
                'rssi': 0,  # RSSI not directly available
                'bonded': False
            })
            
        return devices
        
    def record_device(self, device_info):
        """
        Record a Bluetooth device signal.
        
        Args:
            device_info: Dictionary containing device information
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.available:
            return False
            
        try:
            # Create a signal model
            device_data = {
                'protocol': 'bluetooth',
                'device_class': device_info.get('device_class', 'unknown'),
                'services': [],  # Would require further scanning for services
                'metadata': {
                    'scan_time': time.time(),
                    'platform': platform
                }
            }
            
            signal = SignalModel(
                signal_type='bluetooth',
                data=device_data,
                name=device_info.get('name', 'Unknown Device'),
                device_name=device_info.get('name', 'Unknown Device'),
                address=device_info.get('address', ''),
                rssi=device_info.get('rssi', 0)
            )
            
            # Save to storage
            return self.storage_service.save_record(signal.to_dict())
            
        except Exception as e:
            print(f"Error recording Bluetooth device: {str(e)}")
            return False
            
    def transmit_signal(self, signal_data):
        """
        Transmit a Bluetooth signal (simulated).
        
        Args:
            signal_data: Dictionary containing signal data
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.available:
            return False
            
        try:
            # In a real implementation, this would attempt to connect to
            # the device and perform some action. Here we'll simulate success.
            print(f"Simulating transmission to Bluetooth device: {signal_data.get('address')}")
            
            # Connect to the device
            if platform == 'android':
                # Android Bluetooth connection would be implemented here
                # This would typically use BluetoothSocket
                pass
            else:
                # Generic Bluetooth connection
                pass
                
            # For demo purposes, we'll just return success
            # In a real app, this would actually send commands to the device
            return True
            
        except Exception as e:
            print(f"Error transmitting Bluetooth signal: {str(e)}")
            return False
