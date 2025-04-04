"""
Main module for the Signal Catcher application.
This module initializes the application and serves as the entry point.
Using standard Kivy instead of KivyMD for better compatibility.
"""
import os
import sys

os.environ['KIVY_GL_BACKEND'] = 'sdl2'

from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform

# Add app directory to path to allow importing app modules
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_dir)

from app.ui.main_screen import MainScreen
from app.models.database import Database

class SignalCatcherApp(App):
    """
    Main application class for Signal Catcher.
    Initializes the database and UI.
    Using standard Kivy instead of KivyMD.
    """
    def __init__(self, **kwargs):
        """Initialize the application."""
        super().__init__(**kwargs)
        self.title = "Signal Catcher"
        
        # Initialize database
        self.database = Database()
        self.database.setup()

    def build(self):
        """Build the application UI."""
        # Request permissions if on Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.BLUETOOTH,
                Permission.BLUETOOTH_ADMIN,
                Permission.ACCESS_FINE_LOCATION,
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
            
        # Set window size for desktop testing
        if platform != 'android':
            Window.size = (380, 700)
            
        return MainScreen()

if __name__ == '__main__':
    SignalCatcherApp().run()
