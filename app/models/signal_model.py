"""
Signal model definition for Signal Catcher app.
Defines the structure and validation for signal data.
"""
import time
import uuid

class SignalModel:
    """
    Model class for signal data.
    Provides structure and validation for both Bluetooth and infrared signals.
    """
    def __init__(self, signal_type, data, **kwargs):
        """
        Initialize a new signal model.
        
        Args:
            signal_type: Type of signal ('bluetooth' or 'infrared')
            data: Raw signal data
            **kwargs: Additional signal properties
        """
        # Generate a unique ID
        self.id = kwargs.get('id', str(uuid.uuid4()))
        
        # Set required properties
        self.type = signal_type
        self.name = kwargs.get('name', f"{signal_type.capitalize()} Signal")
        self.timestamp = kwargs.get('timestamp', time.time())
        self.data = data
        
        # Set type-specific properties
        if signal_type == 'bluetooth':
            self.device_name = kwargs.get('device_name', 'Unknown Device')
            self.address = kwargs.get('address', 'Unknown')
            self.rssi = kwargs.get('rssi', 0)
        elif signal_type == 'infrared':
            self.frequency = kwargs.get('frequency', 0)
            self.duration = kwargs.get('duration', 0)
            self.pattern = kwargs.get('pattern', [])
            
    def to_dict(self):
        """
        Convert the signal model to a dictionary.
        
        Returns:
            Dictionary representation of the signal
        """
        # Base properties for all signals
        result = {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'timestamp': self.timestamp,
            'data': self.data
        }
        
        # Add type-specific properties
        if self.type == 'bluetooth':
            result.update({
                'device_name': getattr(self, 'device_name', 'Unknown Device'),
                'address': getattr(self, 'address', 'Unknown'),
                'rssi': getattr(self, 'rssi', 0)
            })
        elif self.type == 'infrared':
            result.update({
                'frequency': getattr(self, 'frequency', 0),
                'duration': getattr(self, 'duration', 0),
                'pattern': getattr(self, 'pattern', [])
            })
            
        return result
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a signal model from a dictionary.
        
        Args:
            data: Dictionary containing signal data
            
        Returns:
            SignalModel instance
        """
        signal_type = data.get('type')
        signal_data = data.get('data')
        
        # Create model instance with the dictionary data
        return cls(signal_type, signal_data, **data)
    
    @staticmethod
    def validate(data):
        """
        Validate signal data.
        
        Args:
            data: Dictionary containing signal data to validate
            
        Returns:
            Boolean indicating if data is valid
        """
        # Check required fields
        required_fields = ['type', 'data']
        for field in required_fields:
            if field not in data:
                return False
                
        # Validate type-specific fields
        signal_type = data.get('type')
        if signal_type == 'bluetooth':
            if 'address' not in data:
                return False
        elif signal_type == 'infrared':
            if 'frequency' not in data and 'pattern' not in data:
                return False
        else:
            # Unsupported signal type
            return False
            
        return True
