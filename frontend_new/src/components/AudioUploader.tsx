import { useRef } from "react";

interface AudioUploaderProps {
  onTranscriptReceived: (transcript: string) => void;
  onError: (error: string) => void;
  onUploading: (uploading: boolean) => void;
}

export default function AudioUploader({ onTranscriptReceived, onError, onUploading }: AudioUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    
    if (!file) return;

    // Validate file type
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/webm', 'audio/ogg', 'audio/mp4'];
    if (!allowedTypes.includes(file.type)) {
      onError('Invalid file type. Please upload mp3, wav, webm, ogg, or m4a files.');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      onError('File too large. Maximum size is 10MB.');
      return;
    }

    onUploading(true);

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('audio', file);

      // Send to backend
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
      console.error("Upload error:", err);
      onError(err instanceof Error ? err.message : "Failed to upload audio");
    } finally {
      onUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="audio-uploader">
      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
        id="audio-file-input"
      />
      <label htmlFor="audio-file-input" className="audio-button upload-audio">
        📁 Upload Audio File
      </label>
    </div>
  );
}