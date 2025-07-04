# cut_audio.py

from pydub import AudioSegment
import os

# --- YOU ONLY NEED TO CHANGE THESE VARIABLES ---

# 1. The path to the MP3 file you want to cut.
#    (e.g., "C:/Users/YourName/Music/song.mp3" or "MUSIC/long_theme.mp3")
INPUT_FILE = "theme.mp3" 

# 2. The path where you want to save the new, shorter MP3 file.
OUTPUT_FILE = "theme_short.mp3"

# 3. The time where you want to cut the audio.
CUT_MINUTES = 2
CUT_SECONDS = 36

# ---------------------------------------------


def cut_mp3(input_path, output_path, cut_time_minutes, cut_time_seconds):
    """
    Cuts an MP3 file from the beginning to the specified time.

    Args:
        input_path (str): Path to the source MP3 file.
        output_path (str): Path to save the new MP3 file.
        cut_time_minutes (int): The minutes part of the cut timestamp.
        cut_time_seconds (int): The seconds part of the cut timestamp.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at '{input_path}'")
        return

    # pydub works in milliseconds
    cut_time_ms = (cut_time_minutes * 60 + cut_time_seconds) * 1000
    
    print(f"Loading audio file: {input_path}...")
    try:
        # Load the MP3 file
        audio = AudioSegment.from_mp3(input_path)
    except Exception as e:
        print(f"Error loading file. Make sure FFmpeg is installed and accessible.")
        print(f"Details: {e}")
        return

    print(f"Audio loaded successfully. Duration: {len(audio) / 1000:.2f}s")

    # Check if the cut time is valid
    if cut_time_ms >= len(audio):
        print("Error: Cut time is longer than the audio file itself.")
        print("The original file will be copied instead.")
        cut_time_ms = len(audio)

    print(f"Cutting audio at {cut_time_minutes:02d}:{cut_time_seconds:02d} (which is {cut_time_ms}ms)...")
    
    # Slice the audio. It's as simple as Python list slicing!
    new_audio = audio[:cut_time_ms]

    print(f"Saving new file to: {output_path}...")
    
    # Export the new audio chunk to an MP3 file
    try:
        new_audio.export(output_path, format="mp3")
        print("Done! Your new audio file has been saved.")
    except Exception as e:
        print(f"Error exporting file: {e}")


# This part runs the function when you execute the script
if __name__ == "__main__":
    cut_mp3(INPUT_FILE, OUTPUT_FILE, CUT_MINUTES, CUT_SECONDS)