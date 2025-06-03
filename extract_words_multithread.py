import argparse
import whisper
import whisper_timestamped
import subprocess
import os
import re
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def get_sample_rate(audio_path):
    """Get the sample rate of the input audio file"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return int(result.stdout.strip())

def sanitize_filename(text):
    """Remove unsafe characters from filenames"""
    return re.sub(r'[^\w\-_]', '_', text)

def process_word(audio_path, output_dir, word, original_sample_rate):
    """Process a single word segment"""
    word_text = word["text"].strip().lower()
    start = word["start"]
    end = word["end"]
    target_sample_rate = original_sample_rate // 2

    # Add 50ms padding to avoid cutoffs
    padded_start = max(0, start - 0.05)
    padded_end = end + 0.05

    # Generate safe filename
    safe_text = sanitize_filename(word_text)
    output_file = f"{output_dir}/{safe_text}_{padded_start:.2f}-{padded_end:.2f}.mp3"

    # FFmpeg command with sample rate conversion and MP3 encoding
    subprocess.run([
        "ffmpeg",
        "-i", audio_path,
        "-ss", str(padded_start),
        "-to", str(padded_end),
        "-af", "silenceremove=start_periods=1:start_threshold=-50dB,aresample=resampler=soxr",
        "-ar", str(target_sample_rate),
        "-c:a", "libmp3lame",
        "-q:a", "2",  # Good quality (0-9 scale, 0=best)
        "-y",
        output_file
    ], check=True)
    return output_file  # Return the processed filename for progress tracking

def split_audio_into_words(audio_path, output_dir="word_clips", max_workers=4):
    # Get original sample rate
    original_sample_rate = get_sample_rate(audio_path)

    # Load Whisper model
    model = whisper.load_model("small")

    # Transcribe with word-level timestamps
    audio = whisper.load_audio(audio_path)
    result = whisper_timestamped.transcribe(model, audio)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Prepare list of words to process
    words_to_process = []
    for segment in result["segments"]:
        for word in segment["words"]:
            if word["text"].strip():  # Skip empty words
                words_to_process.append(word)

    # Use ThreadPoolExecutor to process words in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all word processing tasks and track progress
        futures = []
        for word in words_to_process:
            futures.append(executor.submit(
                process_word, 
                audio_path, 
                output_dir, 
                word, 
                original_sample_rate
            ))

        # Initialize progress bar
        with tqdm(total=len(futures), desc="Processing words") as pbar:
            for future in futures:
                try:
                    future.result()  # Will raise exceptions if any occurred
                    pbar.update(1)
                except subprocess.CalledProcessError as e:
                    pbar.write(f"Error processing word: {e}")
                    pbar.update(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split audio into clean word clips as MP3 at half sample rate."
    )
    parser.add_argument("audio_path", help="Input audio file (MP3/WAV/etc.)")
    parser.add_argument("--output_dir", default="word_clips", help="Output directory")
    parser.add_argument(
        "--jobs", 
        type=int, 
        default=min(4, os.cpu_count()), 
        help="Number of parallel jobs to use (default: 4 or CPU count if lower)"
    )
    args = parser.parse_args()

    split_audio_into_words(
        args.audio_path, 
        args.output_dir, 
        args.jobs
    )
