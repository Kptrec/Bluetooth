"""
Database management for Signal Catcher app.
Handles SQLite database operations for storing signal records.
"""
import os
import sqlite3
import json
from kivy.utils import platform

class Database:
    """
    SQLite database manager for the Signal Catcher app.
    Handles database creation, connection, and operations.
    """
    def __init__(self):
        """Initialize the database manager."""
        self.conn = None
        self.cursor = None
        self.db_path = self._get_db_path()
        
    def _get_db_path(self):
        """
        Get the appropriate database path based on platform.
        
        Returns:
            String path to the database file
        """
        if platform == 'android':
            # Use Android's app storage directory
            from android.storage import app_storage_path
            app_dir = app_storage_path()
            return os.path.join(app_dir, 'signal_catcher.db')
        else:
            # Use current directory for other platforms
            return 'signal_catcher.db'
        
    def setup(self):
        """Set up the database and create necessary tables if they don't exist."""
        try:
            self.connect()
            
            # Create signals table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    data TEXT,
                    properties TEXT
                )
            ''')
            
            self.conn.commit()
        except Exception as e:
            print(f"Database setup error: {str(e)}")
        finally:
            self.disconnect()
            
    def connect(self):
        """Establish a connection to the SQLite database."""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable row access by column name
            self.cursor = self.conn.cursor()
            
    def disconnect(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            
    def insert_signal(self, signal_dict):
        """
        Insert a new signal record into the database.
        
        Args:
            signal_dict: Dictionary containing signal data
            
        Returns:
            String ID of the inserted record or None on failure
        """
        try:
            self.connect()
            
            # Extract main fields
            signal_id = signal_dict.get('id')
            signal_type = signal_dict.get('type')
            signal_name = signal_dict.get('name')
            signal_timestamp = signal_dict.get('timestamp')
            
            # Extract data field
            data = signal_dict.get('data')
            if isinstance(data, (dict, list)):
                data = json.dumps(data)
                
            # Extract all other properties
            properties_dict = {k: v for k, v in signal_dict.items() 
                             if k not in ('id', 'type', 'name', 'timestamp', 'data')}
            properties = json.dumps(properties_dict)
            
            # Insert the record
            self.cursor.execute('''
                INSERT INTO signals (id, type, name, timestamp, data, properties)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (signal_id, signal_type, signal_name, signal_timestamp, data, properties))
            
            self.conn.commit()
            return signal_id
            
        except Exception as e:
            print(f"Error inserting signal: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return None
        finally:
            self.disconnect()
            
    def get_signal(self, signal_id):
        """
        Retrieve a signal record by ID.
        
        Args:
            signal_id: ID of the signal to retrieve
            
        Returns:
            Dictionary containing signal data or None if not found
        """
        try:
            self.connect()
            
            self.cursor.execute('''
                SELECT * FROM signals WHERE id = ?
            ''', (signal_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return None
                
            # Convert row to dictionary
            result = dict(row)
            
            # Parse JSON fields
            if 'data' in result and result['data']:
                try:
                    result['data'] = json.loads(result['data'])
                except:
                    pass  # Keep as string if not valid JSON
                    
            if 'properties' in result and result['properties']:
                try:
                    properties = json.loads(result['properties'])
                    # Merge properties into the result
                    result.update(properties)
                    del result['properties']
                except:
                    pass
                    
            return result
            
        except Exception as e:
            print(f"Error getting signal: {str(e)}")
            return None
        finally:
            self.disconnect()
            
    def get_all_signals(self, signal_type=None):
        """
        Retrieve all signal records, optionally filtered by type.
        
        Args:
            signal_type: Optional type to filter by
            
        Returns:
            List of dictionaries containing signal data
        """
        try:
            self.connect()
            
            if signal_type:
                query = "SELECT * FROM signals WHERE type = ? ORDER BY timestamp DESC"
                self.cursor.execute(query, (signal_type,))
            else:
                query = "SELECT * FROM signals ORDER BY timestamp DESC"
                self.cursor.execute(query)
                
            rows = self.cursor.fetchall()
            result = []
            
            for row in rows:
                # Convert row to dictionary
                signal_dict = dict(row)
                
                # Parse JSON fields
                if 'data' in signal_dict and signal_dict['data']:
                    try:
                        signal_dict['data'] = json.loads(signal_dict['data'])
                    except:
                        pass  # Keep as string if not valid JSON
                        
                if 'properties' in signal_dict and signal_dict['properties']:
                    try:
                        properties = json.loads(signal_dict['properties'])
                        # Merge properties into the result
                        signal_dict.update(properties)
                        del signal_dict['properties']
                    except:
                        pass
                        
                result.append(signal_dict)
                
            return result
            
        except Exception as e:
            print(f"Error getting signals: {str(e)}")
            return []
        finally:
            self.disconnect()
            
    def update_signal(self, signal_id, signal_dict):
        """
        Update an existing signal record.
        
        Args:
            signal_id: ID of the signal to update
            signal_dict: Dictionary containing updated signal data
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            self.connect()
            
            # Extract main fields
            signal_type = signal_dict.get('type')
            signal_name = signal_dict.get('name')
            signal_timestamp = signal_dict.get('timestamp')
            
            # Extract data field
            data = signal_dict.get('data')
            if isinstance(data, (dict, list)):
                data = json.dumps(data)
                
            # Extract all other properties
            properties_dict = {k: v for k, v in signal_dict.items() 
                             if k not in ('id', 'type', 'name', 'timestamp', 'data')}
            properties = json.dumps(properties_dict)
            
            # Update the record
            self.cursor.execute('''
                UPDATE signals
                SET type = ?, name = ?, timestamp = ?, data = ?, properties = ?
                WHERE id = ?
            ''', (signal_type, signal_name, signal_timestamp, data, properties, signal_id))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating signal: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False
        finally:
            self.disconnect()
            
    def delete_signal(self, signal_id):
        """
        Delete a signal record by ID.
        
        Args:
            signal_id: ID of the signal to delete
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            self.connect()
            
            self.cursor.execute('''
                DELETE FROM signals WHERE id = ?
            ''', (signal_id,))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error deleting signal: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False
        finally:
            self.disconnect()
