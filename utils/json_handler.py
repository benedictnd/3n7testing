import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class JsonHandler:
    """
    Utility class for handling JSON data operations
    """
    def __init__(self, base_dir="data"):
        """Initialize with the base directory for JSON files"""
        self.base_dir = base_dir
        # Ensure the data directory exists
        os.makedirs(self.base_dir, exist_ok=True)
        
    def _get_file_path(self, filename: str) -> str:
        """Get the full path to a JSON file"""
        return os.path.join(self.base_dir, filename)
    
    def read_json_file(self, filename: str) -> Dict:
        """Read and parse a JSON file"""
        file_path = self._get_file_path(filename)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    return json.load(file)
            return {}
        except Exception as e:
            print(f"Error reading {filename}: {str(e)}")
            return {}
    
    def write_json_file(self, filename: str, data: Dict) -> bool:
        """Write data to a JSON file"""
        file_path = self._get_file_path(filename)
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
            return True
        except Exception as e:
            print(f"Error writing to {filename}: {str(e)}")
            return False
    
    def append_to_json_array(self, filename: str, array_key: str, new_item: Dict) -> bool:
        """Append an item to a JSON array within a file"""
        data = self.read_json_file(filename)
        
        # Initialize the array if it doesn't exist
        if array_key not in data:
            data[array_key] = []
            
        # Add the new item
        if "id" not in new_item:
            new_item["id"] = str(uuid.uuid4())
            
        data[array_key].append(new_item)
        
        # Write back to file
        return self.write_json_file(filename, data)
    
    def update_json_item(self, filename: str, array_key: str, item_id: str, updated_item: Dict) -> bool:
        """Update a specific item in a JSON array by id"""
        data = self.read_json_file(filename)
        
        if array_key not in data:
            return False
            
        # Find and update the item
        for i, item in enumerate(data[array_key]):
            if item.get("id") == item_id:
                updated_item["id"] = item_id  # Ensure ID is preserved
                data[array_key][i] = updated_item
                return self.write_json_file(filename, data)
                
        return False
    
    def delete_json_item(self, filename: str, array_key: str, item_id: str) -> bool:
        """Delete a specific item from a JSON array by id"""
        data = self.read_json_file(filename)
        
        if array_key not in data:
            return False
            
        # Find and remove the item
        initial_length = len(data[array_key])
        data[array_key] = [item for item in data[array_key] if item.get("id") != item_id]
        
        if len(data[array_key]) < initial_length:
            return self.write_json_file(filename, data)
            
        return False
    
    def get_json_item_by_id(self, filename: str, array_key: str, item_id: str) -> Optional[Dict]:
        """Get a specific item from a JSON array by id"""
        data = self.read_json_file(filename)
        
        if array_key not in data:
            return None
            
        for item in data[array_key]:
            if item.get("id") == item_id:
                return item
                
        return None
    
    def get_all_json_items(self, filename: str, array_key: str) -> List[Dict]:
        """Get all items from a JSON array"""
        data = self.read_json_file(filename)
        
        if array_key not in data:
            return []
            
        return data[array_key]
