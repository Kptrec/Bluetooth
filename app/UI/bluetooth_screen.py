"""
Bluetooth screen implementation for Signal Catcher app.
Handles Bluetooth signal scanning and recording.
"""
import threading
import time
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
# ListView ve ListItemButton modern Kivy'de kaldırıldı
# Bunun yerine GridLayout kullanıyoruz
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

from app.services.bluetooth_service import BluetoothService

# Define the KV language string for the BluetoothScreen
KV = '''
<BluetoothScreen>:
    orientation: "vertical"
    padding: 16
    spacing: 10
    
    Label:
        text: "Bluetooth Signal Scanner"
        font_size: '20sp'
        size_hint_y: None
        height: self.texture_size[1]
        
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: 48
        spacing: 8
        
        Button:
            id: scan_button
            text: "Start Scan"
            on_release: root.toggle_scan()
            background_color: 0.2, 0.6, 1, 1
            
        Button:
            id: record_button
            text: "Record Signal"
            on_release: root.record_selected_device()
            background_color: 1, 0.8, 0, 1
            disabled: True
    
    Label:
        text: "Detected Devices"
        font_size: '18sp'
        size_hint_y: None
        height: self.texture_size[1]
        
    ScrollView:
        GridLayout:
            id: device_list
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: 2
    
    ProgressBar:
        id: scan_progress
        max: 100
        value: 0
        size_hint_y: None
        height: 4
'''

class BluetoothDeviceItem(Button):
    """Button representing a Bluetooth device."""
    def __init__(self, device_info, **kwargs):
        """
        Initialize a Bluetooth device button.
        
        Args:
            device_info: Dictionary containing device information
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)
        self.device_info = device_info
        self.text = f"{device_info['name']} ({device_info['address']})"
        self.size_hint_y = None
        self.height = 50
        
class BluetoothScreen(BoxLayout):
    """
    Screen for scanning and recording Bluetooth signals.
    """
    def __init__(self, **kwargs):
        """Initialize the Bluetooth screen with its components."""
        super().__init__(**kwargs)
        Builder.load_string(KV)
        self.bluetooth_service = BluetoothService()
        self.scanning = False
        self.scan_thread = None
        self.selected_device = None
        self.selected_button = None
        
    def on_parent(self, widget, parent):
        """Called when the screen is added to a parent widget."""
        # Initialize Bluetooth service when screen is added to parent
        if parent and not self.bluetooth_service.is_initialized():
            self.initialize_bluetooth()
    
    def initialize_bluetooth(self):
        """Initialize the Bluetooth service."""
        try:
            self.bluetooth_service.initialize()
            if not self.bluetooth_service.is_available():
                self.show_message("Bluetooth Not Available", 
                                "Bluetooth is not available on this device. Please make sure Bluetooth is enabled.")
        except Exception as e:
            self.show_message("Bluetooth Error", 
                              f"Failed to initialize Bluetooth: {str(e)}")
    
    def toggle_scan(self):
        """Toggle Bluetooth scanning on/off."""
        if self.scanning:
            self.stop_scan()
        else:
            self.start_scan()
    
    def start_scan(self):
        """Start Bluetooth scanning process."""
        if not self.bluetooth_service.is_available():
            self.show_message("Bluetooth Not Available", 
                            "Bluetooth is not available. Please enable Bluetooth in your device settings.")
            return
        
        self.scanning = True
        self.ids.scan_button.text = "Stop Scan"
        self.ids.device_list.clear_widgets()
        self.ids.scan_progress.value = 0
        
        # Start progress animation
        self.progress_event = Clock.schedule_interval(self.update_progress, 0.1)
        
        # Start scan in a separate thread
        self.scan_thread = threading.Thread(target=self.scan_process)
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def stop_scan(self):
        """Stop Bluetooth scanning process."""
        if self.scanning:
            self.scanning = False
            self.ids.scan_button.text = "Start Scan"
            if hasattr(self, 'progress_event'):
                self.progress_event.cancel()
            self.ids.scan_progress.value = 0
    
    def scan_process(self):
        """Background process for Bluetooth scanning."""
        try:
            devices = self.bluetooth_service.scan_devices()
            
            # Update UI on the main thread
            def update_ui(dt):
                self.ids.device_list.clear_widgets()
                for device in devices:
                    item = BluetoothDeviceItem(device)
                    item.bind(on_release=self.select_device)
                    self.ids.device_list.add_widget(item)
                self.stop_scan()
                
            Clock.schedule_once(update_ui)
            
        except Exception as e:
            def show_error(dt):
                self.show_message("Scan Error", f"Error during scan: {str(e)}")
                self.stop_scan()
            Clock.schedule_once(show_error)
    
    def update_progress(self, dt):
        """Update the scan progress indicator."""
        self.ids.scan_progress.value = (self.ids.scan_progress.value + 2) % 100
    
    def select_device(self, instance):
        """
        Handle device selection from the list.
        
        Args:
            instance: The selected device button
        """
        self.selected_device = instance.device_info
        self.ids.record_button.disabled = False
        
        # Reset previously selected button
        if self.selected_button:
            self.selected_button.background_color = (1, 1, 1, 1)
        
        # Highlight the new selected button
        instance.background_color = (0.8, 0.8, 1, 1)
        self.selected_button = instance
    
    def record_selected_device(self):
        """Record the signal of the selected Bluetooth device."""
        if not self.selected_device:
            return
            
        try:
            # Attempt to record the device signal
            success = self.bluetooth_service.record_device(self.selected_device)
            
            if success:
                self.show_message("Signal Recorded", 
                                 f"Successfully recorded signal from {self.selected_device['name']}")
            else:
                self.show_message("Recording Failed", 
                                 "Failed to record the Bluetooth signal.")
                
        except Exception as e:
            self.show_message("Recording Error", 
                             f"Error recording signal: {str(e)}")
    
    def show_message(self, title, message):
        """
        Display a message dialog.
        
        Args:
            title: Dialog title
            message: Dialog message
        """
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        
        # Add OK button
        btn = Button(text='OK', size_hint=(1, None), height=50)
        content.add_widget(btn)
        
        # Create popup
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        
        # Bind button to close popup
        btn.bind(on_release=popup.dismiss)
        
        popup.open()
