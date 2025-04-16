from websockets.asyncio.server import serve
from logging import info, warning
import base64
import json
import asyncio

from .crypto import decrypt_data, encrypt_data
from .users import get_users
from . import get_from_env
from . import commands

async def init() -> None:
    # Getting info from environment
    addr = get_from_env.get_addr()
    info(f"Using address: {addr}")

    port = get_from_env.get_port()
    info(f"Using port: {port}")

    # Start command reader task
    asyncio.create_task(commands.start_command_reader())

    print("Server starting! Type 'help' for available commands.")

    # Start serving
    await start_websocket_server(addr, port)

async def handler(websocket) -> None:
    try:
        async for message in websocket:
            info(f"Received msg: {message}")
            response = await process(message)
            await websocket.send(response)
            info(f"Sent msg: {response}")
    except Exception as e:
        warning(f"Handler error: {repr(e)}")


async def start_websocket_server(addr: str, port: int) -> None:
    async with serve(handler, addr, port) as server:
        await server.serve_forever()


async def process(message: str) -> str:
    users = get_users()

    try:
        # Decode base64 message and parse JSON
        json_request = base64.b64decode(message).decode("utf-8")
        request = json.loads(json_request)
        info(f"Request: {request}")

        # Validate UUID
        if "uuid" not in request or request["uuid"] not in users:
            return "Invalid UUID"

        # Decrypt incoming data with server's private key
        encrypted_names = base64.b64decode(request["raw"])
        server_private_key = base64.b64decode(users[request["uuid"]]["secret"])

        decrypted_names = decrypt_data(server_private_key, encrypted_names)

        # Process decrypted names
        result = []
        for encoded_name in decrypted_names.split("|"):
            if encoded_name:  # Check for empty strings
                import sys
                from os import path
                sys.path.append(path.join(path.dirname(__file__), '..'))
                from services import VersionFinder

                finder = VersionFinder()

                name = base64.b64decode(encoded_name).decode("utf-8")

                res = finder.find_version(name)

                result.append(res)

        # Prepare JSON response
        response_json = json.dumps({"status": "success", "software": result})

        # Encrypt response with client's public key
        client_public_key = base64.b64decode(users[request["uuid"]]["public_key"])
        encrypted_response = encrypt_data(client_public_key, response_json.encode("utf-8"))

        # Return base64-encoded encrypted response
        return base64.b64encode(encrypted_response).decode("utf-8")

    except json.JSONDecodeError:
        return "Bad JSON in request"
    except KeyError:
        return "Bad Key in JSON"
    except ValueError as e:
        if "padding" in str(e):
            return "Bad Base64 in request"
        return f"Processing error: {str(e)}"
    except Exception as e:
        return f"Error: {repr(e)}"
