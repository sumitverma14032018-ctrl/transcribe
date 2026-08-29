import argparse
import sys
from extractor import extract_audio

def main():
    parser = argparse.ArgumentParser(description="Convert a YouTube video to an MP3 file.")
    parser.add_argument("url", help="The URL of the YouTube video.")
    parser.add_argument("--output", default="downloads", help="The directory to save the MP3 file (default: downloads).")

    args = parser.parse_args()

    url = args.url
    output_dir = args.output

    print(f"--- Converting YouTube Video to MP3 ---")
    print(f"URL: {url}")
    print(f"Output Directory: {output_dir}")
    print("-" * 40)

    try:
        result = extract_audio(url, output_path=output_dir)
        print(f"\n--- Success! ---")
        print(f"Title: {result['title']}")
        print(f"Saved to: {result['path']}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
