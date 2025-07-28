"""Simple demo script for spectrum analysis."""

from music import SpectrumAnalyzer
import matplotlib.pyplot as plt


def main():
    """Demonstrate spectrum analysis with the provided audio file."""
    print("Starting spectrum analysis demo...")
    
    # Create analyzer instance
    analyzer = SpectrumAnalyzer()
    
    # Audio file path (using the existing file in the project)
    audio_file = "molihua.mp4"
    
    try:
        print(f"Loading audio file: {audio_file}")
        
        # Perform complete analysis and save results
        features = analyzer.analyze_audio_file(
            audio_file, 
            save_dir="spectrum_results",
            prefix="molihua"
        )
        
        # Print some key features
        print("\n=== Analysis Results ===")
        # Handle tempo as it might be a scalar or array
        tempo = features['tempo'] if hasattr(features['tempo'], '__len__') and len(features['tempo']) == 1 else features['tempo']
        if hasattr(tempo, '__iter__') and not isinstance(tempo, str):
            tempo = float(tempo[0]) if len(tempo) > 0 else float(tempo)
        else:
            tempo = float(tempo)
        
        print(f"Tempo: {tempo:.2f} BPM")
        print(f"Average spectral centroid: {features['spectral_centroid'].mean():.2f} Hz")
        print(f"Average spectral bandwidth: {features['spectral_bandwidth'].mean():.2f} Hz")
        print(f"Average RMS energy: {features['rms'].mean():.4f}")
        print(f"Average zero crossing rate: {features['zero_crossing_rate'].mean():.4f}")
        
        print(f"\nSpectrum analysis plots saved to 'spectrum_results/' directory")
        print("Generated files:")
        print("- molihua_magnitude_spectrogram.png")
        print("- molihua_mel_spectrogram.png") 
        print("- molihua_mfcc.png")
        print("- molihua_spectral_features.png")
        
        # Also show one plot interactively
        print("\nDisplaying Mel spectrogram...")
        analyzer.plot_spectrogram('mel', title='Mel Spectrogram - 茉莉花 (Molihua)', show=True)
        
    except FileNotFoundError:
        print(f"Error: Audio file '{audio_file}' not found in the current directory.")
        print("Please make sure the audio file exists.")
    except Exception as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    main() 