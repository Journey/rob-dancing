import numpy as np
from typing import Dict
from dataclasses import dataclass
from enum import Enum

class JointType(Enum):
    """机器人关节类型"""
    HEAD_YAW = "head_yaw"      # 头部左右转动
    HEAD_PITCH = "head_pitch"   # 头部上下点头
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

class MovementStyle(Enum):
    """舞蹈风格"""
    ROBOTIC = "robotic"        # 机械风格
    FLUID = "fluid"            # 流畅风格
    ENERGETIC = "energetic"     # 活力风格
    CALM = "calm"              # 平静风格

@dataclass
class JointLimits:
    """关节限制"""
    min_angle: float
    max_angle: float
    max_velocity: float
    max_acceleration: float

@dataclass
class DanceMove:
    """舞蹈动作"""
    joint: JointType
    target_angle: float
    duration: float
    style: MovementStyle
    intensity: float  # 0-1, 动作强度
    time: float