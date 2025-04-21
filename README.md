# Software Updates Checker Server

A secure WebSocket server for checking software versions using external search services and AI analysis.

## Features

- 🔒 End-to-end encryption using ECC (Elliptic Curve Cryptography)
- 🌐 WebSocket communication protocol
- 🔑 User management system with UUID-based authentication
- 🔍 Integrated with Yandex Search, Safe Browsing, and GPT APIs
- 📁 Environment-based configuration
- 📄 JSON configuration storage for users

## Installation

1. Clone the repository:
```bash
git clone https://github.com/NotBalds/swuc-server.git
cd swuc-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (create `.env` file):
```env
SWUC_SERVER_ADDR=localhost
SWUC_SERVER_PORT=8765
YANDEX_FOLDER_ID=your_folder_id
YANDEX_SEARCH_API_KEY=your_search_key
YANDEX_SAFE_BROWSING_API_KEY=your_safety_key
YANDEX_GPT_API_KEY=your_gpt_key
```

## Usage

### Starting the Server
```bash
python src/main.py
```

### Server Commands
Once the server is running, use these commands in the console:
```
help       - Show available commands
new        - Create new user (generates UUID and keys)
list       - List registered users
del <uuid> - Delete a user
exit       - Shutdown server
```

### Client Configuration
When creating a new user (`new` command), the server:
1. Generates UUID for the client
2. Creates `users/<uuid>.json` with connection details
3. Stores server-side configuration in `users.json`

Client configuration includes:
- WebSocket URL
- Client secret key
- Server public key
- UUID identifier

## API Workflow

1. **Client Request**:
   - Encrypts software name list using server's public key
   - Base64 encodes and sends via WebSocket

2. **Server Processing**:
   1. Validates UUID
   2. Decrypts request using client-specific private key
   3. Performs web search and content analysis
   4. Encrypts response with client's public key
   5. Returns base64-encoded result

3. **Response Format**:
```json
[
  {
    "error": null,
    "metadata": {
      "analysis_time": "2023-12-20T00:00:00Z",
      "urls_analyzed": 5,
      "urls_searched": 5
    },
    "name": "python",
    "sources": [
      "https://www.python.org/downloads/",
      "https://www.python.org/downloads/windows/",
      "https://www.python.org/?downloads=",
      "https://python.en.uptodown.com/windows/download",
      "https://rdil.github.io/pythondotorg-downloads-page-prototype/"
    ],
    "version": "3.13.3"
  }
]
```

## Security

- 🔐 ECC Encryption using `eciespy` library
- 🔑 Unique key pair per user
- 🛡️ Base64 encoding for all network communications

## Dependencies

- Python 3.8+
- websockets
- ecies
- python-dotenv
- yandex APIs (search, safe browsing, GPT)

## Configuration Files


## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/fooBar`)
3. Commit changes (`git commit -am 'Add some fooBar'`)
4. Push to branch (`git push origin feature/fooBar`)
5. Create new Pull Request

## License

[MIT License](https://github.com/NotBalds/swuc-server/blob/master/LICENSE)
