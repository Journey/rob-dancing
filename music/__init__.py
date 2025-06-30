"""Music analysis and visualization package."""

__version__ = "0.1.0"

from .audio_visualizer import AudioVisualizer, load_and_plot_audio
from .spectrum_analyzer import SpectrumAnalyzer, analyze_audio_spectrum

__all__ = [
    'AudioVisualizer',
    'load_and_plot_audio', 
    'SpectrumAnalyzer',
    'analyze_audio_spectrum'
] 