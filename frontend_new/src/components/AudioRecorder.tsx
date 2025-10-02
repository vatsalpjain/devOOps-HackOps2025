import { useState, useRef } from "react";

interface AudioRecorderProps {
  onTranscriptReceived: (transcript: string) => void;
  onError: (error: string) => void;
}

export default function AudioRecorder({ onTranscriptReceived, onError }: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Collect audio data
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await transcribeAudio(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      
    } catch (err) {
      console.error("Microphone access denied:", err);
      onError("Microphone access denied. Please allow microphone access and try again.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    setIsTranscribing(true);

    try {
      // Create FormData to send audio file
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      // Send to backend /transcribe endpoint
      const response = await fetch('http://127.0.0.1:8000/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Transcription failed');
      }

      const data = await response.json();
      onTranscriptReceived(data.transcript);
      
    } catch (err) {
      console.error("Transcription error:", err);
      onError(err instanceof Error ? err.message : "Failed to transcribe audio");
    } finally {
      setIsTranscribing(false);
    }
  };

  return (
    <div className="audio-recorder">
      {!isRecording && !isTranscribing && (
        <button 
          onClick={startRecording} 
          className="audio-button start-recording"
          title="Start voice recording"
        >
          🎤 Start Recording
        </button>
      )}

      {isRecording && (
        <button 
          onClick={stopRecording} 
          className="audio-button stop-recording"
          title="Stop and transcribe"
        >
          ⏹️ Stop Recording
        </button>
      )}

      {isTranscribing && (
        <div className="transcribing-indicator">
          <span className="spinner"></span> Transcribing audio...
        </div>
      )}
    </div>
  );
}