import argparse
import os
import sys
from transcriber import transcribe_audio

def main():
    parser = argparse.ArgumentParser(description="Transcribe an MP3 file using OpenAI Whisper.")
    parser.add_argument("input", help="Path to the input MP3 file.")
    parser.add_argument("output", help="Path to the output transcription text file.")
    parser.add_argument("--model", default="large-v3", help="Whisper model to use (default: large-v3).")

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    model_name = args.model

    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)

    print(f"--- Starting Transcription ---")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Model:  {model_name}")
    print("-" * 30)

    try:
        # The transcribe_audio function already handles incremental saving to output_path
        transcribe_audio(input_path, model_name=model_name, output_file=output_path)
        print(f"\n--- Success! Transcription saved to: {output_path} ---")
    except Exception as e:
        print(f"\nAn error occurred during transcription: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
