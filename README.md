# Twitter Tweet Fetcher

A tool to fetch the latest tweets (excluding retweets) from a specific X/Twitter account URL using the `twscrape` library.

## Features

- Fetch tweets from a Twitter account by username or URL
- Flexible tweet filtering (exclude retweets, exclude pinned tweets, only media tweets, only tweets with links)
- Extract links from tweets
- Save tweets to JSON file
- API endpoints for programmatic access

## Project Structure

```
twscrape_api/
│── src/
│   └── twscrape_api/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core.py
│       ├── cli.py
│       └── api.py
│── scripts/
│   └── test_api.ps1
│── accounts.db
│── pyproject.toml
│── twscrape_api_run.py
└── README.md
```

## Installation

### For Development

1. Clone the repository:

```bash
git clone https://github.com/OhkuboSGMS/twscrape_api.git
cd twscrape_api
```

2. Create a virtual environment:

```bash
uv venv
```

3. Initialize the project:

```bash
uv init
```

4. Install dependencies:

```bash
uv add twscrape fastapi uvicorn
```

### For Usage

1. Clone or download the repository:

```bash
git clone https://github.com/OhkuboSGMS/twscrape_api.git
cd twscrape_api
```

2. Install the package in development mode:

```bash
pip install -e .
```

Or install directly from the repository:

```bash
pip install git+https://github.com/OhkuboSGMS/twscrape_api.git
```

### Dependencies

- **twscrape**: For fetching tweets from Twitter
- **fastapi**: For the API implementation
- **uvicorn**: For running the API server

## Authentication

This tool requires authentication with Twitter. You need to have a `accounts.db` file with valid Twitter credentials. The `accounts.db` file is used by the `twscrape` library to authenticate with Twitter.

## Command-line Usage

```bash
# Using the module
python -m twscrape_api cli <twitter_url_or_username> [options]
```

### Arguments and Options

- `twitter_url_or_username`: Twitter username or URL (required)
- `-l, --limit`: Maximum number of tweets to fetch (optional, default: 10)
- `-o, --output`: Output file path (optional, default: `{username}_tweets.json`)
- `--db-path`: Path to the accounts database (optional, default: `./accounts.db`)

### Filter Options

- `--include-retweets`: Include retweets (default: exclude retweets)
- `--exclude-pinned`: Exclude pinned tweets
- `--only-media`: Include only tweets with media (photos, videos, or animated GIFs)
- `--only-links`: Include only tweets with links

### Examples

```bash
# Fetch 5 tweets from Elon Musk's account
python -m twscrape_api cli https://twitter.com/elonmusk -l 5

# Fetch 10 tweets from Elon Musk's account using just the username
python -m twscrape_api cli elonmusk

# Fetch 20 tweets from Elon Musk's account and save to a custom file
python -m twscrape_api cli elonmusk -l 20 -o elon_tweets.json

# Fetch only tweets with media
python -m twscrape_api cli elonmusk --only-media

# Fetch tweets excluding retweets and pinned tweets
python -m twscrape_api cli elonmusk --exclude-pinned
```

## API Usage

The API provides endpoints to fetch tweets programmatically.

### Start the API server

```bash
# Using the module
python -m twscrape_api api [host] [port]
```

This will start the API server at http://localhost:8000 by default.

### PowerShell Test Script

A PowerShell script is provided to test the API:

```powershell
# Run the test script
.\scripts\test_api.ps1
```

This script will:
1. Start the API server in a new PowerShell window
2. Wait for the server to be ready
3. Send requests to both API endpoints using curl
4. Display the formatted results

### API Endpoints

#### GET /tweets

Fetch tweets from a Twitter account.

**Parameters:**

- `username_or_url`: Twitter username or URL (required)
- `limit`: Maximum number of tweets to fetch (optional, default: 10, max: 100)
- `include_retweets`: Include retweets (optional, default: false)
- `exclude_pinned`: Exclude pinned tweets (optional, default: false)
- `only_media`: Include only tweets with media (optional, default: false)
- `only_links`: Include only tweets with links (optional, default: false)
- `db_path`: Path to the accounts database (optional, default: ./accounts.db)

**Example:**

```
http://localhost:8000/tweets?username_or_url=elonmusk&limit=5&only_media=true
```

**Response:**

```json
{
  "tweets": [
    {
      "id": 1234567890,
      "id_str": "1234567890",
      "url": "https://twitter.com/elonmusk/status/1234567890",
      "date": "2025-03-28 04:57:16+00:00",
      "username": "elonmusk",
      "displayname": "Elon Musk",
      "rawContent": "Tweet content here",
      "likeCount": 12345,
      "retweetCount": 678,
      "replyCount": 910,
      "links": [
        {
          "url": "https://example.com",
          "text": "example.com",
          "tcourl": "https://t.co/abc123"
        }
      ]
    }
  ],
  "count": 1
}
```

#### GET /tweets/json

Fetch tweets from a Twitter account and return the raw JSON.

**Parameters:**

- `username_or_url`: Twitter username or URL (required)
- `limit`: Maximum number of tweets to fetch (optional, default: 10, max: 100)
- `include_retweets`: Include retweets (optional, default: false)
- `exclude_pinned`: Exclude pinned tweets (optional, default: false)
- `only_media`: Include only tweets with media (optional, default: false)
- `only_links`: Include only tweets with links (optional, default: false)
- `db_path`: Path to the accounts database (optional, default: ./accounts.db)

**Example:**

```
http://localhost:8000/tweets/json?username_or_url=elonmusk&limit=5&only_links=true
```

**Response:**

Raw JSON data of the tweets.

### API Documentation

The API documentation is available at http://localhost:8000/docs when the API server is running.

## Development

### Package Structure

- `__init__.py`: Package initialization and version information
- `__main__.py`: Main entry point for the package
- `core.py`: Core functionality for fetching tweets
- `cli.py`: Command-line interface
- `api.py`: FastAPI implementation

## License

MIT
