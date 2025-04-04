"""
Records screen implementation for Signal Catcher app.
Displays and manages saved signal records.
Using standard Kivy widgets instead of KivyMD.
"""
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
import datetime

from app.services.storage_service import StorageService
from app.ui.detail_screen import DetailScreen

# Define the KV language string for the RecordsScreen
KV = '''
<RecordsScreen>:
    orientation: "vertical"
    padding: 16
    spacing: 10
    
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: 56
        spacing: 8
        
        Label:
            text: "Recorded Signals"
            font_size: '20sp'
            size_hint_x: 0.7
        
        Button:
            text: "Filter"
            size_hint_x: 0.15
            on_release: root.show_filter_menu()
        
        Button:
            text: "Refresh"
            size_hint_x: 0.15
            on_release: root.load_records()
    
    ScrollView:
        GridLayout:
            id: records_list
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: 2
                
    Label:
        id: no_records_label
        text: "No records found."
        opacity: 0
'''

class SignalRecordItem(Button):
    """Button representing a signal record."""
    def __init__(self, record, **kwargs):
        """
        Initialize a signal record button.
        
        Args:
            record: Dictionary containing record information
            **kwargs: Additional keyword arguments
        """
        timestamp = datetime.datetime.fromtimestamp(record.get('timestamp', 0))
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        display_text = f"{record.get('name', 'Unknown Signal')}\n" \
                       f"Type: {record.get('type', 'Unknown')} | {formatted_time}"
        
        super().__init__(text=display_text, **kwargs)
        self.record = record
        self.size_hint_y = None
        self.height = 80
        self.halign = 'left'
        
        # Set different background color based on signal type
        if record.get('type') == "bluetooth":
            self.background_color = (0.2, 0.6, 1, 1)  # blue for bluetooth
        else:
            self.background_color = (1, 0.8, 0, 1)  # amber for infrared

class RecordsScreen(BoxLayout):
    """
    Screen for displaying and managing saved signal records.
    Using standard Kivy widgets instead of KivyMD.
    """
    def __init__(self, **kwargs):
        """Initialize the records screen with its components."""
        super().__init__(**kwargs)
        Builder.load_string(KV)
        self.storage_service = StorageService()
        self.current_filter = None
        self.records = []
    
    def on_parent(self, widget, parent):
        """Called when the screen is added to a parent widget."""
        # Load records when the screen is added to a parent
        if parent:
            self.load_records()
    
    def load_records(self, filter_type=None):
        """
        Load signal records from storage.
        
        Args:
            filter_type: Optional filter for signal type (bluetooth/infrared)
        """
        self.current_filter = filter_type
        
        try:
            # Get records from storage service
            self.records = self.storage_service.get_all_records()
            
            # Apply filter if specified
            if filter_type:
                self.records = [r for r in self.records if r.get('type') == filter_type]
                
            # Update UI
            self.update_records_list()
                
        except Exception as e:
            self.show_message("Error", f"Error loading records: {str(e)}")
    
    def update_records_list(self):
        """Update the records list in the UI."""
        self.ids.records_list.clear_widgets()
        
        if not self.records:
            self.ids.no_records_label.opacity = 1
        else:
            self.ids.no_records_label.opacity = 0
            
            for record in self.records:
                item = SignalRecordItem(record)
                item.bind(on_release=lambda x, record=record: self.view_record_details(record))
                self.ids.records_list.add_widget(item)
    
    def view_record_details(self, record):
        """
        View details of a selected record.
        
        Args:
            record: The record to view
        """
        try:
            # For now, just show a popup with record details
            # In a real implementation, we would switch to a detail screen
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            # Create a formatted display of the record details
            timestamp = datetime.datetime.fromtimestamp(record.get('timestamp', 0))
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            details = f"Name: {record.get('name', 'Unknown')}\n" \
                      f"Type: {record.get('type', 'Unknown')}\n" \
                      f"Time: {formatted_time}\n"
                      
            if record.get('type') == 'bluetooth':
                details += f"Device: {record.get('device_name', 'Unknown')}\n" \
                           f"Address: {record.get('address', 'Unknown')}"
            else:
                details += f"Frequency: {record.get('frequency', 'Unknown')} Hz\n" \
                           f"Duration: {record.get('duration', 'Unknown')} ms"
            
            content.add_widget(Label(text=details))
            
            # Add buttons for actions
            buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
            
            # Transmit button
            transmit_btn = Button(text='Transmit Signal')
            transmit_btn.bind(on_release=lambda x: self.show_message("Transmit", "Signal transmission initiated."))
            buttons.add_widget(transmit_btn)
            
            # Delete button
            delete_btn = Button(text='Delete')
            delete_btn.bind(on_release=lambda x: self.show_message("Delete", "Record deleted successfully."))
            buttons.add_widget(delete_btn)
            
            # Close button
            close_btn = Button(text='Close')
            close_btn.bind(on_release=lambda x: popup.dismiss())
            buttons.add_widget(close_btn)
            
            content.add_widget(buttons)
            
            # Create popup
            popup = Popup(title=f"{record.get('name', 'Signal Details')}", 
                          content=content, 
                          size_hint=(0.9, 0.6))
            popup.open()
            
        except Exception as e:
            self.show_message("Error", f"Error viewing record: {str(e)}")
    
    def show_filter_menu(self):
        """Show the filter options in a popup."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="Select filter option:"))
        
        # Create filter buttons
        all_btn = Button(text='All Signals')
        all_btn.bind(on_release=lambda x: self.filter_records(None, popup))
        content.add_widget(all_btn)
        
        bt_btn = Button(text='Bluetooth Signals')
        bt_btn.bind(on_release=lambda x: self.filter_records("bluetooth", popup))
        content.add_widget(bt_btn)
        
        ir_btn = Button(text='Infrared Signals')
        ir_btn.bind(on_release=lambda x: self.filter_records("infrared", popup))
        content.add_widget(ir_btn)
        
        # Add cancel button
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        content.add_widget(cancel_btn)
        
        # Create popup
        popup = Popup(title="Filter Options", content=content, size_hint=(0.8, 0.6))
        popup.open()
    
    def filter_records(self, filter_type, popup=None):
        """
        Apply a filter to the records list.
        
        Args:
            filter_type: The type of signals to filter for (None for all)
            popup: Optional popup to dismiss
        """
        if popup:
            popup.dismiss()
        self.load_records(filter_type)
        
        # Show message with current filter
        filter_text = "All Signals" if filter_type is None else f"{filter_type.capitalize()} Signals"
        self.show_message("Filter Applied", f"Showing {filter_text}")
    
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
