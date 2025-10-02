"""Audio transcription service using Deepgram"""

from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from config.settings import settings

class AudioTranscriber:
    """Transcribes audio to text using Deepgram API"""
    
    def __init__(self):
        """Initialize Deepgram client"""
        self.client = None
        if settings.DEEPGRAM_API_KEY:
            try:
                self.client = DeepgramClient(settings.DEEPGRAM_API_KEY)
                print("✅ Deepgram client initialized")
            except Exception as e:
                print(f"❌ Deepgram init failed: {e}")
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe audio bytes to text
        
        Args:
            audio_data: Raw audio file bytes (mp3, wav, webm, etc.)
            
        Returns:
            Transcribed text string
        """
        if not self.client:
            raise ValueError("Deepgram API key not configured")
        
        try:
            # Prepare audio payload
            payload: FileSource = {
                "buffer": audio_data,
            }
            
            # Configure transcription options
            options = PrerecordedOptions(
                model="nova-2",  # Fast, accurate model
                smart_format=True,  # Auto-formatting (punctuation, etc.)
                language="en",  # English language
                punctuate=True,  # Add punctuation
                diarize=False,  # Don't separate speakers
            )
            
            # Call Deepgram API
            response = self.client.listen.rest.v("1").transcribe_file(payload, options)
            
            # Extract transcript from response
            transcript = response.results.channels[0].alternatives[0].transcript
            
            if not transcript or transcript.strip() == "":
                raise ValueError("No speech detected in audio")
            
            print(f"✅ Transcription: {transcript[:100]}...")
            return transcript
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")

# Create global instance
audio_transcriber = AudioTranscriber()