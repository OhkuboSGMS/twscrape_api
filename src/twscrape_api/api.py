#!/usr/bin/env python3
"""
FastAPI implementation for the tweet fetching functionality.
Provides API endpoints to fetch tweets from a Twitter account.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import uvicorn
import asyncio
from .core import extract_username_from_url, fetch_tweets, convert_tweet_to_response

# Initialize FastAPI app
app = FastAPI(
    title="Twitter Tweets API",
    description="API to fetch tweets from a Twitter account using twscrape",
    version="1.0.0"
)

# Define response models
class Link(BaseModel):
    url: str
    text: Optional[str] = None
    tcourl: Optional[str] = None

class TweetResponse(BaseModel):
    id: int
    id_str: str
    url: str
    date: str
    username: str
    displayname: str
    rawContent: str
    likeCount: int
    retweetCount: int
    replyCount: int
    links: List[Link] = Field(default_factory=list)

class TweetsResponse(BaseModel):
    tweets: List[TweetResponse]
    count: int

# API endpoints
@app.get("/tweets", response_model=TweetsResponse, tags=["tweets"])
async def get_tweets(
    username_or_url: str = Query(..., description="Twitter username or URL"),
    limit: int = Query(10, description="Maximum number of tweets to fetch", ge=1, le=100),
    include_retweets: bool = Query(False, description="Include retweets"),
    exclude_pinned: bool = Query(False, description="Exclude pinned tweets"),
    only_media: bool = Query(False, description="Include only tweets with media"),
    only_links: bool = Query(False, description="Include only tweets with links"),
    db_path: str = Query("./accounts.db", description="Path to the accounts database")
):
    """
    Fetch tweets from a Twitter account with customizable filtering.
    
    - **username_or_url**: Twitter username or URL
    - **limit**: Maximum number of tweets to fetch (1-100)
    - **include_retweets**: Include retweets (default: False)
    - **exclude_pinned**: Exclude pinned tweets (default: False)
    - **only_media**: Include only tweets with media (default: False)
    - **only_links**: Include only tweets with links (default: False)
    - **db_path**: Path to the accounts database (default: ./accounts.db)
    
    Returns a list of tweets.
    """
    try:
        # Check if input is a URL or a username
        if username_or_url.startswith("http") or "twitter.com" in username_or_url or "x.com" in username_or_url:
            username = extract_username_from_url(username_or_url)
            if not username:
                raise HTTPException(status_code=400, detail=f"Could not extract username from URL: {username_or_url}")
        else:
            # Assume input is a username
            username = username_or_url
        
        # Set up filters
        filters = []
        
        if not include_retweets:
            filters.append(exclude_retweets)
        
        if exclude_pinned:
            filters.append(exclude_pinned_tweets)
        
        if only_media:
            filters.append(only_with_media)
        
        if only_links:
            filters.append(only_with_links)
        
        # Fetch tweets
        tweets = await fetch_tweets(
            username=username, 
            limit=limit, 
            db_path=db_path,
            filter_func=filters if filters else None
        )
        
        if not tweets:
            return {"tweets": [], "count": 0}
        
        # Convert tweets to response format
        tweet_responses = [convert_tweet_to_response(tweet) for tweet in tweets]
        
        return {"tweets": tweet_responses, "count": len(tweet_responses)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tweets/json", tags=["tweets"])
async def get_tweets_json(
    username_or_url: str = Query(..., description="Twitter username or URL"),
    limit: int = Query(10, description="Maximum number of tweets to fetch", ge=1, le=100),
    include_retweets: bool = Query(False, description="Include retweets"),
    exclude_pinned: bool = Query(False, description="Exclude pinned tweets"),
    only_media: bool = Query(False, description="Include only tweets with media"),
    only_links: bool = Query(False, description="Include only tweets with links"),
    db_path: str = Query("./accounts.db", description="Path to the accounts database")
):
    """
    Fetch tweets from a Twitter account with customizable filtering and return the raw JSON.
    
    - **username_or_url**: Twitter username or URL
    - **limit**: Maximum number of tweets to fetch (1-100)
    - **include_retweets**: Include retweets (default: False)
    - **exclude_pinned**: Exclude pinned tweets (default: False)
    - **only_media**: Include only tweets with media (default: False)
    - **only_links**: Include only tweets with links (default: False)
    - **db_path**: Path to the accounts database (default: ./accounts.db)
    
    Returns the raw JSON data of the tweets.
    """
    try:
        # Check if input is a URL or a username
        if username_or_url.startswith("http") or "twitter.com" in username_or_url or "x.com" in username_or_url:
            username = extract_username_from_url(username_or_url)
            if not username:
                raise HTTPException(status_code=400, detail=f"Could not extract username from URL: {username_or_url}")
        else:
            # Assume input is a username
            username = username_or_url
        
        # Set up filters
        filters = []
        
        if not include_retweets:
            filters.append(exclude_retweets)
        
        if exclude_pinned:
            filters.append(exclude_pinned_tweets)
        
        if only_media:
            filters.append(only_with_media)
        
        if only_links:
            filters.append(only_with_links)
        
        # Fetch tweets
        tweets = await fetch_tweets(
            username=username, 
            limit=limit, 
            db_path=db_path,
            filter_func=filters if filters else None
        )
        
        if not tweets:
            return []
        
        # Convert tweets to JSON
        tweets_data = [json.loads(tweet.json()) for tweet in tweets]
        
        return tweets_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint.
    
    Returns information about the API.
    """
    return {
        "name": "Twitter Tweets API",
        "description": "API to fetch tweets from a Twitter account using twscrape",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/tweets", "method": "GET", "description": "Fetch tweets from a Twitter account"},
            {"path": "/tweets/json", "method": "GET", "description": "Fetch tweets from a Twitter account and return the raw JSON"}
        ]
    }

def run_server(host="0.0.0.0", port=8000):
    """Run the API server."""
    uvicorn.run("twscrape_api.api:app", host=host, port=port, reload=True)

# Run the API server
if __name__ == "__main__":
    run_server()
