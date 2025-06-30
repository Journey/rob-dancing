"""Example 1: Using AudioVisualizer class to visualize audio files."""

import sys
from pathlib import Path

# Add the parent directory to the path to import our music package
sys.path.append(str(Path(__file__).parent.parent))

from music.audio_visualizer import AudioVisualizer


def main():
    """Demonstrate using AudioVisualizer class."""
    
    print("Example 1: Using AudioVisualizer class")
    
    # Initialize the visualizer with custom figure size
    visualizer = AudioVisualizer(figsize=(14, 6))
    
    # Audio file to process
    audio_file = "molihua.mp4"
    
    try:
        # Load audio and plot waveform
        visualizer.visualize_audio_file(
            audio_file, 
            title="My Audio File Waveform",
            save_path="example1_waveform.png",  # Save with unique name
            show=True  # Show the visualization
        )
        
        print("✓ AudioVisualizer class example completed")
        print("✓ Waveform saved as example1_waveform.png")
        
    except FileNotFoundError:
        print(f"Audio file '{audio_file}' not found.")
        print("Please ensure the audio file exists in the project root.")
    except Exception as e:
        print(f"Error processing audio: {e}")


if __name__ == "__main__":
    main() 