"""Music analysis and visualization package."""

__version__ = "0.1.0"

from .analyzer import AudioVisualizer, load_and_plot_audio, SpectrumAnalyzer, analyze_audio_spectrum

__all__ = [
    'AudioVisualizer',
    'load_and_plot_audio', 
    'SpectrumAnalyzer',
    'analyze_audio_spectrum'
] 