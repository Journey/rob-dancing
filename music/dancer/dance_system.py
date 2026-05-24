"""DanceSystem — high-level pipeline: audio file → keyframe JSON.

Usage (Python API):
    system = DanceSystem()
    data = system.create_dance_from_music("song.mp3")
    system.save_dance_sequence(data, "song_dance.json")

The output JSON format is:
    {
      "audio_file": "...",
      "duration": 60.0,
      "tempo": 99.38,
      "keyframes": [
        {"time": 1.857, "transition": 0.33, "gesture": "side_step_left",
         "pose": {"head_yaw": 0, "shoulder_left": -20, ...}},
        ...
      ]
    }
"""

from typing import Dict, Optional
from dataclasses import asdict
import json

from .dance_choreographer import DanceChoreographer
from .dance_executor import SimulatedExecutor
from ..analyzer import SpectrumAnalyzer


class DanceSystem:
    """Music-driven dance choreography system."""

    def __init__(self, robot_config: Optional[Dict] = None):
        self.spectrum_analyzer = SpectrumAnalyzer()
        self.choreographer = DanceChoreographer(robot_config or {})
        self.executor = SimulatedExecutor()

    def create_dance_from_music(self, audio_file: str) -> Dict:
        """Full pipeline: analyse audio → choreograph → return dance dict."""
        print(f"[DanceSystem] Analysing audio: {audio_file}")
        audio_features = self.spectrum_analyzer.analyze_audio_file(audio_file)

        print(f"[DanceSystem] Tempo: {audio_features['tempo']:.1f} BPM  "
              f"| Beats: {len(audio_features['beats_time'])}  "
              f"| Duration: {audio_features['duration']:.1f}s")

        keyframes = self.choreographer.choreograph_dance(audio_features)
        print(f"[DanceSystem] Generated {len(keyframes)} keyframes")

        return {
            "audio_file": audio_file,
            "duration":   float(audio_features["duration"]),
            "tempo":      float(audio_features["tempo"]),
            "keyframes": [
                {
                    "time":       round(kf.time, 4),
                    "transition": round(kf.transition, 4),
                    "gesture":    kf.gesture_name,
                    "pose":       {k: round(v, 2) for k, v in asdict(kf.pose).items()},
                }
                for kf in keyframes
            ],
        }

    def save_dance_sequence(self, dance_data: Dict, output_file: str) -> None:
        """Serialise dance_data to JSON."""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(dance_data, f, indent=2, ensure_ascii=False)
        print(f"[DanceSystem] Saved → {output_file}")

    def visualize_dance(self, dance_data: Dict) -> None:
        """Quick matplotlib preview of keyframe joint angles over time."""
        import matplotlib.pyplot as plt

        keyframes = dance_data.get("keyframes", [])
        if not keyframes:
            print("[DanceSystem] No keyframes to visualise.")
            return

        joint_names = list(keyframes[0]["pose"].keys())
        times = [kf["time"] for kf in keyframes]
        angles = {j: [kf["pose"][j] for kf in keyframes] for j in joint_names}

        cols = 4
        rows = -(-len(joint_names) // cols)   # ceiling division
        fig, axes = plt.subplots(rows, cols, figsize=(16, rows * 3))
        axes = axes.flatten()

        for i, joint in enumerate(joint_names):
            axes[i].plot(times, angles[joint], linewidth=1.2)
            axes[i].set_title(joint, fontsize=9)
            axes[i].set_xlabel("t (s)", fontsize=7)
            axes[i].set_ylabel("deg", fontsize=7)
            axes[i].axhline(0, color="gray", linewidth=0.5, linestyle="--")
            axes[i].tick_params(labelsize=7)

        for j in range(len(joint_names), len(axes)):
            axes[j].set_visible(False)

        plt.suptitle(
            f"{dance_data.get('audio_file', 'unknown')}  "
            f"| {dance_data.get('tempo', 0):.1f} BPM  "
            f"| {len(keyframes)} keyframes",
            fontsize=10,
        )
        plt.tight_layout()
        plt.show()

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
