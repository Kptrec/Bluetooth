"""
Main screen implementation for Signal Catcher app.
Acts as the container for all other screens using a simpler tab-based navigation.
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.ui.bluetooth_screen import BluetoothScreen
from app.ui.infrared_screen import InfraredScreen
from app.ui.records_screen import RecordsScreen

# Define the KV language string for the MainScreen
KV = '''
<MainScreen>:
    orientation: 'vertical'
    
    TabbedPanel:
        id: tab_panel
        do_default_tab: False
        tab_pos: 'top_mid'
        
        TabbedPanelItem:
            id: bluetooth_tab
            text: 'Bluetooth'
            BoxLayout:
                orientation: 'vertical'
                BluetoothScreen:
                    id: bluetooth_screen
                
        TabbedPanelItem:
            id: infrared_tab
            text: 'Infrared'
            BoxLayout:
                orientation: 'vertical'
                InfraredScreen:
                    id: infrared_screen
                
        TabbedPanelItem:
            id: records_tab
            text: 'Records'
            BoxLayout:
                orientation: 'vertical'
                RecordsScreen:
                    id: records_screen
'''

class MainScreen(BoxLayout):
    """
    Main screen with tabbed panel for navigation.
    Manages navigation between different screens.
    """
    def __init__(self, **kwargs):
        """Initialize the main screen with its components."""
        super().__init__(**kwargs)
        Builder.load_string(KV)
        # Default tab will be the first one (Bluetooth)
        
    def switch_tab(self, tab_name):
        """
        Switch to the specified tab.
        
        Args:
            tab_name: The name of the tab to switch to
        """
        tab_id = f"{tab_name.lower()}_tab"
        if hasattr(self.ids, tab_id):
            tab = getattr(self.ids, tab_id)
            self.ids.tab_panel.switch_to(tab)
