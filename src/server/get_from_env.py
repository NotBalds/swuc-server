import os
import logging

def get_addr() -> str:
    addr = os.getenv("SWUC_SERVER_ADDR")
    if not addr:
        return "localhost"
    else:
        return addr


def get_port() -> int:
    port = os.getenv("SWUC_SERVER_PORT")
    try:
        port = int(port) if port is not None else 8765
    except ValueError:
        logging.warning(f"Incorrect port value: '{port}', using default 8765")
        port = 8765

    return port
