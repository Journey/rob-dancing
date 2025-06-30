"""Example script demonstrating basic usage of the music visualization library."""

import sys
from pathlib import Path

# Add the parent directory to the path to import our music package
sys.path.append(str(Path(__file__).parent.parent))

from music.audio_visualizer import AudioVisualizer, load_and_plot_audio


def main():
    """Demonstrate different ways to use the audio visualization library."""
    
    # Example 1: Using the class-based approach
    print("Example 1: Using AudioVisualizer class")
    visualizer = AudioVisualizer(figsize=(14, 6))
    
    # Replace 'song.mp3' with your actual audio file
    audio_file = "molihua.mp4"
    
    try:
        # Load audio and plot waveform (don't show to avoid blocking)
        visualizer.visualize_audio_file(
            audio_file, 
            title="My Audio File Waveform",
            save_path="waveform.png",  # Optional: save the plot
            show=False  # Don't show to avoid blocking execution
        )
        print("✓ Example 1 completed - waveform saved as waveform.png")
        
        # Example 2: Using the convenience function
        print("\nExample 2: Using convenience function")
        load_and_plot_audio(
            audio_file,
            figsize=(12, 4),
            title="Convenient Audio Visualization",
            show=False  # Don't show to avoid blocking execution
        )
        print("✓ Example 2 completed")
        
        # Example 3: Step-by-step approach
        print("\nExample 3: Step-by-step approach")
        y, sr = visualizer.load_audio(audio_file)
        print(f"Loaded audio: {len(y)} samples at {sr} Hz")
        print(f"Duration: {len(y) / sr:.2f} seconds")
        
        # Plot with custom settings (show this one)
        fig = visualizer.plot_waveform(
            y, sr, 
            title=f"Custom Waveform ({len(y) / sr:.1f}s)",
            show=True  # Show the final visualization
        )
        print("✓ Example 3 completed")
        
    except FileNotFoundError:
        print(f"Audio file '{audio_file}' not found.")
        print("Please place audio file in the project root,")
    except Exception as e:
        print(f"Error processing audio: {e}")


if __name__ == "__main__":
    main() 