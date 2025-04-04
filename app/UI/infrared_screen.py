"""
Infrared screen implementation for Signal Catcher app.
Handles infrared signal detection and recording.
Using standard Kivy widgets instead of KivyMD.
"""
import threading
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

from app.services.infrared_service import InfraredService

# Define the KV language string for the InfraredScreen
KV = '''
<InfraredScreen>:
    orientation: "vertical"
    padding: 16
    spacing: 10
    
    Label:
        text: "Infrared Signal Detector"
        font_size: '20sp'
        size_hint_y: None
        height: self.texture_size[1]
        
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: 48
        spacing: 8
        
        Button:
            id: listen_button
            text: "Start Listening"
            on_release: root.toggle_listening()
            background_color: 0.2, 0.6, 1, 1
            
        Button:
            id: record_button
            text: "Record Signal"
            on_release: root.record_signal()
            background_color: 1, 0.8, 0, 1
            disabled: True
    
    Label:
        text: "Signal Information"
        font_size: '18sp'
        size_hint_y: None
        height: self.texture_size[1]
    
    BoxLayout:
        id: signal_info_card
        orientation: "vertical"
        padding: 8
        size_hint: 1, None
        height: 200
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            id: signal_info
            text: "No signal detected."
            halign: "center"
            valign: "center"
    
    Label:
        text: "Recent Signals"
        font_size: '18sp'
        size_hint_y: None
        height: self.texture_size[1]
    
    ScrollView:
        GridLayout:
            id: signal_list
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: 2
    
    ProgressBar:
        id: listen_progress
        max: 100
        value: 0
        size_hint_y: None
        height: 4
'''

class IRSignalCard(BoxLayout):
    """Card representing an infrared signal."""
    def __init__(self, signal_info, **kwargs):
        """
        Initialize an infrared signal card.
        
        Args:
            signal_info: Dictionary containing signal information
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)
        self.signal_info = signal_info
        self.orientation = "vertical"
        self.padding = 8
        self.size_hint = (1, None)
        self.height = 100
        
        # Add background
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Add signal info to the card
        label = Label(
            text=(f"Signal detected at {signal_info['timestamp']}\n"
                 f"Frequency: {signal_info.get('frequency', 'Unknown')} Hz\n"
                 f"Duration: {signal_info.get('duration', 'Unknown')} ms"),
            halign="left",
            size_hint_y=None,
            height=80
        )
        self.add_widget(label)
    
    def _update_rect(self, instance, value):
        """Update the background rectangle position and size."""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class InfraredScreen(BoxLayout):
    """
    Screen for detecting and recording infrared signals.
    Using standard Kivy widgets instead of KivyMD.
    """
    def __init__(self, **kwargs):
        """Initialize the infrared screen with its components."""
        super().__init__(**kwargs)
        Builder.load_string(KV)
        self.infrared_service = InfraredService()
        self.listening = False
        self.listen_thread = None
        self.current_signal = None
        
    def on_parent(self, widget, parent):
        """Called when the screen is added to a parent widget."""
        # Initialize infrared service when screen is added to parent
        if parent and not self.infrared_service.is_initialized():
            self.initialize_infrared()
    
    def initialize_infrared(self):
        """Initialize the infrared service."""
        try:
            self.infrared_service.initialize()
            if not self.infrared_service.is_available():
                self.show_message("Infrared Not Available", 
                                "Infrared receiver is not available on this device.")
        except Exception as e:
            self.show_message("Infrared Error", 
                              f"Failed to initialize infrared sensor: {str(e)}")
    
    def toggle_listening(self):
        """Toggle infrared listening on/off."""
        if self.listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        """Start infrared signal listening process."""
        if not self.infrared_service.is_available():
            self.show_message("Infrared Not Available", 
                            "Infrared receiver is not available on this device.")
            return
        
        self.listening = True
        self.ids.listen_button.text = "Stop Listening"
        self.ids.signal_info.text = "Listening for infrared signals..."
        self.ids.listen_progress.value = 0
        
        # Start progress animation
        self.progress_event = Clock.schedule_interval(self.update_progress, 0.1)
        
        # Start listening in a separate thread
        self.listen_thread = threading.Thread(target=self.listen_process)
        self.listen_thread.daemon = True
        self.listen_thread.start()
    
    def stop_listening(self):
        """Stop infrared signal listening process."""
        if self.listening:
            self.listening = False
            self.ids.listen_button.text = "Start Listening"
            if hasattr(self, 'progress_event'):
                self.progress_event.cancel()
            self.ids.listen_progress.value = 0
            self.infrared_service.stop_listening()
    
    def listen_process(self):
        """Background process for infrared listening."""
        try:
            def signal_callback(signal):
                def update_ui(dt):
                    self.current_signal = signal
                    self.ids.signal_info.text = (
                        f"Signal detected!\n"
                        f"Frequency: {signal.get('frequency', 'Unknown')} Hz\n"
                        f"Duration: {signal.get('duration', 'Unknown')} ms\n"
                        f"Pattern: {signal.get('pattern', 'Unknown')}"
                    )
                    self.ids.record_button.disabled = False
                    
                    # Add to recent signals list
                    signal_card = IRSignalCard(signal)
                    self.ids.signal_list.add_widget(signal_card)
                    
                Clock.schedule_once(update_ui)
            
            self.infrared_service.start_listening(signal_callback)
            
        except Exception as e:
            def show_error(dt):
                self.show_message("Listening Error", f"Error while listening: {str(e)}")
                self.stop_listening()
            Clock.schedule_once(show_error)
    
    def update_progress(self, dt):
        """Update the listening progress indicator."""
        self.ids.listen_progress.value = (self.ids.listen_progress.value + 1) % 100
    
    def record_signal(self):
        """Record the current infrared signal."""
        if not self.current_signal:
            self.show_message("No Signal", "No infrared signal detected to record.")
            return
            
        try:
            # Record the current signal
            success = self.infrared_service.record_signal(self.current_signal)
            
            if success:
                self.show_message("Signal Recorded", 
                                 "Successfully recorded the infrared signal.")
            else:
                self.show_message("Recording Failed", 
                                 "Failed to record the infrared signal.")
                
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
