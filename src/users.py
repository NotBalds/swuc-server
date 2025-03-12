import json
import os
from logging import warning

def get_users() -> dict:
    """
    Load users from JSON file.
    """
    try:
        if not os.path.exists("users.json"):
            with open("users.json", "w") as f:
                json.dump({}, f)

        with open("users.json", "r") as users_file:
            return json.load(users_file)
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        warning(f"Error loading users: {repr(e)}")
        return {}

def save_users(users: dict) -> None:
    """Save users to JSON file"""
    try:
        with open("users.json", "w") as users_file:
            json.dump(users, users_file, indent=2)
    except Exception as e:
        warning(f"Error saving users: {repr(e)}")