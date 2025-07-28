from typing import Dict
from .dance_choreographer import DanceChoreographer
from .dance_executor import DanceExecutor
from ..analyzer import SpectrumAnalyzer
from .types import JointType
import json

class DanceSystem:
    """音乐驱动舞蹈系统"""
    
    def __init__(self, robot_config: Dict):
        self.spectrum_analyzer = SpectrumAnalyzer()
        self.choreographer = DanceChoreographer(robot_config)
        self.executor = DanceExecutor(robot_interface=None)  # 需要实际的机器人接口
        
    def create_dance_from_music(self, audio_file: str) -> Dict:
        """从音乐文件创建舞蹈"""
        # 1. 分析音乐特征
        audio_features = self.spectrum_analyzer.analyze_audio_file(audio_file)
        
        # 2. 编排舞蹈
        dance_sequence = self.choreographer.choreograph_dance(audio_features)
        
        # 3. 生成舞蹈文件
        dance_data = {
            'audio_file': audio_file,
            'duration': audio_features.get('duration', 0),
            'tempo': audio_features.get('tempo', 120),
            'dance_sequence': [
                {
                    'joint': move.joint.value,
                    'target_angle': move.target_angle,
                    'duration': move.duration,
                    'style': move.style.value,
                    'intensity': move.intensity,
                    'time': getattr(move, 'time', 0)
                }
                for move in dance_sequence
            ]
        }
        
        return dance_data
    
    def save_dance_sequence(self, dance_data: Dict, output_file: str):
        """保存舞蹈序列"""
        with open(output_file, 'w') as f:
            json.dump(dance_data, f, indent=2)
    
    def visualize_dance(self, dance_data: Dict):
        """可视化舞蹈"""
        # 创建舞蹈可视化
        import matplotlib.pyplot as plt
        
        times = []
        joint_angles = {joint.value: [] for joint in JointType}
        
        current_time = 0
        for move in dance_data['dance_sequence']:
            times.append(current_time)
            joint_angles[move['joint']].append(move['target_angle'])
            current_time += move['duration']
        
        # 绘制关节角度变化
        fig, axes = plt.subplots(3, 4, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, (joint_name, angles) in enumerate(joint_angles.items()):
            if i < len(axes):
                axes[i].plot(times[:len(angles)], angles)
                axes[i].set_title(joint_name)
                axes[i].set_xlabel('Time (s)')
                axes[i].set_ylabel('Angle (deg)')
        
        plt.tight_layout()
        plt.show()