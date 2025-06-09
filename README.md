# AD-Remoto (WIP)

A simple Python server for Active Directory (AD) remote operations.

## Overview
This project provides a lightweight server to interact with Active Directory using Python. It is designed for internal use within a corporate network and can be configured to match your AD environment.

## Features
- Search, rename, unlock and change the password of the users.
- Customizable host, port, and AD search base
- Configuration via JSON file
- Modular codebase for easy extension

## Example Configuration
See `config.json` for a sample configuration:
```json
{
    "HOST": "0.0.0.0",
    "PORT": 7777,
    "fqdn": "HOST.EXAMPLE.CORP",
    "domain": "EXAMPLE.CORP",
    "search_base": "DC=EXAMPLE,DC=CORP"
}
```

## Getting Started
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/AD-Remoto.git
   cd AD-Remoto
   ```
2. Install dependencies (if any):
   ```sh
   pip install -r requirements.txt
   ```
3. Edit `config.json` as needed.
4. Run the server:
   ```sh
   python server.py
   ```

## Files
- `server.py` - Main server script
- `client.py` - Client script for testing
- `ad_helper.py` - Helper functions for AD operations
- `log.py` - Logging utilities
- `config.json` - Server configuration

## License
MIT License
