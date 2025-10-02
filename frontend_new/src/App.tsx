import "./App.css";
import { useState } from "react";
import AudioRecorder from "./components/AudioRecorder";
import AudioUploader from "./components/AudioUploader";

// Define TypeScript interfaces for the API response
interface MoodAnalysis {
  category: string;
  description: string;
  summary: string;
  score: number;
  intensity: string;
}

interface Song {
  name: string;
  artist: string;
  album_art: string;
  uri: string;
  external_url: string;
}

interface ApiResponse {
  mood_analysis: MoodAnalysis;
  songs: Song[];
}

function App() {
  // State to store what the user types
  const [moodText, setMoodText] = useState("");
  // State to track if we're loading
  const [isLoading, setIsLoading] = useState(false);
  // State to store the API response
  const [recommendations, setRecommendations] = useState<Song[]>([]);
  const [moodAnalysis, setMoodAnalysis] = useState<MoodAnalysis | null>(null);
  // State to handle errors
  const [error, setError] = useState("");
  // State for success message
  const [showSuccess, setShowSuccess] = useState(false);
  // State to track if audio is uploading
  const [isUploading, setIsUploading] = useState(false);

  // Function to handle when user clicks the button
  const handleGetRecommendations = async () => {
    if (!moodText.trim()) return;
    
    setIsLoading(true);
    setError("");
    setShowSuccess(false);
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
        throw new Error(`Server error: ${response.status}. Please try again.`);
      }

      const data: ApiResponse = await response.json();
      
      if (!data.songs || data.songs.length === 0) {
        throw new Error("No songs found for your mood. Try a different description.");
      }

      setRecommendations(data.songs);
      setMoodAnalysis(data.mood_analysis);
      setShowSuccess(true);
      
      // Auto-hide success message after 3 seconds
      setTimeout(() => setShowSuccess(false), 3000);
      
    } catch (err) {
      let errorMessage = "Something went wrong. Please try again.";
      
      if (err instanceof Error) {
        if (err.message.includes('fetch')) {
          errorMessage = "Can't connect to server. Make sure the backend is running.";
        } else {
          errorMessage = err.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key in textarea
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey && !isLoading && moodText.trim()) {
      handleGetRecommendations();
    }
  };

  // Handle transcript from audio
  const handleTranscriptReceived = (transcript: string) => {
    setMoodText(transcript);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  // Handle audio errors
  const handleAudioError = (errorMsg: string) => {
    setError(errorMsg);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Groovi</h1>
        <p>Describe your mood with text or voice, and we'll find the perfect soundtrack for you.</p>

        <div className="input-area">
          {/* Audio Input Options */}
          <div className="audio-input-section">
            <AudioRecorder 
              onTranscriptReceived={handleTranscriptReceived}
              onError={handleAudioError}
            />
            <AudioUploader 
              onTranscriptReceived={handleTranscriptReceived}
              onError={handleAudioError}
              onUploading={setIsUploading}
            />
          </div>

          {/* Existing Text Input */}
          <textarea
            value={moodText}
            onChange={(e) => setMoodText(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="e.g., 'I had a fantastic day and I'm ready to celebrate!' (Ctrl+Enter to submit)"
            rows={4}
          />
          
          <button
            onClick={handleGetRecommendations}
            disabled={isLoading || isUploading || !moodText.trim()}
            className="simple-vibe-button"
          >
            {isLoading ? "Finding your vibe..." : 
             isUploading ? "Processing audio..." :
             "Get My Vibe"}
          </button>
          
          <div className="char-counter">
            {moodText.length}/500 characters
          </div>
        </div>
      </header>

      <main className="results-area">
        {/* Success message */}
        {showSuccess && (
          <div className="success">
            🎵 Found {recommendations.length} perfect songs for your mood!
          </div>
        )}

        {/* Error message */}
        {error && <div className="error">{error}</div>}
        
        {/* Mood analysis */}
        {moodAnalysis && (
          <div className="mood-summary">
            <h2>Your Mood Analysis</h2>
            <div className="mood-card">
              <div className="mood-category">
                <span className="mood-label">{moodAnalysis.category}</span>
                <span className="mood-intensity">
                  ({moodAnalysis.intensity} intensity)
                </span>
              </div>
              
              {/* ADD THIS: Display the AI-generated summary */}
              <p className="mood-summary-text">{moodAnalysis.summary}</p>
              
              <p className="mood-description">{moodAnalysis.description}</p>
              <div className="mood-score">
                Sentiment Score:{" "}
                <span className="score-value">
                  {moodAnalysis.score.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Songs section */}
        {recommendations.length > 0 && (
          <div className="songs-section">
            <h2>Your Personalized Playlist</h2>
            <p className="songs-subtitle">
              Top {recommendations.length} songs curated for your current mood
            </p>
          </div>
        )}

        <div className="song-list">
          {recommendations.map((song, index) => (
            <div
              key={song.uri}
              className="song-item"
              onClick={() => window.open(song.external_url, "_blank")}
              style={{ animationDelay: `${index * 0.15}s` }}
              title={`Listen to ${song.name} by ${song.artist} on Spotify`}
            >
              <img 
                src={song.album_art} 
                alt={`${song.name} album cover`} 
                className="album-art"
                loading="lazy"
              />
              <div className="song-details">
                <p className="song-name">{song.name}</p>
                <p className="song-artist">{song.artist}</p>
              </div>
              <div className="play-indicator">▶</div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default App;
