#!/usr/bin/env python3
"""
Test script to verify Spotify API connection
"""
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

def test_spotify_connection():
    """Test if Spotify API credentials work"""
    
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    
    print(f"Client ID: {client_id[:10]}..." if client_id else "Client ID: None")
    print(f"Client Secret: {client_secret[:10]}..." if client_secret else "Client Secret: None")
    
    if not client_id or not client_secret:
        print("❌ ERROR: Spotify credentials not found in .env file")
        return False
    
    try:
        # Test connection
        spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id, 
                client_secret=client_secret
            )
        )
        
        # Test with a simple search
        print("Testing Spotify API connection...")
        results = spotify.search(q='test', type='track', limit=1)
        
        if results and results['tracks']['items']:
            print("✅ SUCCESS: Spotify API connection works!")
            print(f"Test track: {results['tracks']['items'][0]['name']}")
            return True
        else:
            print("❌ ERROR: No results from Spotify search")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to Spotify API: {e}")
        return False

def test_recommendations():
    """Test Spotify recommendations with valid genres"""
    
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    
    try:
        spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id, 
                client_secret=client_secret
            )
        )
        
        # Test recommendations with simple, common genres
        print("Testing recommendations...")
        recommendations = spotify.recommendations(
            seed_genres=['pop'], 
            limit=5
        )
        
        if recommendations and recommendations['tracks']:
            print(f"✅ SUCCESS: Got {len(recommendations['tracks'])} recommendations")
            for track in recommendations['tracks'][:3]:
                print(f"  - {track['name']} by {track['artists'][0]['name']}")
            return True
        else:
            print("❌ ERROR: No recommendations returned")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to get recommendations: {e}")
        return False

if __name__ == "__main__":
    print("=== Spotify API Test ===")
    
    connection_ok = test_spotify_connection()
    if connection_ok:
        test_recommendations()
    
    print("\n=== Test Complete ===")
