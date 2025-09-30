import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # <-- VADER import
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import requests
import json
import random

load_dotenv()

app = FastAPI()

# --- CORS (Cross-Origin Resource Sharing) ---
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Clients ---
# Spotify Client
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    raise Exception("Spotify credentials not found. Please check your .env file.")

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
    )
)

# VADER Sentiment Analyzer (fallback)
analyzer = SentimentIntensityAnalyzer()

# Enhanced song libraries for dynamic recommendations
MOOD_SONG_LIBRARIES = {
    "Very Positive": [
        {"name": "Happy", "artist": "Pharrell Williams", "search_terms": ["happy", "celebration", "joy", "upbeat"]},
        {"name": "Can't Stop the Feeling!", "artist": "Justin Timberlake", "search_terms": ["feel good", "dance", "party"]},
        {"name": "Good as Hell", "artist": "Lizzo", "search_terms": ["confidence", "empowerment", "feel good"]},
        {"name": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "search_terms": ["funk", "dance", "party"]},
        {"name": "Walking on Sunshine", "artist": "Katrina and the Waves", "search_terms": ["sunshine", "happy", "energy"]},
        {"name": "I Gotta Feeling", "artist": "The Black Eyed Peas", "search_terms": ["party", "celebration", "good times"]},
        {"name": "Don't Worry Be Happy", "artist": "Bobby McFerrin", "search_terms": ["happy", "positive", "carefree"]},
        {"name": "Best Day of My Life", "artist": "American Authors", "search_terms": ["best day", "celebration", "joy"]},
    ],
    "Positive": [
        {"name": "Good 4 U", "artist": "Olivia Rodrigo", "search_terms": ["pop", "upbeat", "energy"]},
        {"name": "Levitating", "artist": "Dua Lipa", "search_terms": ["dance", "pop", "feel good"]},
        {"name": "Sunflower", "artist": "Post Malone, Swae Lee", "search_terms": ["chill", "positive", "vibe"]},
        {"name": "Blinding Lights", "artist": "The Weeknd", "search_terms": ["synthwave", "energy", "drive"]},
        {"name": "Don't Stop Me Now", "artist": "Queen", "search_terms": ["rock", "energy", "unstoppable"]},
        {"name": "Good Vibes", "artist": "Chris Brown", "search_terms": ["good vibes", "positive", "chill"]},
        {"name": "High Hopes", "artist": "Panic! At The Disco", "search_terms": ["optimistic", "hope", "energy"]},
        {"name": "Count on Me", "artist": "Bruno Mars", "search_terms": ["friendship", "support", "positive"]},
    ],
    "Neutral": [
        {"name": "Weightless", "artist": "Marconi Union", "search_terms": ["ambient", "calm", "relaxing"]},
        {"name": "Holocene", "artist": "Bon Iver", "search_terms": ["indie", "calm", "introspective"]},
        {"name": "Clair de Lune", "artist": "Claude Debussy", "search_terms": ["classical", "peaceful", "serene"]},
        {"name": "Breathe Me", "artist": "Sia", "search_terms": ["emotional", "calm", "reflective"]},
        {"name": "The Night We Met", "artist": "Lord Huron", "search_terms": ["indie", "mellow", "nostalgic"]},
        {"name": "Skinny Love", "artist": "Bon Iver", "search_terms": ["indie", "calm", "acoustic"]},
        {"name": "Mad About You", "artist": "Sting", "search_terms": ["mellow", "romantic", "calm"]},
        {"name": "Vienna", "artist": "Billy Joel", "search_terms": ["piano", "reflective", "wisdom"]},
    ],
    "Negative": [
        {"name": "Someone Like You", "artist": "Adele", "search_terms": ["heartbreak", "emotional", "piano"]},
        {"name": "Fix You", "artist": "Coldplay", "search_terms": ["healing", "support", "emotional"]},
        {"name": "The Sound of Silence", "artist": "Disturbed", "search_terms": ["introspective", "powerful", "emotional"]},
        {"name": "Everybody Hurts", "artist": "R.E.M.", "search_terms": ["support", "understanding", "comfort"]},
        {"name": "Mad World", "artist": "Gary Jules", "search_terms": ["melancholy", "introspective", "sad"]},
        {"name": "Tears Don't Fall", "artist": "Bullet for My Valentine", "search_terms": ["emotional", "rock", "pain"]},
        {"name": "In the End", "artist": "Linkin Park", "search_terms": ["struggle", "emotional", "rock"]},
        {"name": "Heavy", "artist": "Linkin Park ft. Kiiara", "search_terms": ["burden", "emotional", "support"]},
    ],
    "Very Negative": [
        {"name": "Hurt", "artist": "Johnny Cash", "search_terms": ["pain", "regret", "deep"]},
        {"name": "Black", "artist": "Pearl Jam", "search_terms": ["grunge", "emotional", "loss"]},
        {"name": "Tears in Heaven", "artist": "Eric Clapton", "search_terms": ["loss", "grief", "acoustic"]},
        {"name": "Creep", "artist": "Radiohead", "search_terms": ["alienation", "alternative", "emotional"]},
        {"name": "Snuff", "artist": "Slipknot", "search_terms": ["loss", "emotional", "metal"]},
        {"name": "One More Day", "artist": "Diamond Rio", "search_terms": ["loss", "regret", "country"]},
        {"name": "Whiskey Lullaby", "artist": "Brad Paisley ft. Alison Krauss", "search_terms": ["tragedy", "country", "loss"]},
        {"name": "Gone Away", "artist": "The Offspring", "search_terms": ["loss", "grief", "punk rock"]},
    ]
}


# --- Pydantic Models ---
class TextInput(BaseModel):
    text: str


# --- Helper Functions ---
def analyze_mood_google(text: str) -> dict:
    """
    Analyzes text sentiment using Google Cloud Natural Language API.
    Returns detailed mood analysis with summary.
    """
    if not GOOGLE_API_KEY:
        return None
    
    try:
        url = f"https://language.googleapis.com/v1/documents:analyzeSentiment?key={GOOGLE_API_KEY}"
        
        payload = {
            "document": {
                "type": "PLAIN_TEXT",
                "content": text
            },
            "encodingType": "UTF8"
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            sentiment = result['documentSentiment']
            
            # Determine mood category
            score = sentiment['score']
            magnitude = sentiment['magnitude']
            
            if score >= 0.6:
                mood_category = "Very Positive"
                mood_description = "You're feeling fantastic and energetic!"
            elif score >= 0.2:
                mood_category = "Positive"
                mood_description = "You're in a good, upbeat mood!"
            elif score >= -0.2:
                mood_category = "Neutral"
                mood_description = "You're feeling calm and balanced."
            elif score >= -0.6:
                mood_category = "Negative"
                mood_description = "You're feeling a bit down or melancholic."
            else:
                mood_category = "Very Negative"
                mood_description = "You're going through a tough time."
            
            # Add intensity based on magnitude
            if magnitude > 0.8:
                intensity = "very intense"
            elif magnitude > 0.5:
                intensity = "moderately intense"
            else:
                intensity = "mild"
            
            return {
                "score": score,
                "magnitude": magnitude,
                "mood_category": mood_category,
                "mood_description": mood_description,
                "intensity": intensity,
                "summary": f"{mood_category} mood with {intensity} emotions. {mood_description}"
            }
        else:
            print(f"Google API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Google API failed: {e}")
        return None

def analyze_mood_vader(text: str) -> dict:
    """
    Fallback mood analysis using VADER sentiment analyzer.
    """
    sentiment_dict = analyzer.polarity_scores(text)
    score = sentiment_dict['compound']
    
    if score >= 0.5:
        mood_category = "Very Positive"
        mood_description = "You're feeling fantastic and energetic!"
    elif score >= 0.1:
        mood_category = "Positive"
        mood_description = "You're in a good, upbeat mood!"
    elif score >= -0.1:
        mood_category = "Neutral"
        mood_description = "You're feeling calm and balanced."
    elif score >= -0.5:
        mood_category = "Negative"
        mood_description = "You're feeling a bit down or melancholic."
    else:
        mood_category = "Very Negative"
        mood_description = "You're going through a tough time."
    
    return {
        "score": score,
        "magnitude": abs(score),
        "mood_category": mood_category,
        "mood_description": mood_description,
        "intensity": "moderate",
        "summary": f"{mood_category} mood. {mood_description}"
    }

def analyze_mood(text: str) -> dict:
    """
    Main mood analysis function that tries Google API first, then falls back to VADER.
    """
    # Try Google API first
    google_result = analyze_mood_google(text)
    if google_result:
        print(f"Using Google API analysis: {google_result['summary']}")
        return google_result
    
    # Fallback to VADER
    print("Falling back to VADER sentiment analysis")
    return analyze_mood_vader(text)

def search_spotify_songs(mood_analysis: dict) -> list:
    """Search for songs on Spotify based on mood analysis and search terms."""
    mood_category = mood_analysis['mood_category']
    mood_description = mood_analysis['mood_description']
    
    try:
        # Get random songs from the mood library
        mood_songs = MOOD_SONG_LIBRARIES.get(mood_category, [])
        selected_songs = random.sample(mood_songs, min(3, len(mood_songs)))
        
        tracks = []
        
        # Search for each selected song
        for song_info in selected_songs:
            search_query = f"{song_info['name']} {song_info['artist']}"
            try:
                results = spotify.search(q=search_query, type='track', limit=1)
                if results['tracks']['items']:
                    track = results['tracks']['items'][0]
                    tracks.append({
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'uri': track['uri'],
                        'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
                        'external_url': track['external_urls']['spotify']
                    })
            except Exception as e:
                print(f"Failed to search for {song_info['name']}: {e}")
                continue
        
        # If we need more songs, search by mood terms
        if len(tracks) < 5:
            search_terms = random.choice(selected_songs)['search_terms'] if selected_songs else ['music']
            search_term = random.choice(search_terms)
            
            try:
                results = spotify.search(q=search_term, type='track', limit=10)
                for track in results['tracks']['items']:
                    if len(tracks) >= 5:
                        break
                    if not any(t['uri'] == track['uri'] for t in tracks):  # Avoid duplicates
                        tracks.append({
                            'name': track['name'],
                            'artist': track['artists'][0]['name'],
                            'uri': track['uri'],
                            'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
                            'external_url': track['external_urls']['spotify']
                        })
            except Exception as e:
                print(f"Failed to search by mood terms: {e}")
        
        return tracks[:5]  # Return exactly 5 songs
        
    except Exception as e:
        print(f"Spotify search failed: {e}")
        return []

def get_song_recommendations(mood_analysis: dict) -> list:
    """Gets song recommendations based on detailed mood analysis."""
    
    mood_category = mood_analysis['mood_category']
    
    # Try Spotify search first
    spotify_tracks = search_spotify_songs(mood_analysis)
    if len(spotify_tracks) >= 3:  # If we got decent results from Spotify
        return spotify_tracks
    
    print(f"Falling back to curated recommendations for {mood_category} mood...")
    
    # Fallback to curated data with randomization
    mood_songs = MOOD_SONG_LIBRARIES.get(mood_category, [])
    if mood_songs:
        # Randomly select 5 songs from the mood library
        selected_songs = random.sample(mood_songs, min(5, len(mood_songs)))
        fallback_tracks = []
        
        for i, song_info in enumerate(selected_songs):
            fallback_tracks.append({
                'name': song_info['name'],
                'artist': song_info['artist'],
                'uri': f'spotify:track:fallback_{mood_category}_{i}',
                'album_art': 'https://i.scdn.co/image/ab67616d0000b273c8b444df094279e70d0ed856',
                'external_url': f'https://open.spotify.com/search/{song_info["name"]} {song_info["artist"]}'
            })
        
        return fallback_tracks
    
    # Ultimate fallback - return a simple default song
    return [{
        'name': 'Happy',
        'artist': 'Pharrell Williams',
        'uri': 'spotify:track:60nZcImufyMA1MKQY3dcCH',
        'album_art': 'https://i.scdn.co/image/ab67616d0000b27341720ef0ae31e10d39e43ca2',
        'external_url': 'https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH'
    }]

# --- API Endpoint ---
@app.post("/recommend")
def recommend_songs(text_input: TextInput):
    if not text_input.text:
        raise HTTPException(status_code=400, detail="No text provided.")
    
    # Get detailed mood analysis
    mood_analysis = analyze_mood(text_input.text)
    songs = get_song_recommendations(mood_analysis)
    
    if not songs:
        raise HTTPException(status_code=404, detail="Could not find any song recommendations.")
    
    # Return comprehensive response with mood summary and top 5 songs
    return {
        "mood_analysis": {
            "category": mood_analysis['mood_category'],
            "description": mood_analysis['mood_description'],
            "summary": mood_analysis['summary'],
            "score": mood_analysis['score'],
            "intensity": mood_analysis['intensity']
        },
        "songs": songs[:5]  # Ensure we return exactly 5 songs
    }