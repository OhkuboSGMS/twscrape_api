#!/usr/bin/env python3
"""
Entry point script for the twscrape_api package.
"""

import sys
from src.twscrape_api.__main__ import print_usage

if __name__ == "__main__":
    # Import the main module and run it
    try:
        from src.twscrape_api.__main__ import main
        sys.exit(main())
    except ImportError:
        print("Error: Could not import the twscrape_api package.")
        print("Make sure you have installed the package correctly.")
        print_usage()
        sys.exit(1)
