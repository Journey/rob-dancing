from typing import List
from .types import DanceMove, JointType, MovementStyle
import numpy as np

class FeatureToActionMapper:
    """音乐特征到动作的映射器"""
    
    def __init__(self):
        self.beat_weight = 0.4      # 节拍权重
        self.frequency_weight = 0.3  # 频率权重
        self.volume_weight = 0.2     # 音量权重
        self.timbre_weight = 0.1     # 音色权重
    
    def map_beat_to_core_movement(self, beat_times: List[float], 
                                 tempo: float) -> List[DanceMove]:
        """节拍映射到核心律动"""
        moves = []
        
        for beat_time in beat_times:
            # 根据节拍强度调整动作
            intensity = self._calculate_beat_intensity(beat_time, tempo)
            
            # 核心律动：髋关节和膝关节
            moves.extend([
                DanceMove(
                    joint=JointType.HIP_LEFT,
                    target_angle=15 * intensity,
                    duration=60.0 / tempo,  # 基于速度的持续时间
                    style=MovementStyle.ENERGETIC,
                    intensity=intensity,
                    time=beat_time
                ),
                DanceMove(
                    joint=JointType.HIP_RIGHT,
                    target_angle=-15 * intensity,
                    duration=60.0 / tempo,
                    style=MovementStyle.ENERGETIC,
                    intensity=intensity,
                    time=beat_time
                ),
                DanceMove(
                    joint=JointType.KNEE_LEFT,
                    target_angle=30 * intensity,
                    duration=60.0 / tempo,
                    style=MovementStyle.ENERGETIC,
                    intensity=intensity,
                    time=beat_time
                ),
                DanceMove(
                    joint=JointType.KNEE_RIGHT,
                    target_angle=30 * intensity,
                    duration=60.0 / tempo,
                    style=MovementStyle.ENERGETIC,
                    intensity=intensity,
                    time=beat_time
                )
            ])
        
        return moves
    
    def map_frequency_to_spatial_movement(self, spectral_centroid: np.ndarray,
                                        time_frames: np.ndarray) -> List[DanceMove]:
        """频率映射到空间位置"""
        moves = []
        
        for i, centroid in enumerate(spectral_centroid):
            time = time_frames[i]
            
            # 低频控制下肢
            if centroid < 1000:  # 低频
                moves.extend(self._generate_lower_body_moves(time, centroid))
            
            # 中频控制躯干
            elif centroid < 4000:  # 中频
                moves.extend(self._generate_torso_moves(time, centroid))
            
            # 高频控制上肢和头部
            else:  # 高频
                moves.extend(self._generate_upper_body_moves(time, centroid))
        
        return moves
    
    def map_volume_to_amplitude(self, rms_energy: np.ndarray,
                               time_frames: np.ndarray) -> List[DanceMove]:
        """音量映射到动作幅度"""
        moves = []
        
        for i, energy in enumerate(rms_energy):
            time = time_frames[i]
            amplitude_factor = np.clip(energy / np.max(rms_energy), 0.1, 1.0)
            
            # 音量影响所有关节的动作幅度
            moves.extend([
                DanceMove(
                    joint=JointType.SHOULDER_LEFT,
                    target_angle=45 * amplitude_factor,
                    duration=0.1,
                    style=MovementStyle.ENERGETIC,
                    intensity=amplitude_factor,
                    time=time
                ),
                DanceMove(
                    joint=JointType.SHOULDER_RIGHT,
                    target_angle=-45 * amplitude_factor,
                    duration=0.1,
                    style=MovementStyle.ENERGETIC,
                    intensity=amplitude_factor,
                    time=time
                )
            ])
        
        return moves
    
    def map_timbre_to_style(self, chroma_features: np.ndarray,
                           spectral_contrast: np.ndarray) -> List[DanceMove]:
        """音色映射到动作风格"""
        moves = []
        
        # 分析主要和弦
        dominant_chord = self._analyze_dominant_chord(chroma_features)
        
        # 根据和弦类型选择风格
        if dominant_chord in ['C', 'F', 'G']:  # 大调和弦
            style = MovementStyle.ENERGETIC
        elif dominant_chord in ['Am', 'Dm', 'Em']:  # 小调和弦
            style = MovementStyle.CALM
        else:
            style = MovementStyle.FLUID
        
        # 根据频谱对比度调整风格
        contrast_mean = np.mean(spectral_contrast)
        if contrast_mean > 0.7:
            style = MovementStyle.ROBOTIC
        elif contrast_mean < 0.3:
            style = MovementStyle.FLUID
        
        return moves
    
    def _calculate_beat_intensity(self, beat_time: float, tempo: float) -> float:
        """计算节拍强度"""
        # 基于速度的强度计算
        base_intensity = min(tempo / 120.0, 1.0)  # 标准化到0-1
        return base_intensity
    
    def _generate_lower_body_moves(self, time: float, frequency: float) -> List[DanceMove]:
        """生成下肢动作"""
        return [
            DanceMove(
                joint=JointType.HIP_LEFT,
                target_angle=20 * (frequency / 1000),
                duration=0.2,
                style=MovementStyle.FLUID,
                intensity=0.6,
                time=time
            ),
            DanceMove(
                joint=JointType.KNEE_LEFT,
                target_angle=40 * (frequency / 1000),
                duration=0.2,
                style=MovementStyle.FLUID,
                intensity=0.6,
                time=time
            )
        ]
    
    def _generate_torso_moves(self, time: float, frequency: float) -> List[DanceMove]:
        """生成躯干动作"""
        return [
            DanceMove(
                joint=JointType.HIP_LEFT,
                target_angle=15 * (frequency / 4000),
                duration=0.3,
                style=MovementStyle.FLUID,
                intensity=0.5,
                time=time
            ),
            DanceMove(
                joint=JointType.HIP_RIGHT,
                target_angle=-15 * (frequency / 4000),
                duration=0.3,
                style=MovementStyle.FLUID,
                intensity=0.5,
                time=time
            )
        ]
    
    def _generate_upper_body_moves(self, time: float, frequency: float) -> List[DanceMove]:
        """生成上肢动作"""
        return [
            DanceMove(
                joint=JointType.SHOULDER_LEFT,
                target_angle=30 * (frequency / 8000),
                duration=0.15,
                style=MovementStyle.ENERGETIC,
                intensity=0.7,
                time=time
            ),
            DanceMove(
                joint=JointType.HEAD_YAW,
                target_angle=20 * (frequency / 8000),
                duration=0.15,
                style=MovementStyle.ENERGETIC,
                intensity=0.7,
                time=time
            )
        ]
    
    def _analyze_dominant_chord(self, chroma_features: np.ndarray) -> str:
        """分析主要和弦"""
        # 简化的和弦分析
        chroma_sum = np.sum(chroma_features, axis=1)
        dominant_note = np.argmax(chroma_sum)
        
        chord_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return chord_names[dominant_note]