"""Audio spectrum analysis and feature extraction module."""

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import warnings

warnings.filterwarnings('ignore')


class SpectrumAnalyzer:
    """A class for analyzing audio spectrum and extracting spectral features."""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize the SpectrumAnalyzer.
        
        Args:
            figsize: Figure size for matplotlib plots as (width, height)
        """
        self.figsize = figsize
        self.audio_data = None
        self.sr = None
        self.stft = None
        self.mel_spectrogram = None
        self.mfcc = None
        
    def load_audio(self, file_path: str, sr: Optional[int] = 22050, duration: Optional[float] = None) -> Tuple[np.ndarray, int]:
        """
        Load an audio file.
        
        Args:
            file_path: Path to the audio file
            sr: Target sampling rate. Default is 22050 Hz
            duration: Duration to load in seconds. If None, loads entire file
            
        Returns:
            Tuple of (audio_data, sampling_rate)
        """
        audio_path = Path(file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            self.audio_data, self.sr = librosa.load(str(audio_path), sr=sr, duration=duration)
            return self.audio_data, self.sr
        except Exception as e:
            raise Exception(f"Failed to load audio file {file_path}: {str(e)}")
    
    def compute_stft(self, n_fft: int = 2048, hop_length: int = 512, window: str = 'hann') -> np.ndarray:
        """
        Compute Short-Time Fourier Transform (STFT).
        
        Args:
            n_fft: Length of the FFT window
            hop_length: Number of samples between successive frames
            window: Window function
            
        Returns:
            Complex-valued STFT matrix
        """
        if self.audio_data is None:
            raise ValueError("No audio data loaded. Call load_audio() first.")
            
        self.stft = librosa.stft(self.audio_data, n_fft=n_fft, hop_length=hop_length, window=window)
        return self.stft
    
    # 计算mel spectrogram更符合人耳对频率的感知
    def compute_mel_spectrogram(self, n_mels: int = 128, fmin: float = 0, fmax: Optional[float] = None) -> np.ndarray:
        """
        Compute Mel-scaled spectrogram.
        
        Args:
            n_mels: Number of Mel bands
            fmin: Minimum frequency
            fmax: Maximum frequency. If None, uses sr/2
            
        Returns:
            Mel spectrogram matrix
        """
        if self.audio_data is None:
            raise ValueError("No audio data loaded. Call load_audio() first.")
            
        if fmax is None:
            fmax = self.sr / 2
            
        self.mel_spectrogram = librosa.feature.melspectrogram(
            y=self.audio_data, sr=self.sr, n_mels=n_mels, fmin=fmin, fmax=fmax
        )
        return self.mel_spectrogram
    
    def compute_mfcc(self, n_mfcc: int = 13, n_mels: int = 128) -> np.ndarray:
        """
        Compute Mel-Frequency Cepstral Coefficients (MFCCs).
        
        Args:
            n_mfcc: Number of MFCCs to return
            n_mels: Number of Mel bands
            
        Returns:
            MFCC matrix
        """
        if self.audio_data is None:
            raise ValueError("No audio data loaded. Call load_audio() first.")
            
        self.mfcc = librosa.feature.mfcc(y=self.audio_data, sr=self.sr, n_mfcc=n_mfcc, n_mels=n_mels)
        return self.mfcc
    
    def extract_spectral_features(self) -> Dict[str, Any]:
        """
        Extract comprehensive spectral features.
        
        Returns:
            Dictionary containing various spectral features
        """
        if self.audio_data is None:
            raise ValueError("No audio data loaded. Call load_audio() first.")
        
        features = {}
        
        # Basic spectral features
        # 频谱质心，表示音频的中心频率，反映了音频的基调
        features['spectral_centroid'] = librosa.feature.spectral_centroid(y=self.audio_data, sr=self.sr)[0]
        # 频谱带宽，表示音频的频率范围, 区分噪音和纯音，噪音带宽大，纯音带宽小
        features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(y=self.audio_data, sr=self.sr)[0]
        # 频谱滚降，表示音频的频率滚降，区分高频和低频内容，语音滚降低，音乐滚升高
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(y=self.audio_data, sr=self.sr)[0]
        # 零交叉率，信号穿过零轴的次数，区分浊音和清音，清音过零率高，浊音过零率低
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(self.audio_data)[0]
        # 梅尔倒谱系数，表示音频的梅尔倒谱系数，区分噪音和语音，噪音梅尔倒谱系数高，语音梅尔倒谱系数低
        features['mfcc'] = librosa.feature.mfcc(y=self.audio_data, sr=self.sr)
        
        # Chroma features
        # 色度特征，表示音频的色度特征，将频谱映射到12个半音阶（C, C#, D, ..., B），基于八度等价的音乐理论
        features['chroma'] = librosa.feature.chroma_stft(y=self.audio_data, sr=self.sr)
        
        # Spectral contrast
        features['spectral_contrast'] = librosa.feature.spectral_contrast(y=self.audio_data, sr=self.sr)
        
        # Tonnetz
        features['tonnetz'] = librosa.feature.tonnetz(y=librosa.effects.harmonic(self.audio_data), sr=self.sr)
        
        # RMS energy
        features['rms'] = librosa.feature.rms(y=self.audio_data)[0]
        
        # Tempo and beat tracking
        tempo, beats_frames = librosa.beat.beat_track(y=self.audio_data, sr=self.sr)
        # Ensure tempo is a scalar value
        features['tempo'] = float(tempo) if hasattr(tempo, '__iter__') and len(tempo) == 1 else float(tempo)
        
        # Convert beat frames to time stamps
        beats_time = librosa.frames_to_time(beats_frames, sr=self.sr)
        
        # Store both frame indices and time stamps for flexibility
        features['beats_frames'] = beats_frames  # Frame indices (original output)
        features['beats_time'] = beats_time      # Time stamps in seconds
        features['beats'] = beats_time           # Default to time stamps for backward compatibility

        # Analysis metadata — needed by DanceChoreographer for frame lookups
        features['sr'] = self.sr
        features['hop_length'] = 512             # librosa default used throughout
        features['duration'] = len(self.audio_data) / self.sr

        return features
    
    def plot_spectrogram(self, spec_type: str = 'magnitude', title: Optional[str] = None, 
                        save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """
        Plot spectrogram.
        
        Args:
            spec_type: Type of spectrogram ('magnitude', 'mel', or 'mfcc')
            title: Title for the plot
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if spec_type == 'magnitude':
            if self.stft is None:
                self.compute_stft()
            S_db = librosa.amplitude_to_db(np.abs(self.stft), ref=np.max)
            img = librosa.display.specshow(S_db, x_axis='time', y_axis='hz', sr=self.sr, ax=ax)
            ax.set_ylabel('Frequency (Hz)')
            plt.colorbar(img, ax=ax, format='%+2.0f dB')
            if title is None:
                title = 'Magnitude Spectrogram'
                
        elif spec_type == 'mel':
            if self.mel_spectrogram is None:
                self.compute_mel_spectrogram()
            S_db = librosa.power_to_db(self.mel_spectrogram, ref=np.max)
            img = librosa.display.specshow(S_db, x_axis='time', y_axis='mel', sr=self.sr, ax=ax)
            ax.set_ylabel('Mel Frequency')
            plt.colorbar(img, ax=ax, format='%+2.0f dB')
            if title is None:
                title = 'Mel Spectrogram'
                
        elif spec_type == 'mfcc':
            if self.mfcc is None:
                self.compute_mfcc()
            img = librosa.display.specshow(self.mfcc, x_axis='time', ax=ax)
            ax.set_ylabel('MFCC Coefficients')
            plt.colorbar(img, ax=ax)
            if title is None:
                title = 'MFCC Features'
        else:
            raise ValueError("spec_type must be 'magnitude', 'mel', or 'mfcc'")
        
        ax.set_title(title)
        ax.set_xlabel('Time (s)')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        if show:
            plt.show()
            
        return fig
    
    def plot_spectral_features(self, features: Optional[Dict[str, Any]] = None, 
                              save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """
        Plot multiple spectral features in a single figure.
        
        Args:
            features: Dictionary of features. If None, computes automatically
            save_path: Optional path to save the figure
            show: Whether to display the plot
            
        Returns:
            matplotlib Figure object
        """
        if features is None:
            features = self.extract_spectral_features()
        
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        
        # Spectral centroid, bandwidth, rolloff
        times = librosa.frames_to_time(np.arange(len(features['spectral_centroid'])), sr=self.sr)
        axes[0, 0].plot(times, features['spectral_centroid'])
        axes[0, 0].set_title('Spectral Centroid')
        axes[0, 0].set_ylabel('Hz')
        
        axes[0, 1].plot(times, features['spectral_bandwidth'])
        axes[0, 1].set_title('Spectral Bandwidth')
        axes[0, 1].set_ylabel('Hz')
        
        # Chroma features
        img1 = librosa.display.specshow(features['chroma'], x_axis='time', y_axis='chroma', ax=axes[1, 0])
        axes[1, 0].set_title('Chromagram')
        plt.colorbar(img1, ax=axes[1, 0])
        
        # Spectral contrast
        img2 = librosa.display.specshow(features['spectral_contrast'], x_axis='time', ax=axes[1, 1])
        axes[1, 1].set_title('Spectral Contrast')
        plt.colorbar(img2, ax=axes[1, 1])
        
        # Zero crossing rate
        zcr_times = librosa.frames_to_time(np.arange(len(features['zero_crossing_rate'])), sr=self.sr)
        axes[2, 0].plot(zcr_times, features['zero_crossing_rate'])
        axes[2, 0].set_title('Zero Crossing Rate')
        axes[2, 0].set_ylabel('Rate')
        axes[2, 0].set_xlabel('Time (s)')
        
        # RMS energy
        rms_times = librosa.frames_to_time(np.arange(len(features['rms'])), sr=self.sr)
        axes[2, 1].plot(rms_times, features['rms'])
        axes[2, 1].set_title('RMS Energy')
        axes[2, 1].set_ylabel('Amplitude')
        axes[2, 1].set_xlabel('Time (s)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        if show:
            plt.show()
            
        return fig
    
    def analyze_audio_file(self, file_path: str, save_dir: Optional[str] = None, 
                          prefix: str = "spectrum_analysis") -> Dict[str, Any]:
        """
        Complete analysis of an audio file with visualization.
        
        Args:
            file_path: Path to the audio file
            save_dir: Directory to save plots. If None, doesn't save
            prefix: Prefix for saved files
            
        Returns:
            Dictionary containing all extracted features
        """
        # Load audio
        self.load_audio(file_path)
        
        # Extract features
        features = self.extract_spectral_features()
        
        # Create save paths if needed
        if save_dir:
            save_dir_path = Path(save_dir)
            save_dir_path.mkdir(exist_ok=True)
            
            mag_save_path = save_dir_path / f"{prefix}_magnitude_spectrogram.png"
            mel_save_path = save_dir_path / f"{prefix}_mel_spectrogram.png"
            mfcc_save_path = save_dir_path / f"{prefix}_mfcc.png"
            features_save_path = save_dir_path / f"{prefix}_spectral_features.png"
        else:
            mag_save_path = mel_save_path = mfcc_save_path = features_save_path = None
        
        # Generate and save plots
        filename = Path(file_path).stem
        
        self.plot_spectrogram('magnitude', 
                            title=f'Magnitude Spectrogram - {filename}',
                            save_path=mag_save_path, show=False)
        
        self.plot_spectrogram('mel', 
                            title=f'Mel Spectrogram - {filename}',
                            save_path=mel_save_path, show=False)
        
        self.plot_spectrogram('mfcc', 
                            title=f'MFCC Features - {filename}',
                            save_path=mfcc_save_path, show=False)
        
        self.plot_spectral_features(features, 
                                  save_path=features_save_path, show=False)
        
        return features


def analyze_audio_spectrum(file_path: str, save_dir: Optional[str] = None, 
                          show_plots: bool = True) -> Dict[str, Any]:
    """
    Convenience function to analyze audio spectrum and generate visualizations.
    
    Args:
        file_path: Path to the audio file
        save_dir: Directory to save plots. If None, doesn't save
        show_plots: Whether to display plots
        
    Returns:
        Dictionary containing extracted spectral features
    """
    analyzer = SpectrumAnalyzer()
    features = analyzer.analyze_audio_file(file_path, save_dir)
    
    if show_plots:
        filename = Path(file_path).stem
        analyzer.plot_spectrogram('magnitude', title=f'Magnitude Spectrogram - {filename}')
        analyzer.plot_spectrogram('mel', title=f'Mel Spectrogram - {filename}')
        analyzer.plot_spectral_features(features)
    
    return features