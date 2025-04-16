import asyncio
import sys
import uuid

from .users import get_users, save_users, save_user
from .crypto import generate_key_pair


async def start_command_reader():
    while True:
        # This creates a future that will be set when stdin has data
        line = await asyncio.to_thread(sys.stdin.readline)
        line = line.strip()

        if line:
            await process_command(line)


async def process_command(command: str) -> None:
    cmd_parts = command.split()
    if not cmd_parts:
        return

    cmd = cmd_parts[0].lower()

    if cmd == "help":
        print("Available commands:")
        print("  new - Create new user")
        print("  list - List all registered users")
        print("  del <uuid> - Delete a user by UUID")
        print("  exit - Exit the server")
        print("  help - Show this help message")

    elif cmd == "new":
        if len(cmd_parts) != 1:
            print("Usage: new")
            return

        await generate_user_keys()

    elif cmd == "list":
        users = get_users()
        if not users:
            print("No users registered.")
            return

        print("Registered users:")
        for user_id, user_data in users.items():
            print(f"  UUID: {user_id}")

    elif cmd == "del":
        if len(cmd_parts) < 2:
            print("Usage: del <uuid>")
            return

        user_id = cmd_parts[1]
        users = get_users()
        if user_id in users:
            del users[user_id]
            save_users(users)
            print(f"User {user_id} deleted.")
        else:
            print(f"User {user_id} not found.")

    elif cmd == "exit":
        print("Shutting down server...")
        # Signal to stop the server
        asyncio.get_event_loop().stop()
        sys.exit()

    else:
        print(f"Unknown command: {cmd}")
        print("Type 'help' for available commands.")


async def generate_user_keys() -> None:
    import get_from_env

    # Generate server keys
    server_secret, server_public = generate_key_pair()

    # Generate client keys
    client_secret, client_public = generate_key_pair()

    # Generate UUID for the user
    user_id = str(uuid.uuid4())
    server_conf = {
        "secret": server_secret,
        "public_key": client_public
    }
    user_conf = {
        "url": f"ws://{get_from_env.get_addr()}:{get_from_env.get_port()}",
        "uuid": user_id,
        "secret": client_secret,
        "public": server_public
    }

    # Save to users.json
    users = get_users()
    users[user_id] = server_conf
    save_users(users)

    save_user(user_id, user_conf)

    print(f"New user UUID: {user_id}")
