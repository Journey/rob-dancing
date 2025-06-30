"""Example 3: Step-by-step approach to audio visualization."""

import sys
from pathlib import Path

# Add the parent directory to the path to import our music package
sys.path.append(str(Path(__file__).parent.parent))

from music.audio_visualizer import AudioVisualizer


def main():
    """Demonstrate step-by-step audio processing."""
    
    print("Example 3: Step-by-step approach")
    
    # Initialize the visualizer
    visualizer = AudioVisualizer(figsize=(12, 4))
    
    # Audio file to process
    audio_file = "molihua.mp4"
    
    try:
        # Step 1: Load the audio file
        print("Step 1: Loading audio file...")
        y, sr = visualizer.load_audio(audio_file)
        
        # Step 2: Display audio information
        print(f"Step 2: Audio information:")
        print(f"  - Samples: {len(y):,}")
        print(f"  - Sample rate: {sr:,} Hz")
        print(f"  - Duration: {len(y) / sr:.2f} seconds")
        print(f"  - Duration: {int(len(y) / sr // 60)}:{int(len(y) / sr % 60):02d} (mm:ss)")
        
        # Step 3: Create visualization with custom settings
        print("Step 3: Creating visualization...")
        fig = visualizer.plot_waveform(
            y, sr, 
            title=f"Step-by-Step Waveform Analysis ({len(y) / sr:.1f}s)",
            save_path="example3_waveform.png",  # Save with unique name
            show=True  # Show the final visualization
        )
        
        print("✓ Step-by-step example completed")
        print("✓ Waveform saved as example3_waveform.png")
        
    except FileNotFoundError:
        print(f"Audio file '{audio_file}' not found.")
        print("Please ensure the audio file exists in the project root.")
    except Exception as e:
        print(f"Error processing audio: {e}")


if __name__ == "__main__":
    main() 