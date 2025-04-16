import logging
from dotenv import load_dotenv
from logging import warning
import asyncio

import server

# Initialization
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

if __name__ == "__main__":
    try:
        asyncio.run(server.init())
    except KeyboardInterrupt:
        print("Server stopped by user.")
    except Exception as e:
        warning(f"Server error: {repr(e)}")
