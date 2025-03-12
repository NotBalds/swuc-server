import logging
from dotenv import load_dotenv
from logging import info, warning
import asyncio
import os

from server import start_websocket_server
from commands import start_command_reader

# Initialization
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

async def init() -> None:
    """Initialize and start the server with command interface"""
    # Getting info from environment
    addr = os.getenv("SWUC_SERVER_ADDR", "0.0.0.0")
    info(f"Using address: {addr}")

    port = os.getenv("SWUC_SERVER_PORT")
    try:
        port = int(port) if port is not None else 8765
    except ValueError:
        warning(f"Incorrect port value: '{port}', using default 8765")
        port = 8765

    info(f"Using port: {port}")

    # Start command reader task
    asyncio.create_task(start_command_reader())

    print("\nServer started! Type 'help' for available commands.")

    # Start serving
    await start_websocket_server(addr, port)

if __name__ == "__main__":
    try:
        asyncio.run(init())
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        warning(f"Server error: {repr(e)}")