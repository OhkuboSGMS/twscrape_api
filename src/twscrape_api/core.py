"""
Core functionality for fetching tweets from Twitter.
"""

from twscrape import API
import asyncio
import json
import re
from typing import Optional, List, Dict, Any
from twscrape.models import Tweet


def extract_username_from_url(url: str) -> Optional[str]:
    """
    Extract username from various Twitter/X URL formats.
    
    Args:
        url: The Twitter/X URL
        
    Returns:
        The extracted username or None if no match found
    """
    patterns = [
        r"(?:https?://)?(?:www\.)?twitter\.com/([^/\s?]+)",
        r"(?:https?://)?(?:www\.)?x\.com/([^/\s?]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


from typing import Optional, List, Dict, Any, Callable, Union

# Define a type for tweet filter functions
TweetFilterFunc = Callable[[Tweet], bool]
TweetMapFunc = Callable[[Tweet], Any]

def exclude_retweets(tweet: Tweet) -> bool:
    """
    Filter function to exclude retweets.
    
    Args:
        tweet: The tweet to check
        
    Returns:
        True if the tweet should be included (not a retweet), False otherwise
    """
    return tweet.retweetedTweet is None


def exclude_pinned_tweets(tweet: Tweet) -> bool:
    """
    Filter function to exclude pinned tweets.
    
    Args:
        tweet: The tweet to check
        
    Returns:
        True if the tweet should be included (not pinned), False otherwise
    """
    # Check if the tweet ID is in the user's pinned tweets list
    if hasattr(tweet.user, 'pinnedIds') and tweet.id in tweet.user.pinnedIds:
        return False
    return True


def only_with_media(tweet: Tweet) -> bool:
    """
    Filter function to include only tweets with media (photos, videos, or animated GIFs).
    
    Args:
        tweet: The tweet to check
        
    Returns:
        True if the tweet should be included (has media), False otherwise
    """
    if not hasattr(tweet, 'media'):
        return False
    
    has_photos = hasattr(tweet.media, 'photos') and len(tweet.media.photos) > 0
    has_videos = hasattr(tweet.media, 'videos') and len(tweet.media.videos) > 0
    has_animated = hasattr(tweet.media, 'animated') and len(tweet.media.animated) > 0
    
    return has_photos or has_videos or has_animated


def only_with_links(tweet: Tweet) -> bool:
    """
    Filter function to include only tweets with links.
    
    Args:
        tweet: The tweet to check
        
    Returns:
        True if the tweet should be included (has links), False otherwise
    """
    return hasattr(tweet, 'links') and len(tweet.links) > 0


def combine_filters(*filters: TweetFilterFunc) -> TweetFilterFunc:
    """
    Combine multiple filter functions with AND logic.
    
    Args:
        *filters: Filter functions to combine
        
    Returns:
        A filter function that returns True only if all filters return True
    """
    def combined_filter(tweet: Tweet) -> bool:
        return all(f(tweet) for f in filters)
    
    return combined_filter

def combine_map_functions(*map_funcs: TweetMapFunc) -> TweetMapFunc:
    """
    Combine multiple map functions with AND logic.

    Args:
        *map_funcs: Map functions to combine

    Returns:
        A map function that applies all map functions in order
    """
    def combined_map(tweet: Tweet) -> Any:
        _tweet = tweet
        for func in map_funcs:
            _tweet = func(_tweet)
        return _tweet

    return combined_map

async def fetch_tweets(
    username: str, 
    limit: int = 10, 
    db_path: str = "./accounts.db",
    filter_func: Optional[Union[TweetFilterFunc, List[TweetFilterFunc]]] = None,
    map_func: Optional[TweetMapFunc | list[TweetMapFunc]] = None
) -> List[Tweet]:
    """
    Fetch tweets from a specific username with customizable filtering.
    
    Args:
        username: The Twitter/X username
        limit: Maximum number of tweets to fetch
        db_path: Path to the accounts database
        filter_func: A function or list of functions to filter tweets
                    Each function should take a Tweet object and return a boolean
                    (True to include the tweet, False to exclude it)
        map_func: A function or list of functions to map tweets
        
    Returns:
        List of filtered tweets
    """
    # Initialize the API with the accounts database
    api = API(db_path)
    await api.pool.login_all()
    
    try:
        # First, get the user by login (username)
        user = await api.user_by_login(username)
        if not user:
            print(f"User not found: {username}")
            return []
        
        # Set up the filter function
        if filter_func is None:
            # Default filter: exclude retweets
            filter_func = exclude_retweets
        elif isinstance(filter_func, list):
            # Combine multiple filters
            filter_func = combine_filters(*filter_func)

        # Set up the map function
        if map_func is None:
            # Default map function: no mapping
            map_func = lambda x: x
        elif isinstance(map_func, list):
            # Combine multiple map functions
            map_func = combine_map_functions(*map_func)
        # Fetch tweets using the user ID with filtering
        tweets = []
        fetch_limit = limit * 3  # Fetch more to account for filtering
        
        async for tweet in api.user_tweets(user.id, limit=fetch_limit):
            if filter_func(tweet):
                tweets.append(map_func(tweet))
                if len(tweets) >= limit:
                    break
        
        return tweets
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return []


def save_tweets_to_json(tweets: List[Tweet], username: str, output_file: str = None) -> str:
    """
    Save tweets to a JSON file.
    
    Args:
        tweets: List of tweets to save
        username: Twitter username
        output_file: Output file path (optional)
        
    Returns:
        Path to the saved JSON file
    """
    if not output_file:
        output_file = f"{username}_tweets.json"
    
    # Convert tweets to JSON
    tweets_data = [json.loads(tweet.json()) for tweet in tweets]
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tweets_data, f, ensure_ascii=False, indent=2)
    
    return output_file


def convert_tweet_to_response(tweet: Tweet) -> Dict[str, Any]:
    """
    Convert a Tweet object to a response format.
    
    Args:
        tweet: Tweet object
        
    Returns:
        Dictionary with tweet data
    """
    links = []
    if hasattr(tweet, 'links') and tweet.links:
        for link in tweet.links:
            links.append({
                "url": link.url,
                "text": link.text,
                "tcourl": link.tcourl
            })
    
    return {
        "id": tweet.id,
        "id_str": tweet.id_str,
        "url": tweet.url,
        "date": str(tweet.date),
        "username": tweet.user.username,
        "displayname": tweet.user.displayname,
        "rawContent": tweet.rawContent,
        "likeCount": tweet.likeCount,
        "retweetCount": tweet.retweetCount,
        "replyCount": tweet.replyCount,
        "links": links
    }
