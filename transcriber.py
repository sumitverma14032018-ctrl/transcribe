import whisper
import os
import logging
import sys
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SegmentCapturer:
    """
    Intercepts stdout to capture Whisper's verbose segment output
    and writes it incrementally to a file.
    """
    def __init__(self, output_file):
        self.output_file = output_file
        self.terminal = sys.stdout
        # Pattern to match Whisper segment output like [00:00.000 --> 00:05.000] text
        self.segment_pattern = re.compile(r'\[\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}\.\d{3}\]\s+(.*)')

    def write(self, message):
        self.terminal.write(message)
        match = self.segment_pattern.search(message)
        if match:
            text = match.group(1).strip()
            if text:
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(text + " ")
                    f.flush()

    def flush(self):
        self.terminal.flush()

def transcribe_audio(audio_file, model_name="large-v3", output_file=None):
    """
    Transcribes an audio file using OpenAI Whisper.
    If output_file is provided, segments are saved incrementally.
    """
    if not os.path.exists(audio_file):
        logger.error(f"Audio file not found: {audio_file}")
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    logger.info(f"Loading Whisper model: {model_name}...")
    model = whisper.load_model(model_name)
    
    logger.info(f"Starting transcription for: {audio_file}")
    
    # Setup incremental saving if output_file is provided
    original_stdout = sys.stdout
    if output_file:
        # Initialize/Clear the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("")
        sys.stdout = SegmentCapturer(output_file)

    try:
        # Using verbose=True will print individual segments to stdout
        result = model.transcribe(audio_file, verbose=True)
    finally:
        if output_file:
            sys.stdout = original_stdout
    
    logger.info(f"Transcription completed for: {audio_file}")
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_audio = sys.argv[1]
        test_output = sys.argv[2] if len(sys.argv) > 2 else "temp_transcription.txt"
        try:
            transcription = transcribe_audio(test_audio, output_file=test_output)
            print("\nFinal transcription result:")
            print(transcription["text"])
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python transcriber.py <audio_file_path> [output_file_path]")
