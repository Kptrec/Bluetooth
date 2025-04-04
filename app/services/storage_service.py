"""
Storage service implementation for Signal Catcher app.
Provides an interface to the database for signal storage operations.
"""
from app.models.database import Database

class StorageService:
    """
    Service for storage operations.
    Provides methods to save, retrieve, update, and delete signal records.
    """
    def __init__(self):
        """Initialize the storage service."""
        self.database = Database()
        
    def save_record(self, record_data):
        """
        Save a signal record to storage.
        
        Args:
            record_data: Dictionary containing record data
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            # Insert record into database
            record_id = self.database.insert_signal(record_data)
            return record_id is not None
            
        except Exception as e:
            print(f"Error saving record: {str(e)}")
            return False
            
    def get_record(self, record_id):
        """
        Retrieve a signal record by ID.
        
        Args:
            record_id: ID of the record to retrieve
            
        Returns:
            Dictionary containing record data or None if not found
        """
        try:
            return self.database.get_signal(record_id)
            
        except Exception as e:
            print(f"Error retrieving record: {str(e)}")
            return None
            
    def get_all_records(self, record_type=None):
        """
        Retrieve all signal records, optionally filtered by type.
        
        Args:
            record_type: Optional type to filter by
            
        Returns:
            List of dictionaries containing record data
        """
        try:
            return self.database.get_all_signals(record_type)
            
        except Exception as e:
            print(f"Error retrieving records: {str(e)}")
            return []
            
    def update_record(self, record_id, record_data):
        """
        Update a signal record.
        
        Args:
            record_id: ID of the record to update
            record_data: Dictionary containing updated record data
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            return self.database.update_signal(record_id, record_data)
            
        except Exception as e:
            print(f"Error updating record: {str(e)}")
            return False
            
    def delete_record(self, record_id):
        """
        Delete a signal record by ID.
        
        Args:
            record_id: ID of the record to delete
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            return self.database.delete_signal(record_id)
            
        except Exception as e:
            print(f"Error deleting record: {str(e)}")
            return False
