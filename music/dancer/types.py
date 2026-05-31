import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum


class JointType(Enum):
    """机器人关节类型"""
    HEAD_YAW = "head_yaw"
    HEAD_PITCH = "head_pitch"
    SHOULDER_LEFT = "shoulder_left"
    SHOULDER_RIGHT = "shoulder_right"
    ELBOW_LEFT = "elbow_left"
    ELBOW_RIGHT = "elbow_right"
    HIP_LEFT = "hip_left"
    HIP_RIGHT = "hip_right"
    KNEE_LEFT = "knee_left"
    KNEE_RIGHT = "knee_right"
    ANKLE_LEFT = "ankle_left"
    ANKLE_RIGHT = "ankle_right"
    SHOULDER_LEFT_Z = "shoulder_left_z"    # 侧向外展（Z轴）
    SHOULDER_RIGHT_Z = "shoulder_right_z"
    TORSO_TWIST = "torso_twist"           # 上身Y轴扭转


class MovementStyle(Enum):
    """舞蹈风格"""
    ROBOTIC = "robotic"
    FLUID = "fluid"
    ENERGETIC = "energetic"
    CALM = "calm"


# ---------------------------------------------------------------------------
# Joint limits: (min_deg, max_deg)
# Chosen to be safe and achievable for a humanoid robot.
# ---------------------------------------------------------------------------
JOINT_LIMITS: Dict[str, Tuple[float, float]] = {
    "head_yaw":       (-45.0,  45.0),
    "head_pitch":     (-30.0,  30.0),
    "shoulder_left":  (-90.0,  90.0),   # negative = arm raised forward/up
    "shoulder_right": (-90.0,  90.0),
    "elbow_left":     (  0.0, 135.0),   # 0 = straight, positive = bend
    "elbow_right":    (  0.0, 135.0),
    "hip_left":       (-30.0,  30.0),   # positive = lean left
    "hip_right":      (-30.0,  30.0),   # positive = lean right
    "knee_left":      (  0.0,  90.0),   # positive = bend backward
    "knee_right":     (  0.0,  90.0),
    "ankle_left":     (-20.0,  20.0),
    "ankle_right":    (-20.0,  20.0),
    "shoulder_left_z":  (-80.0,  80.0),   # 侧向外展：正值 = 手臂向外张开
    "shoulder_right_z": (-80.0,  80.0),
    "torso_twist":      (-25.0,  25.0),   # 上身扭转：正值 = 向右扭
}


@dataclass
class Pose:
    """全身关节姿态 — 所有关节角度同时定义（单位：度）

    这是编排的核心数据类型。每个 Keyframe 包含一个 Pose，
    描述机器人在该时刻所有关节的目标角度。
    """
    head_yaw:       float = 0.0
    head_pitch:     float = 0.0
    shoulder_left:  float = 0.0   # 负值 = 手臂抬起/前伸
    shoulder_right: float = 0.0
    elbow_left:     float = 0.0   # 正值 = 肘弯曲
    elbow_right:    float = 0.0
    hip_left:       float = 0.0   # 正值 = 身体向左倾
    hip_right:      float = 0.0   # 正值 = 身体向右倾
    knee_left:      float = 0.0   # 正值 = 膝盖弯曲
    knee_right:     float = 0.0
    ankle_left:     float = 0.0
    ankle_right:    float = 0.0
    shoulder_left_z:  float = 0.0  # 左臂侧向外展（Z轴），正值向外
    shoulder_right_z: float = 0.0  # 右臂侧向外展（Z轴），正值向外
    torso_twist:      float = 0.0  # 上身Y轴扭转，正值向右


@dataclass
class Keyframe:
    """时间轴上的一个关键帧

    time:        该帧的绝对时间（秒）
    pose:        目标姿态
    transition:  到达该姿态所用的过渡时长（秒）
    gesture_name: 所使用的动作原语名称（调试/可视化用）
    """
    time:         float
    pose:         Pose
    transition:   float = 0.3
    gesture_name: str = ""


# ---------------------------------------------------------------------------
# Backward-compatible legacy types (kept for dance_executor interface)
# ---------------------------------------------------------------------------

@dataclass
class JointLimits:
    min_angle: float
    max_angle: float
    max_velocity: float
    max_acceleration: float


@dataclass
class DanceMove:
    """Legacy single-joint move — kept for DanceExecutor compatibility."""
    joint: JointType
    target_angle: float
    duration: float
    style: MovementStyle
    intensity: float