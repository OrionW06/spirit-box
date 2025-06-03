#!/usr/bin/env python3
import os
import random
import argparse
import numpy as np
import sounddevice as sd
from pathlib import Path
import librosa

class SpiritBox:
    def __init__(self, audio_dir, scan_speed=50, noise_level=0.7, reverb=True, activation_chance=0.5):
        self.audio_dir = Path(audio_dir)
        self.scan_speed = scan_speed  # ms between clips
        self.noise_level = noise_level
        self.reverb = reverb
        self.activation_chance = activation_chance
        self.audio_clips = self.load_clips()
        self.running = False
        
        if not self.audio_clips:
            raise ValueError("No valid audio clips found!")
        
        # Audio settings
        self.sample_rate = 24000
        sd.default.samplerate = self.sample_rate
        sd.default.channels = 1

    def load_clips(self):
        """Load all short audio clips from directory"""
        valid_ext = {'.wav', '.mp3', '.ogg', '.flac'}
        clips = []
        
        for root, _, files in os.walk(self.audio_dir):
            for f in files:
                if Path(f).suffix.lower() in valid_ext:
                    clips.append(Path(root) / f)
        
        return clips

    def apply_reverb(self, audio):
        """Apply a simple but effective reverb"""
        impulse_length = int(0.2 * self.sample_rate)  # 200ms reverb tail
        impulse = np.zeros(impulse_length)
        
        # Create reverb impulses at different delays
        delays = [int(x * self.sample_rate) for x in [0.02, 0.04, 0.08, 0.16]]
        decays = [0.8, 0.6, 0.4, 0.2]
        
        for delay, decay in zip(delays, decays):
            if delay < impulse_length:
                impulse[delay] = decay
        
        # Apply the reverb
        wet = np.convolve(audio, impulse, mode='same')
        return np.clip(audio * 0.7 + wet * 0.3, -1, 1)

    def process_clip(self, clip_path):
        """Load and process a single audio clip"""
        try:
            # Load audio with librosa
            clip, sr = librosa.load(clip_path, sr=self.sample_rate, mono=True)
            
            # Normalize the clip
            clip = clip / (np.max(np.abs(clip)) + 0.001)
            
            # Add effects
            if self.reverb:
                clip = self.apply_reverb(clip)
            
            return clip
        
        except Exception as e:
            print(f"Error processing {clip_path.name}: {str(e)}")
            return None

    def generate_noise(self, duration_ms):
        """Generate white noise for background"""
        samples = int(duration_ms * self.sample_rate / 1000)
        return np.random.randn(samples) * self.noise_level * 0.05

    def run(self):
        """Main spirit box scanning loop"""
        print(f"Spirit box active - Scanning {len(self.audio_clips)} clips...")
        print(f"Activation chance: {self.activation_chance*100}%")
        print("Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            while self.running:
                # Generate background noise for the scan duration
                noise = self.generate_noise(self.scan_speed)
                
                # Roll the RNG to determine if we play a clip or just noise
                if random.random() < self.activation_chance:
                    clip_path = random.choice(self.audio_clips)
                    print(f"▶ {clip_path.name}", end='\r')
                    audio = self.process_clip(clip_path)
                    if audio is not None:
                        # Mix the clip with noise
                        min_length = min(len(noise), len(audio))
                        noise[:min_length] += audio[:min_length]
                        noise = np.clip(noise, -1, 1)
                else:
                    print("⏸ silence", end='\r')
                
                # Play the mixed audio
                sd.play(noise)
                sd.wait()
                
        except KeyboardInterrupt:
            print("\nSpirit box stopped")
            self.running = False
            sd.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spirit Box Simulator")
    parser.add_argument("directory", help="Directory containing audio clips")
    parser.add_argument("--speed", type=int, default=50, 
                      help="Scan speed in milliseconds (default: 50)")
    parser.add_argument("--noise", type=float, default=0.7,
                      help="White noise level (0-1, default: 0.7)")
    parser.add_argument("--no-reverb", action="store_false",
                      help="Disable reverb effect")
    parser.add_argument("--chance", type=float, default=0.5,
                      help="Probability of playing a clip (0-1, default: 0.5)")
    
    args = parser.parse_args()
    
    try:
        spirit_box = SpiritBox(
            audio_dir=args.directory,
            scan_speed=args.speed,
            noise_level=args.noise,
            reverb=args.no_reverb,
            activation_chance=args.chance
        )
        spirit_box.run()
    except Exception as e:
        print(f"Error: {str(e)}")
