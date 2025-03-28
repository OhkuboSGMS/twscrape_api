#!/usr/bin/env python3
"""
Command-line interface for fetching tweets from Twitter.
"""

import asyncio
import sys
import argparse
from typing import Optional, List
from .core import (
    extract_username_from_url, 
    fetch_tweets, 
    save_tweets_to_json,
    exclude_retweets,
    exclude_pinned_tweets,
    only_with_media,
    only_with_links,
    TweetFilterFunc
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Fetch tweets from a Twitter account")
    
    parser.add_argument(
        "twitter_url_or_username",
        help="Twitter username or URL"
    )
    
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=10,
        help="Maximum number of tweets to fetch (default: 10)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: {username}_tweets.json)"
    )
    
    parser.add_argument(
        "--db-path",
        default="./accounts.db",
        help="Path to the accounts database (default: ./accounts.db)"
    )
    
    # Filter options
    parser.add_argument(
        "--include-retweets",
        action="store_true",
        help="Include retweets (default: exclude retweets)"
    )
    
    parser.add_argument(
        "--exclude-pinned",
        action="store_true",
        help="Exclude pinned tweets"
    )
    
    parser.add_argument(
        "--only-media",
        action="store_true",
        help="Include only tweets with media (photos, videos, or animated GIFs)"
    )
    
    parser.add_argument(
        "--only-links",
        action="store_true",
        help="Include only tweets with links"
    )
    
    return parser.parse_args()


async def main():
    """Main function to process command line arguments and fetch tweets."""
    # Parse command line arguments
    args = parse_args()
    
    # Check if input is a URL or a username
    if args.twitter_url_or_username.startswith("http") or "twitter.com" in args.twitter_url_or_username or "x.com" in args.twitter_url_or_username:
        username = extract_username_from_url(args.twitter_url_or_username)
        if not username:
            print(f"Could not extract username from URL: {args.twitter_url_or_username}")
            return
    else:
        # Assume input is a username
        username = args.twitter_url_or_username
    
    # Set up filters
    filters: List[TweetFilterFunc] = []
    
    if not args.include_retweets:
        filters.append(exclude_retweets)
    
    if args.exclude_pinned:
        filters.append(exclude_pinned_tweets)
    
    if args.only_media:
        filters.append(only_with_media)
    
    if args.only_links:
        filters.append(only_with_links)
    
    # Print filter information
    filter_descriptions = []
    if not args.include_retweets:
        filter_descriptions.append("excluding retweets")
    if args.exclude_pinned:
        filter_descriptions.append("excluding pinned tweets")
    if args.only_media:
        filter_descriptions.append("only with media")
    if args.only_links:
        filter_descriptions.append("only with links")
    
    filter_text = ", ".join(filter_descriptions) if filter_descriptions else "no filters"
    print(f"Fetching up to {args.limit} tweets for user: {username} ({filter_text})")
    
    # Fetch tweets
    tweets = await fetch_tweets(
        username=username, 
        limit=args.limit, 
        db_path=args.db_path,
        filter_func=filters if filters else None
    )
    
    # Display results
    if not tweets:
        print(f"No tweets found for user: {username}")
        return
        
    print(f"\nFound {len(tweets)} tweets:")
    for i, tweet in enumerate(tweets, 1):
        print(f"\n--- Tweet {i} ---")
        print(f"Date: {tweet.date}")
        print(f"Text: {tweet.rawContent}")
        print(f"Likes: {tweet.likeCount}")
        print(f"URL: https://twitter.com/{username}/status/{tweet.id}")
        
        # Display links if present
        if tweet.links:
            print(f"Links:")
            for link in tweet.links:
                print(f"  - {link.url}")
    
    # Save tweets to JSON file
    json_file = save_tweets_to_json(tweets, username, args.output)
    print(f"\nTweets saved to {json_file}")


if __name__ == "__main__":
    asyncio.run(main())
