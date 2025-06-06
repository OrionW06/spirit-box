# Spirit Box

A customizable, Python-based "spirit box" audio tool for paranormal audio experiments. This project provides utilities to extract word-level audio clips from speech, concatenate clips, and play them in rapid, randomized, noisy sequences—mimicking the operation of a traditional "spirit box" used in ghost hunting and ITC (Instrumental Transcommunication) research.

## Features

- **Spirit Box Audio Player**  
  Rapidly plays random audio-word clips with configurable white noise and optional reverb effects. Simulates the scanning and randomness of a real spirit box device.

- **Word Extraction from Audio**  
  Uses the OpenAI Whisper model to transcribe input audio files and cut them into individual word clips (MP3 format) with precise timestamps.

- **Batch Processing**  
  Includes a multithreaded version for faster word extraction (see note below).

- **Clip Concatenation**  
  Merge multiple MP3 clips into a single audio file using ffmpeg.

## Components

### `sbox.py`
The main spirit box player.  
- Scans a directory for audio clips and rapidly plays them with added noise.
- Configurable scan speed, noise level, reverb, activation probability, and more.
- CLI usage:
  ```bash
  python sbox.py <directory> [--speed 50] [--noise 0.7] [--no-reverb] [--chance 0.5]
  ```

### `extract_words.py`
Extracts word-level MP3 clips from a source audio file.
- Uses OpenAI Whisper (and whisper_timestamped) for transcription.
- Outputs each word as an MP3 in the specified directory.
- CLI usage:
  ```bash
  python extract_words.py <input_audio> [--output_dir word_clips]
  ```

### `extract_words_multithread.py`  
**Note: This multithreaded variant is experimental and has not been thoroughly tested.**  
- Same functionality as `extract_words.py`, but processes word clips in parallel for speed.
- CLI usage:
  ```bash
  python extract_words_multithread.py <input_audio> [--output_dir word_clips] [--jobs 4]
  ```

### `concat_mp3.py`
Concatenates all MP3 files in the `audio` directory into a single output file using ffmpeg.
- CLI usage:
  ```bash
  python concat_mp3.py
  ```

## Requirements

- Python 3.7+
- [sounddevice](https://python-sounddevice.readthedocs.io/)
- [librosa](https://librosa.org/)
- [numpy](https://numpy.org/)
- [openai-whisper](https://github.com/openai/whisper)
- [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped)
- [ffmpeg](https://ffmpeg.org/) (must be installed and on PATH)
- tqdm (for progress bars in the multithreaded version)

Install dependencies (example):
```bash
pip install sounddevice librosa numpy openai-whisper whisper-timestamped tqdm
```

## Usage Example

1. **Extract words from your audio file:**
   ```bash
   python extract_words.py myaudio.mp3 --output_dir word_clips
   ```

2. **Play your spirit box:**
   ```bash
   python sbox.py word_clips --speed 50 --noise 0.7 --chance 0.6
   ```

3. **Concatenate clips (optional):**
   Place MP3 files in the `audio` directory and run:
   ```bash
   python concat_mp3.py
   ```

## Disclaimer

- The multithreaded extraction app (`extract_words_multithread.py`) is **experimental** and has **not been thoroughly tested**. Use with caution.
- This software is provided for entertainment and research purposes only.

---
Contributions and feedback are welcome!
