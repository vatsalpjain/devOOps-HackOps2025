# Mood-Based Song Recommender

A full-stack application that recommends songs based on your mood using sentiment analysis and the Spotify API.

## Quick Fix for "Failed to fetch" Error

The "Failed to fetch" error occurs because the backend server is not running. Follow these steps:

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
# Option 1: Using the start script
python start_server.py

# Option 2: Using uvicorn directly
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Start the Frontend
In a new terminal:
```bash
cd frontend
npm start
```

## Project Structure
```
song-recommender/
├── backend/
│   ├── main.py              # FastAPI backend
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── start_server.py      # Server startup script
└── frontend/
    ├── src/
    │   ├── App.js           # React frontend
    │   └── App.css          # Styles
    └── public/
        └── index.html       # HTML template
```

## How It Works

1. **Frontend**: React app where users input their mood
2. **Backend**: FastAPI server that:
   - Analyzes mood using VADER sentiment analysis
   - Gets song recommendations from Spotify API
   - Returns recommendations to frontend
3. **Spotify Integration**: Uses Spotify Web API for recommendations and Web Playback SDK for music playback

## Environment Variables

The backend uses these environment variables (stored in `.env`):
- `SPOTIPY_CLIENT_ID`: Your Spotify app client ID
- `SPOTIPY_CLIENT_SECRET`: Your Spotify app client secret

## Troubleshooting

### "Failed to fetch" Error
- **Cause**: Backend server not running
- **Solution**: Start the backend server using the steps above

### Spotify Playback Issues
- **Cause**: Invalid or expired OAuth token
- **Solution**: Get a new token from Spotify Developer Dashboard and update `SPOTIFY_OAUTH_TOKEN` in `App.js`

### CORS Errors
- **Cause**: Frontend and backend running on different ports
- **Solution**: Make sure frontend runs on `localhost:3000` and backend on `127.0.0.1:8000`
