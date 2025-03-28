#!/usr/bin/env python3
"""
Main entry point for the twscrape_api package.
"""

import sys
import asyncio
from .cli import main as cli_main
from .api import run_server


def print_usage():
    """Print usage information."""
    print("Usage: python -m twscrape_api [command] [args...]")
    print("\nCommands:")
    print("  cli <twitter_url_or_username> [limit] [output_file]")
    print("      Fetch tweets from a Twitter account and save to a JSON file")
    print("  api [host] [port]")
    print("      Start the API server")
    print("  help")
    print("      Show this help message")
    print("\nExamples:")
    print("  python -m twscrape_api cli elonmusk 5")
    print("  python -m twscrape_api api 127.0.0.1 8080")


def main():
    """Main entry point function."""
    if len(sys.argv) < 2 or sys.argv[1] == "help":
        print_usage()
        return 0
    
    command = sys.argv[1]
    
    if command == "cli":
        # Remove the 'cli' argument and pass the rest to the CLI
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        asyncio.run(cli_main())
        return 0
    
    elif command == "api":
        # Start the API server
        host = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        run_server(host, port)
        return 0
    
    else:
        print(f"Unknown command: {command}")
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
