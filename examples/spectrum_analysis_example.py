"""Example demonstrating spectrum analysis and feature extraction."""

import sys
import os
from pathlib import Path

# Add parent directory to path to import music module
sys.path.append(str(Path(__file__).parent.parent))

from music import SpectrumAnalyzer, analyze_audio_spectrum


def basic_spectrum_analysis():
    """Basic spectrum analysis example."""
    print("=== Basic Spectrum Analysis ===")
    
    # Using the convenience function
    audio_file = "molihua.mp4"  # You can change this to any audio file
    
    try:
        # Analyze audio and show plots
        features = analyze_audio_spectrum(audio_file, show_plots=True)
        
        tempo = float(features['tempo']) if hasattr(features['tempo'], '__iter__') else features['tempo']
        print(f"Tempo: {tempo:.2f} BPM")
        print(f"Average spectral centroid: {features['spectral_centroid'].mean():.2f} Hz")
        print(f"Average spectral bandwidth: {features['spectral_bandwidth'].mean():.2f} Hz")
        print(f"Average zero crossing rate: {features['zero_crossing_rate'].mean():.4f}")
        
    except FileNotFoundError:
        print(f"Audio file '{audio_file}' not found. Please place an audio file in the project root.")
    except Exception as e:
        print(f"Error: {e}")


def advanced_spectrum_analysis():
    """Advanced spectrum analysis with custom parameters and file saving."""
    print("\n=== Advanced Spectrum Analysis ===")
    
    # Using the SpectrumAnalyzer class directly
    analyzer = SpectrumAnalyzer(figsize=(14, 10))
    audio_file = "molihua.mp4"
    
    try:
        # Load audio with custom parameters
        audio_data, sr = analyzer.load_audio(audio_file, sr=22050, duration=30)  # Load first 30 seconds
        print(f"Loaded audio: {len(audio_data)} samples at {sr} Hz")
        
        # Extract spectral features
        features = analyzer.extract_spectral_features()
        
        # Create individual plots
        print("Generating spectrograms...")
        
        # Magnitude spectrogram
        analyzer.plot_spectrogram('magnitude', 
                                title='STFT Magnitude Spectrogram',
                                save_path='magnitude_spec.png',
                                show=False)
        
        # Mel spectrogram  
        analyzer.plot_spectrogram('mel',
                                title='Mel-scale Spectrogram', 
                                save_path='mel_spec.png',
                                show=False)
        
        # MFCC features
        analyzer.plot_spectrogram('mfcc',
                                title='MFCC Coefficients',
                                save_path='mfcc_features.png', 
                                show=False)
        
        # Combined spectral features plot
        analyzer.plot_spectral_features(features,
                                      save_path='spectral_features.png',
                                      show=False)
        
        print("Plots saved successfully!")
        
        # Print detailed feature statistics
        print(f"\n=== Feature Statistics ===")
        tempo = float(features['tempo']) if hasattr(features['tempo'], '__iter__') else features['tempo']
        print(f"Tempo: {tempo:.2f} BPM")
        print(f"Number of beats detected: {len(features['beats'])}")
        print(f"Spectral centroid - mean: {features['spectral_centroid'].mean():.2f} Hz, std: {features['spectral_centroid'].std():.2f}")
        print(f"Spectral bandwidth - mean: {features['spectral_bandwidth'].mean():.2f} Hz, std: {features['spectral_bandwidth'].std():.2f}")
        print(f"Spectral rolloff - mean: {features['spectral_rolloff'].mean():.2f} Hz, std: {features['spectral_rolloff'].std():.2f}")
        print(f"Zero crossing rate - mean: {features['zero_crossing_rate'].mean():.4f}, std: {features['zero_crossing_rate'].std():.4f}")
        print(f"RMS energy - mean: {features['rms'].mean():.4f}, std: {features['rms'].std():.4f}")
        print(f"Chroma features shape: {features['chroma'].shape}")
        print(f"Spectral contrast shape: {features['spectral_contrast'].shape}")
        
    except FileNotFoundError:
        print(f"Audio file '{audio_file}' not found.")
    except Exception as e:
        print(f"Error: {e}")


def batch_analysis():
    """Analyze multiple audio files in batch."""
    print("\n=== Batch Analysis ===")
    
    # Look for audio files in current directory
    audio_extensions = ['.mp3', '.wav', '.m4a', '.mp4', '.flac']
    current_dir = Path('.')
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(current_dir.glob(f'*{ext}'))
    
    if not audio_files:
        print("No audio files found in current directory.")
        return
    
    analyzer = SpectrumAnalyzer()
    
    for audio_file in audio_files[:3]:  # Limit to first 3 files
        print(f"\nAnalyzing: {audio_file.name}")
        try:
            # Analyze with automatic saving
            features = analyzer.analyze_audio_file(
                str(audio_file), 
                save_dir=f"analysis_{audio_file.stem}",
                prefix=audio_file.stem
            )
            
            tempo = float(features['tempo']) if hasattr(features['tempo'], '__iter__') else features['tempo']
            print(f"  Tempo: {tempo:.2f} BPM")
            print(f"  Avg spectral centroid: {features['spectral_centroid'].mean():.2f} Hz")
            print(f"  Analysis saved to: analysis_{audio_file.stem}/")
            
        except Exception as e:
            print(f"  Error analyzing {audio_file}: {e}")


def compare_features():
    """Compare features between different audio segments."""
    print("\n=== Feature Comparison ===")
    
    analyzer = SpectrumAnalyzer()
    audio_file = "molihua.mp4"
    
    try:
        # Analyze first 15 seconds
        analyzer.load_audio(audio_file, duration=15)
        features_part1 = analyzer.extract_spectral_features()
        
        # Analyze next 15 seconds (offset 15-30)
        # Note: librosa doesn't support offset directly, this is a simplified example
        analyzer.load_audio(audio_file, duration=30)
        full_features = analyzer.extract_spectral_features()
        
        print("Comparison of spectral features:")
        print(f"First 15s - Avg centroid: {features_part1['spectral_centroid'].mean():.2f} Hz")
        print(f"Full audio - Avg centroid: {full_features['spectral_centroid'].mean():.2f} Hz")
        tempo1 = float(features_part1['tempo']) if hasattr(features_part1['tempo'], '__iter__') else features_part1['tempo']
        tempo2 = float(full_features['tempo']) if hasattr(full_features['tempo'], '__iter__') else full_features['tempo']
        print(f"First 15s - Tempo: {tempo1:.2f} BPM") 
        print(f"Full audio - Tempo: {tempo2:.2f} BPM")
        
    except Exception as e:
        print(f"Error in comparison: {e}")


if __name__ == "__main__":
    print("Audio Spectrum Analysis Examples")
    print("=" * 40)
    
    # Run examples
    basic_spectrum_analysis()
    advanced_spectrum_analysis()
    batch_analysis()
    compare_features()
    
    print("\n" + "=" * 40)
    print("All examples completed!") 