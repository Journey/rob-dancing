"""Simple example that matches the original code exactly."""

import librosa
import librosa.display
import matplotlib.pyplot as plt

# Your original code
y, sr = librosa.load('song.mp3')
plt.figure(figsize=(12, 4))
librosa.display.waveshow(y, sr=sr)  # 绘制波形图
plt.title('Audio Waveform')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.tight_layout()
plt.show() 