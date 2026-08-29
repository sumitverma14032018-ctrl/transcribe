import yt_dlp
import os

def extract_audio(url, output_path='downloads'):
    """
    Extracts audio from a YouTube video and saves it as an mp3 file.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': False,
        'extractor_args': {'youtube': {'player_client': ['android', 'web', 'tv']}},
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        mp3_filename = base + '.mp3'
        
        return {
            'path': mp3_filename,
            'title': info.get('title', 'Unknown Title'),
            'duration': info.get('duration', 0)
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        print(f"Extracting audio from: {test_url}")
        try:
            result = extract_audio(test_url)
            print(f"Successfully extracted: {result['path']}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python extractor.py <YouTube_URL>")
