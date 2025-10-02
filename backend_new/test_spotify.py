"""Test Spotify API connection"""

from services.spotify_client import spotify_client

def test_connection():
    print("🎵 Testing Spotify API...")
    
    try:
        results = spotify_client.search_track("Happy Pharrell Williams", limit=1)
        
        if results:
            track = spotify_client.format_track(results[0])
            print(f"✅ Connected! Test: {track['name']} by {track['artist']}")
            return True
        else:
            print("⚠️ Connected but no results")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()