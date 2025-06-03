import os
import shlex
from pathlib import Path

def main():
    # Check if audio directory exists
    audio_dir = Path("audio")
    if not audio_dir.is_dir():
        print("Error: 'audio' directory not found!")
        return 1

    # Change to audio directory
    os.chdir(audio_dir)

    # Get list of MP3 files (now that we're in the audio directory)
    mp3_files = sorted(Path('.').glob("*.mp3"))
    if not mp3_files:
        print("No MP3 files found in the 'audio' directory")
        return 1

    # Create a temporary file with the list of files to concatenate
    list_file = "concat_list.txt"
    try:
        with open(list_file, "w", encoding='utf-8') as f:
            for mp3 in mp3_files:
                # Properly escape quotes and backslashes for ffmpeg
                escaped_name = str(mp3).replace("'", "'\\''")
                f.write(f"file '{escaped_name}'\n")

        # Concatenate the files using ffmpeg
        os.system(f"ffmpeg -f concat -safe 0 -i {shlex.quote(list_file)} -c copy ../output.mp3")

    finally:
        # Clean up
        if os.path.exists(list_file):
            os.remove(list_file)

    print("Concatenation complete. Output file: ../output.mp3")
    return 0

if __name__ == "__main__":
    exit(main())
