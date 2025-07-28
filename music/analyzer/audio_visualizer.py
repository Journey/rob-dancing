"""Audio visualization utilities using librosa and matplotlib."""

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Optional, Tuple


class AudioVisualizer:
    """A class for visualizing audio files using librosa and matplotlib."""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 4)):
        """
        Initialize the AudioVisualizer.
        
        Args:
            figsize: Figure size for matplotlib plots as (width, height)
        """
        self.figsize = figsize
    
    def load_audio(self, file_path: str, sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """
        Load an audio file using librosa.
        
        Args:
            file_path: Path to the audio file
            sr: Target sampling rate. If None, uses the native sampling rate
            
        Returns:
            Tuple of (audio_data, sampling_rate)
            
        Raises:
            FileNotFoundError: If the audio file doesn't exist
            Exception: If the file cannot be loaded
        """
        audio_path = Path(file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            y, sr = librosa.load(str(audio_path), sr=sr)
            return y, sr
        except Exception as e:
            raise Exception(f"Failed to load audio file {file_path}: {str(e)}")
    
    def plot_waveform(self, y: np.ndarray, sr: int, title: str = "Audio Waveform", 
                     save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """
        Plot the waveform of an audio signal.
        
        Args:
            y: Audio time series
            sr: Sampling rate
            title: Title for the plot
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            matplotlib Figure object
        """
        fig = plt.figure(figsize=self.figsize)
        librosa.display.waveshow(y, sr=sr)
        plt.title(title)
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
    
    def visualize_audio_file(self, file_path: str, title: Optional[str] = None,
                            save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """
        Load and visualize an audio file in one step.
        
        Args:
            file_path: Path to the audio file
            title: Title for the plot. If None, uses filename
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            matplotlib Figure object
        """
        y, sr = self.load_audio(file_path)
        
        if title is None:
            title = f"Waveform - {Path(file_path).name}"
        
        return self.plot_waveform(y, sr, title=title, save_path=save_path, show=show)


def load_and_plot_audio(file_path: str, figsize: Tuple[int, int] = (12, 4), 
                       title: Optional[str] = None, save_path: Optional[str] = None, show: bool = True) -> None:
    """
    Convenience function to load and plot an audio file.
    
    This is a simplified interface that matches the original code structure.
    
    Args:
        file_path: Path to the audio file
        figsize: Figure size as (width, height)
        title: Title for the plot
        save_path: Optional path to save the figure
        show: Whether to display the plot
    """
    visualizer = AudioVisualizer(figsize=figsize)
    visualizer.visualize_audio_file(file_path, title=title, save_path=save_path, show=show)
