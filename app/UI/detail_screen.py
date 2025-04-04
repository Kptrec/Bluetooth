"""
Detail screen implementation for Signal Catcher app.
Displays detailed information about a selected signal record.
Using standard Kivy widgets instead of KivyMD.
"""
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import datetime

from app.services.storage_service import StorageService
from app.services.bluetooth_service import BluetoothService
from app.services.infrared_service import InfraredService

# Define the KV language string for the DetailScreen
KV = '''
<DetailScreen>:
    orientation: "vertical"
    padding: 16
    spacing: 10
    
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: 56
        spacing: 8
        
        Button:
            text: "Back"
            size_hint_x: 0.2
            on_release: root.go_back()
        
        Label:
            id: detail_title
            text: "Signal Details"
            font_size: '20sp'
            size_hint_x: 0.8
            
    BoxLayout:
        orientation: "vertical"
        padding: 10
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            id: signal_name
            text: "Signal Name"
            font_size: '18sp'
            size_hint_y: None
            height: self.texture_size[1]
            color: 0, 0, 0, 1
            
        Label:
            id: signal_type
            text: "Type: "
            size_hint_y: None
            height: self.texture_size[1]
            color: 0, 0, 0, 1
            
        Label:
            id: signal_timestamp
            text: "Recorded at: "
            size_hint_y: None
            height: self.texture_size[1]
            color: 0, 0, 0, 1
            
        Label:
            id: signal_properties
            text: "Properties: "
            size_hint_y: None
            height: self.texture_size[1] * 4
            color: 0, 0, 0, 1
            text_size: self.width, None
            halign: 'left'
        
        Label:
            id: signal_data
            text: "Signal Data: "
            size_hint_y: None
            height: self.texture_size[1] * 3
            color: 0, 0, 0, 1
            text_size: self.width, None
            halign: 'left'
    
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: 50
        spacing: 10
        padding: [0, 10, 0, 0]
        
        Button:
            text: "Share"
            on_release: root.share_record()
            background_color: 0.2, 0.6, 1, 1
            
        Button:
            text: "Transmit"
            on_release: root.transmit_signal()
            background_color: 1, 0.8, 0, 1
            
        Button:
            text: "Delete"
            on_release: root.delete_record()
            background_color: 0.8, 0.2, 0.2, 1
'''

class DetailScreen(BoxLayout):
    """
    Screen for displaying detailed information about a signal record.
    Using standard Kivy widgets instead of KivyMD.
    """
    def __init__(self, **kwargs):
        """Initialize the detail screen with its components."""
        super().__init__(**kwargs)
        Builder.load_string(KV)
        self.storage_service = StorageService()
        self.bluetooth_service = BluetoothService()
        self.infrared_service = InfraredService()
        self.current_record = None
        
    def set_record(self, record):
        """
        Set the current record and update the UI.
        
        Args:
            record: The record to display
        """
        self.current_record = record
        
        # Update UI with record details
        self.ids.signal_name.text = record.get('name', 'Unknown Signal')
        self.ids.signal_type.text = f"Type: {record.get('type', 'Unknown').capitalize()}"
        
        # Format timestamp
        timestamp = datetime.datetime.fromtimestamp(record.get('timestamp', 0))
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.ids.signal_timestamp.text = f"Recorded at: {formatted_time}"
        
        # Format properties based on signal type
        if record.get('type') == 'bluetooth':
            properties = f"Properties:\n" \
                         f"Device Name: {record.get('device_name', 'Unknown')}\n" \
                         f"Device Address: {record.get('address', 'Unknown')}\n" \
                         f"Signal Strength: {record.get('rssi', 'Unknown')} dBm"
        else:  # infrared
            properties = f"Properties:\n" \
                         f"Frequency: {record.get('frequency', 'Unknown')} Hz\n" \
                         f"Duration: {record.get('duration', 'Unknown')} ms"
                         
        self.ids.signal_properties.text = properties
        
        # Format signal data (limited display for large data)
        data = record.get('data', '')
        if isinstance(data, dict):
            import json
            data = json.dumps(data, indent=2)
        elif isinstance(data, (list, bytes)):
            data = str(data)
            
        if len(data) > 200:
            data = data[:200] + "... (truncated)"
            
        self.ids.signal_data.text = f"Signal Data:\n{data}"
    
    def go_back(self):
        """Return to the records screen."""
        if hasattr(self.parent, 'current'):
            self.parent.current = "records_screen"
    
    def share_record(self):
        """Share the current record."""
        if not self.current_record:
            return
            
        try:
            if platform == 'android':
                from android.content import Intent
                from jnius import autoclass
                
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                String = autoclass('java.lang.String')
                
                # Create sharing intent
                intent = Intent()
                intent.setAction(Intent.ACTION_SEND)
                
                # Create shareable text from record
                record_type = self.current_record.get('type', 'Unknown')
                record_name = self.current_record.get('name', 'Unknown Signal')
                timestamp = datetime.datetime.fromtimestamp(self.current_record.get('timestamp', 0))
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                share_text = f"Signal: {record_name}\n" \
                             f"Type: {record_type}\n" \
                             f"Recorded at: {formatted_time}\n"
                
                # Add type-specific details
                if record_type == 'bluetooth':
                    share_text += f"Device: {self.current_record.get('device_name', 'Unknown')}\n" \
                                 f"Address: {self.current_record.get('address', 'Unknown')}"
                else:
                    share_text += f"Frequency: {self.current_record.get('frequency', 'Unknown')} Hz"
                
                intent.putExtra(Intent.EXTRA_TEXT, String(share_text))
                intent.setType('text/plain')
                
                # Start the sharing activity
                current_activity = PythonActivity.mActivity
                current_activity.startActivity(Intent.createChooser(intent, String("Share Signal via")))
            else:
                # For non-Android platforms
                self.show_message("Sharing", "Sharing is only available on Android devices")
                
        except Exception as e:
            self.show_message("Error", f"Error sharing record: {str(e)}")
    
    def transmit_signal(self):
        """Transmit the current signal."""
        if not self.current_record:
            return
            
        signal_type = self.current_record.get('type')
        
        try:
            # Attempt to transmit based on signal type
            if signal_type == 'bluetooth':
                if self.bluetooth_service.is_available():
                    success = self.bluetooth_service.transmit_signal(self.current_record)
                    self.show_transmission_result(success)
                else:
                    self.show_message("Not Available", "Bluetooth not available for transmission")
            elif signal_type == 'infrared':
                if self.infrared_service.is_available():
                    success = self.infrared_service.transmit_signal(self.current_record)
                    self.show_transmission_result(success)
                else:
                    self.show_message("Not Available", "Infrared not available for transmission")
            else:
                self.show_message("Error", f"Unsupported signal type: {signal_type}")
                
        except Exception as e:
            self.show_message("Error", f"Error transmitting signal: {str(e)}")
    
    def show_transmission_result(self, success):
        """
        Show the result of a transmission attempt.
        
        Args:
            success: Boolean indicating if transmission was successful
        """
        if success:
            self.show_message("Success", "Signal transmitted successfully!")
        else:
            self.show_message("Failed", "Failed to transmit signal")
    
    def delete_record(self):
        """Delete the current record."""
        if not self.current_record:
            return
            
        # Show confirmation dialog
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="Are you sure you want to delete this record? This action cannot be undone."))
        
        # Add buttons
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        
        # Cancel button
        cancel_btn = Button(text='CANCEL')
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        buttons.add_widget(cancel_btn)
        
        # Delete button
        delete_btn = Button(text='DELETE', background_color=(0.8, 0.2, 0.2, 1))
        delete_btn.bind(on_release=lambda x: self.confirm_delete(popup))
        buttons.add_widget(delete_btn)
        
        content.add_widget(buttons)
        
        # Create popup
        popup = Popup(title="Delete Record", content=content, size_hint=(0.8, 0.4))
        popup.open()
    
    def confirm_delete(self, dialog):
        """
        Confirm and perform record deletion.
        
        Args:
            dialog: The confirmation dialog to dismiss
        """
        dialog.dismiss()
        
        try:
            # Delete record from storage
            record_id = self.current_record.get('id')
            success = self.storage_service.delete_record(record_id)
            
            if success:
                self.show_message("Success", "Record deleted successfully")
                
                # Return to records screen after short delay
                Clock.schedule_once(lambda dt: self.go_back(), 2)
            else:
                self.show_message("Failed", "Failed to delete record")
                
        except Exception as e:
            self.show_message("Error", f"Error deleting record: {str(e)}")
    
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
