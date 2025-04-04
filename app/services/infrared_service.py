"""
Infrared service implementation for Signal Catcher app.
Handles infrared signal detection, recording, and transmission.
"""
import time
import random
import uuid
import threading
from kivy.utils import platform
from kivy.clock import Clock

from app.models.signal_model import SignalModel
from app.services.storage_service import StorageService

class InfraredService:
    """
    Service for infrared operations.
    Handles signal detection, recording, and transmission.
    """
    def __init__(self):
        """Initialize the infrared service."""
        self.initialized = False
        self.available = False
        self.consumer_ir = None
        self.listening = False
        self.listen_thread = None
        self.storage_service = StorageService()
        
    def initialize(self):
        """Initialize the infrared sensor and check availability."""
        if self.initialized:
            return
            
        try:
            if platform == 'android':
                self._initialize_android_ir()
            else:
                self._initialize_generic_ir()
                
            self.initialized = True
            
        except Exception as e:
            print(f"Infrared initialization error: {str(e)}")
            self.available = False
            
    def _initialize_android_ir(self):
        """Initialize infrared on Android."""
        try:
            from jnius import autoclass
            from android.activity import mActivity
            
            Context = autoclass('android.content.Context')
            PackageManager = autoclass('android.content.pm.PackageManager')
            ConsumerIrManager = autoclass('android.hardware.ConsumerIrManager')
            
            # Check if device has IR blaster
            has_ir_feature = mActivity.getPackageManager().hasSystemFeature(
                PackageManager.FEATURE_CONSUMER_IR)
                
            if has_ir_feature:
                # Get IR service
                self.consumer_ir = mActivity.getSystemService(Context.CONSUMER_IR_SERVICE)
                self.available = True
            else:
                self.available = False
                
        except Exception as e:
            print(f"Android IR initialization error: {str(e)}")
            self.available = False
            
    def _initialize_generic_ir(self):
        """Initialize infrared on non-Android platforms (simulation)."""
        # For non-Android platforms, we'll simulate IR functionality
        self.consumer_ir = "Simulated IR"
        self.available = True
        
    def is_initialized(self):
        """
        Check if the service is initialized.
        
        Returns:
            Boolean indicating if the service is initialized
        """
        return self.initialized
        
    def is_available(self):
        """
        Check if infrared is available.
        
        Returns:
            Boolean indicating if infrared is available
        """
        return self.available
        
    def start_listening(self, callback):
        """
        Start listening for infrared signals.
        
        Args:
            callback: Function to call when a signal is detected
            
        Returns:
            Boolean indicating if listening started successfully
        """
        if not self.available or self.listening:
            return False
            
        self.listening = True
        self.listen_callback = callback
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self._listen_process)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        return True
        
    def stop_listening(self):
        """
        Stop listening for infrared signals.
        
        Returns:
            Boolean indicating if listening stopped successfully
        """
        if not self.listening:
            return False
            
        self.listening = False
        return True
        
    def _listen_process(self):
        """Background process for infrared listening."""
        try:
            # In a real implementation, this would connect to the IR receiver
            # and wait for signals. Here we'll simulate random signal detection.
            
            while self.listening:
                # Simulate random signal detection (every 2-5 seconds)
                time.sleep(random.uniform(2, 5))
                
                if not self.listening:
                    break
                    
                # Generate simulated signal
                signal = self._generate_simulated_signal()
                
                # Call the callback with the detected signal
                if self.listen_callback:
                    self.listen_callback(signal)
                    
        except Exception as e:
            print(f"IR listening error: {str(e)}")
            self.listening = False
            
    def _generate_simulated_signal(self):
        """
        Generate a simulated infrared signal.
        
        Returns:
            Dictionary containing simulated signal data
        """
        # Common IR remote frequencies
        frequencies = [36000, 38000, 40000, 56000]
        
        # Generate pattern (pairs of on/off times in microseconds)
        pattern_length = random.randint(10, 30)
        pattern = []
        for _ in range(pattern_length):
            # On time (typically shorter)
            pattern.append(random.randint(500, 2000))
            # Off time (typically longer)
            pattern.append(random.randint(1000, 5000))
            
        # Generate signal data
        frequency = random.choice(frequencies)
        duration = sum(pattern) / 1000  # Convert to milliseconds
        
        # Common remote types
        remote_types = ["TV", "DVD", "AC", "Stereo", "Projector"]
        remote_type = random.choice(remote_types)
        
        # Create signal object
        return {
            'type': 'infrared',
            'timestamp': time.time(),
            'frequency': frequency,
            'duration': duration,
            'pattern': pattern,
            'name': f"{remote_type} Remote Signal",
            'remote_type': remote_type
        }
        
    def record_signal(self, signal_info):
        """
        Record an infrared signal.
        
        Args:
            signal_info: Dictionary containing signal information
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            # Create a signal model
            signal_data = {
                'protocol': 'infrared',
                'frequency': signal_info.get('frequency'),
                'pattern': signal_info.get('pattern', []),
                'metadata': {
                    'record_time': time.time(),
                    'platform': platform,
                    'remote_type': signal_info.get('remote_type', 'Unknown')
                }
            }
            
            signal = SignalModel(
                signal_type='infrared',
                data=signal_data,
                name=signal_info.get('name', 'IR Signal'),
                frequency=signal_info.get('frequency', 0),
                duration=signal_info.get('duration', 0),
                pattern=signal_info.get('pattern', [])
            )
            
            # Save to storage
            return self.storage_service.save_record(signal.to_dict())
            
        except Exception as e:
            print(f"Error recording infrared signal: {str(e)}")
            return False
            
    def transmit_signal(self, signal_data):
        """
        Transmit an infrared signal.
        
        Args:
            signal_data: Dictionary containing signal data
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.available:
            return False
            
        try:
            frequency = signal_data.get('frequency', 0)
            pattern = signal_data.get('pattern', [])
            
            if not frequency or not pattern:
                # Try to get pattern from the data field
                data = signal_data.get('data', {})
                if isinstance(data, dict):
                    frequency = data.get('frequency', frequency)
                    pattern = data.get('pattern', pattern)
            
            if platform == 'android' and self.consumer_ir:
                # Transmit on Android
                if self.consumer_ir.hasIrEmitter():
                    # Convert pattern to int array if it's not already
                    if pattern and isinstance(pattern, list):
                        # Ensure the pattern is a list of integers
                        pattern = [int(p) for p in pattern]
                        self.consumer_ir.transmit(frequency, pattern)
                        return True
                return False
            else:
                # Simulate transmission on other platforms
                print(f"Simulating IR transmission: Frequency={frequency}Hz, Pattern={pattern}")
                return True
                
        except Exception as e:
            print(f"Error transmitting infrared signal: {str(e)}")
            return False
