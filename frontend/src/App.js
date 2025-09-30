import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// IMPORTANT: You MUST get this token from the Spotify Developer Dashboard.
// It expires every hour. A real app would have a full login flow.
const SPOTIFY_OAUTH_TOKEN = 'BQABwnH1Gm3WKBRt29X-LJ3C5Zz8JVNBa7Z_FN68l26RR3uQS8bd7e054BALW8hlvGus7_Hbr9Qiu8IZud-GtmmIbZFkO9z8VggbucqFp7iIPoSiAtdUS4p_o1t9V8apeRN_awVNeQo';

function App() {
  const [moodText, setMoodText] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [moodAnalysis, setMoodAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentTrack, setCurrentTrack] = useState(null);

  const playerRef = useRef(null);
  const deviceIdRef = useRef(null);

  // Initialize Spotify Web Playback SDK
  useEffect(() => {
    if (!SPOTIFY_OAUTH_TOKEN || SPOTIFY_OAUTH_TOKEN === 'YOUR_TEMPORARY_SPOTIFY_OAUTH_TOKEN') {
      console.error("Spotify OAuth Token is not set! Please get a new token.");
      setError("Spotify Player failed to load. Please provide a valid OAuth Token in App.js.");
      return;
    }

    window.onSpotifyWebPlaybackSDKReady = () => {
      const player = new window.Spotify.Player({
        name: 'Mood Recommender Player',
        getOAuthToken: cb => { cb(SPOTIFY_OAUTH_TOKEN); },
        volume: 0.5
      });

      player.addListener('ready', ({ device_id }) => {
        console.log('Ready with Device ID', device_id);
        deviceIdRef.current = device_id;
      });

      player.addListener('not_ready', ({ device_id }) => {
        console.log('Device ID has gone offline', device_id);
      });
      
      player.addListener('player_state_changed', (state) => {
        if (!state) {
            return;
        }
        setCurrentTrack(state.track_window.current_track);
      });

      player.connect();
      playerRef.current = player;
    };
  }, []);


  const getRecommendations = async () => {
    if (!moodText) return;
    setIsLoading(true);
    setError('');
    setRecommendations([]);
    setMoodAnalysis(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: moodText }),
      });

      if (!response.ok) {
        throw new Error('Failed to get recommendations from the backend.');
      }

      const data = await response.json();
      setRecommendations(data.songs);
      setMoodAnalysis(data.mood_analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  const playSong = (spotify_uri) => {
    if (!deviceIdRef.current) {
        console.error("Spotify player is not ready.");
        setError("Spotify player is not ready. Make sure you are using a Premium account.");
        return;
    }
    fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceIdRef.current}`, {
        method: 'PUT',
        body: JSON.stringify({ uris: [spotify_uri] }),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${SPOTIFY_OAUTH_TOKEN}`
        },
    });
  };


  return (
    <div className="App">
      <header className="App-header">
        <h1>Mood-Based Song Recommender</h1>
        <p>Describe your mood, and we'll find the perfect soundtrack for you.</p>
        <div className="input-area">
          <textarea
            value={moodText}
            onChange={(e) => setMoodText(e.target.value)}
            placeholder="e.g., 'I had a fantastic day and I'm ready to celebrate!'"
          />
          <button onClick={getRecommendations} disabled={isLoading}>
            {isLoading ? 'Thinking...' : 'Get My Vibe'}
          </button>
        </div>
      </header>

      <main className="results-area">
        {error && <p className="error">{error}</p>}
        
        {moodAnalysis && (
          <div className="mood-summary">
            <h2>Your Mood Analysis</h2>
            <div className="mood-card">
              <div className="mood-category">
                <span className="mood-label">{moodAnalysis.category}</span>
                <span className="mood-intensity">({moodAnalysis.intensity} intensity)</span>
              </div>
              <p className="mood-description">{moodAnalysis.description}</p>
              <div className="mood-score">
                Sentiment Score: <span className="score-value">{moodAnalysis.score.toFixed(2)}</span>
              </div>
            </div>
          </div>
        )}

        {recommendations.length > 0 && (
          <div className="songs-section">
            <h2>Your Personalized Playlist</h2>
            <p className="songs-subtitle">Top 5 songs curated for your current mood</p>
          </div>
        )}

        <div className="song-list">
          {recommendations.map((song) => (
            <div 
            key={song.uri} 
            className="song-item" 
            onClick={() => window.open(song.external_url, '_blank')}
          >
              <img src={song.album_art} alt={song.name} className="album-art" />
              <div className="song-details">
                <p className="song-name">{song.name}</p>
                <p className="song-artist">{song.artist}</p>
              </div>
            </div>
          ))}
        </div>
      </main>

      {currentTrack && (
        <footer className="now-playing-bar">
           <img src={currentTrack.album.images[0].url} alt={currentTrack.name} />
           <div>
              <p>Now Playing: {currentTrack.name}</p>
              <p>{currentTrack.artists.map(artist => artist.name).join(', ')}</p>
           </div>
        </footer>
      )}
    </div>
  );
}

export default App;