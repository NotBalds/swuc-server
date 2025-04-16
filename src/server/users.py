import json
import os
from logging import warning

def get_users() -> dict:
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
    try:
        with open("users.json", "w") as users_file:
            json.dump(users, users_file, indent=2)
    except Exception as e:
        warning(f"Error saving users: {repr(e)}")

def save_user(uuid: str, user: dict) -> None:
    if not os.path.exists("users"):
        os.makedirs("users")
    try:
        with open(f"users/{uuid}.json", "w") as users_file:
            json.dump(user, users_file, indent=2)
    except Exception as e:
        warning(f"Error saving user: {repr(e)}")
