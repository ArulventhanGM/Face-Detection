import json
import os

# Sample metadata dictionary - in production, this could be loaded from a database
PEOPLE_METADATA = {
    "john_doe": {
        "name": "John Doe",
        "email": "john.doe@company.com",
        "role": "Software Engineer",
        "department": "Engineering",
        "employee_id": "EMP001",
        "phone": "+1-555-0123"
    },
    "jane_smith": {
        "name": "Jane Smith",
        "email": "jane.smith@company.com",
        "role": "Product Manager",
        "department": "Product",
        "employee_id": "EMP002",
        "phone": "+1-555-0124"
    },
    "bob_johnson": {
        "name": "Bob Johnson",
        "email": "bob.johnson@company.com",
        "role": "Senior Developer",
        "department": "Engineering",
        "employee_id": "EMP003",
        "phone": "+1-555-0125"
    },
    "alice_brown": {
        "name": "Alice Brown",
        "email": "alice.brown@company.com",
        "role": "UX Designer",
        "department": "Design",
        "employee_id": "EMP004",
        "phone": "+1-555-0126"
    },
    "mike_wilson": {
        "name": "Mike Wilson",
        "email": "mike.wilson@company.com",
        "role": "Data Scientist",
        "department": "Data Science",
        "employee_id": "EMP005",
        "phone": "+1-555-0127"
    }
}

def get_person_metadata(name):
    """
    Fetch metadata for a recognized person.
    
    Args:
        name (str): The name of the person (usually filename without extension)
        
    Returns:
        dict: Person's metadata or None if not found
    """
    # Convert name to lowercase and replace spaces with underscores for consistent lookup
    lookup_name = name.lower().replace(' ', '_')
    
    return PEOPLE_METADATA.get(lookup_name, None)

def load_metadata_from_file(file_path):
    """
    Load metadata from a JSON file.
    
    Args:
        file_path (str): Path to JSON file containing metadata
        
    Returns:
        dict: Loaded metadata
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_metadata_to_file(metadata, file_path):
    """
    Save metadata to a JSON file.
    
    Args:
        metadata (dict): Metadata dictionary to save
        file_path (str): Path to save the JSON file
    """
    with open(file_path, 'w') as f:
        json.dump(metadata, f, indent=2)

def add_person_metadata(name, metadata):
    """
    Add or update metadata for a person.
    
    Args:
        name (str): Person's name
        metadata (dict): Person's metadata
    """
    lookup_name = name.lower().replace(' ', '_')
    PEOPLE_METADATA[lookup_name] = metadata

def get_all_people():
    """
    Get all people in the metadata.
    
    Returns:
        dict: All people metadata
    """
    return PEOPLE_METADATA
