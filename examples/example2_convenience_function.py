"""Example 2: Using the convenience function to visualize audio files."""

import sys
from pathlib import Path

# Add the parent directory to the path to import our music package
sys.path.append(str(Path(__file__).parent.parent))

from music.audio_visualizer import load_and_plot_audio


def main():
    """Demonstrate using the convenience function."""
    
    print("Example 2: Using convenience function")
    
    # Audio file to process
    audio_file = "molihua.mp4"
    
    try:
        # Use the convenient one-line function
        load_and_plot_audio(
            audio_file,
            figsize=(12, 4),
            title="Convenient Audio Visualization",
            save_path="example2_waveform.png",  # Save with unique name
            show=True  # Show the visualization
        )
        
        print("✓ Convenience function example completed")
        print("✓ Waveform saved as example2_waveform.png")
        
    except FileNotFoundError:
        print(f"Audio file '{audio_file}' not found.")
        print("Please ensure the audio file exists in the project root.")
    except Exception as e:
        print(f"Error processing audio: {e}")


if __name__ == "__main__":
    main() 