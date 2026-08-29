import sys
import os
from extractor import extract_audio
from transcriber import transcribe_audio

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <YouTube_URL>")
        sys.exit(1)

    url_or_path = sys.argv[1]
    output_dir = "transcriptions"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        if url_or_path.startswith(('http://', 'https://', 'www.')):
            # 1. Extract Audio
            print(f"--- Step 1: Extracting audio from {url_or_path} ---")
            audio_info = extract_audio(url_or_path)
            audio_file = audio_info['path']
            print(f"Audio extracted to: {audio_file}")
        else:
            # 1. Use local path
            print(f"--- Step 1: Using local audio file {url_or_path} ---")
            if not os.path.exists(url_or_path):
                print(f"Error: File not found: {url_or_path}")
                sys.exit(1)
            audio_file = url_or_path

        # 2. Transcribe Audio
        print(f"\n--- Step 2: Transcribing audio with Whisper Large-v3 (Incremental) ---")
        
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}.txt")
        
        result = transcribe_audio(audio_file, output_file=output_file)
        
        # 3. Success Message (File is already saved incrementally)
        print(f"\n--- Success! Transcription saved to: {output_file} ---")
        
        # Cleanup (optional, keeping for now)
        # os.remove(audio_file)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
