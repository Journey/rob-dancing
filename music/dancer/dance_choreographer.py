from typing import Dict, List
from .feature_to_action import FeatureToActionMapper
from .types import DanceMove, JointType, MovementStyle
import numpy as np

class DanceChoreographer:

    """舞蹈编排器"""
    
    def __init__(self, robot_config: Dict):
        self.robot_config = robot_config
        self.mapper = FeatureToActionMapper()
        self.joint_limits = self._initialize_joint_limits()
        self.current_pose = self._initialize_pose()
        
    def choreograph_dance(self, audio_features: Dict) -> List[DanceMove]:
        """编排完整舞蹈"""
        dance_sequence = []
        
        # 1. 节拍驱动的核心律动
        beat_moves = self.mapper.map_beat_to_core_movement(
            audio_features['beats_time'],
            audio_features['tempo']
        )
        dance_sequence.extend(beat_moves)
        
        # 2. 频率驱动的空间动作
        freq_moves = self.mapper.map_frequency_to_spatial_movement(
            audio_features['spectral_centroid'],
            np.arange(len(audio_features['spectral_centroid'])) * 0.1
        )
        dance_sequence.extend(freq_moves)
        
        # 3. 音量驱动的动作幅度
        volume_moves = self.mapper.map_volume_to_amplitude(
            audio_features['rms'],
            np.arange(len(audio_features['rms'])) * 0.1
        )
        dance_sequence.extend(volume_moves)
        
        # 4. 音色驱动的动作风格
        timbre_moves = self.mapper.map_timbre_to_style(
            audio_features['chroma'],
            audio_features['spectral_contrast']
        )
        dance_sequence.extend(timbre_moves)
        
        # 5. 优化舞蹈序列
        optimized_sequence = self._optimize_dance_sequence(dance_sequence)
        
        return optimized_sequence
    
    def _optimize_dance_sequence(self, moves: List[DanceMove]) -> List[DanceMove]:
        """优化舞蹈序列"""
        optimized_moves = []
        
        # 按时间排序
        moves.sort(key=lambda x: getattr(x, 'time', 0))
        
        for i, move in enumerate(moves):
            # 检查关节限制
            if self._check_joint_limits(move):
                # 添加平滑过渡
                if i > 0:
                    transition_moves = self._create_transition(
                        optimized_moves[-1], move
                    )
                    optimized_moves.extend(transition_moves)
                
                optimized_moves.append(move)
        
        return optimized_moves
    
    def _check_joint_limits(self, move: DanceMove) -> bool:
        """检查关节限制"""
        limits = self.joint_limits[move.joint]
        
        # 检查角度限制
        if not (limits.min_angle <= move.target_angle <= limits.max_angle):
            return False
        
        # 检查速度限制
        current_angle = self.current_pose[move.joint]
        velocity = abs(move.target_angle - current_angle) / move.duration
        
        if velocity > limits.max_velocity:
            return False
        
        return True
    
    def _create_transition(self, prev_move: DanceMove, 
                          next_move: DanceMove) -> List[DanceMove]:
        """创建动作间的平滑过渡"""
        transitions = []
        
        # 如果两个动作涉及同一关节，创建过渡
        if prev_move.joint == next_move.joint:
            transition_duration = 0.1  # 100ms过渡时间
            
            # 计算中间角度
            mid_angle = (prev_move.target_angle + next_move.target_angle) / 2
            
            transition_move = DanceMove(
                joint=prev_move.joint,
                target_angle=mid_angle,
                duration=transition_duration,
                style=MovementStyle.FLUID,
                intensity=(prev_move.intensity + next_move.intensity) / 2,
                time=next_move.time - transition_duration
            )
            
            transitions.append(transition_move)
        
        return transitions
    
    def _ensure_balance(self, moves: List[DanceMove]) -> List[DanceMove]:
        """确保动作平衡性"""
        balanced_moves = []
        
        for move in moves:
            # 检查是否需要平衡动作
            if self._needs_balance(move):
                balance_move = self._create_balance_move(move)
                balanced_moves.append(balance_move)
            
            balanced_moves.append(move)
        
        return balanced_moves
    
    def _needs_balance(self, move: DanceMove) -> bool:
        """判断是否需要平衡动作"""
        # 单侧动作需要平衡
        unilateral_joints = [
            JointType.SHOULDER_LEFT, JointType.SHOULDER_RIGHT,
            JointType.HIP_LEFT, JointType.HIP_RIGHT,
            JointType.KNEE_LEFT, JointType.KNEE_RIGHT
        ]
        
        return move.joint in unilateral_joints
    
    def _create_balance_move(self, original_move: DanceMove) -> DanceMove:
        """创建平衡动作"""
        # 找到对应的对称关节
        balance_joint_map = {
            JointType.SHOULDER_LEFT: JointType.SHOULDER_RIGHT,
            JointType.SHOULDER_RIGHT: JointType.SHOULDER_LEFT,
            JointType.HIP_LEFT: JointType.HIP_RIGHT,
            JointType.HIP_RIGHT: JointType.HIP_LEFT,
            JointType.KNEE_LEFT: JointType.KNEE_RIGHT,
            JointType.KNEE_RIGHT: JointType.KNEE_LEFT
        }
        
        balance_joint = balance_joint_map.get(original_move.joint)
        if balance_joint:
            return DanceMove(
                joint=balance_joint,
                target_angle=-original_move.target_angle * 0.5,  # 对称但幅度较小
                duration=original_move.duration,
                style=original_move.style,
                intensity=original_move.intensity * 0.7
            )
        
        return None
    
    def _initialize_joint_limits(self) -> Dict[JointType, 'JointLimits']:
        """初始化关节限制"""
        from .types import JointLimits
        
        joint_limits = {}
        config_limits = self.robot_config.get('joint_limits', {})
        
        for joint_type in JointType:
            joint_name = joint_type.value
            if joint_name in config_limits:
                limits = config_limits[joint_name]
                joint_limits[joint_type] = JointLimits(
                    min_angle=limits.get('min', -90),
                    max_angle=limits.get('max', 90),
                    max_velocity=limits.get('max_velocity', 180),  # 度/秒
                    max_acceleration=limits.get('max_acceleration', 360)  # 度/秒²
                )
            else:
                # 默认限制
                joint_limits[joint_type] = JointLimits(
                    min_angle=-90,
                    max_angle=90,
                    max_velocity=180,
                    max_acceleration=360
                )
        
        return joint_limits
    
    def _initialize_pose(self) -> Dict[JointType, float]:
        """初始化机器人姿态"""
        pose = {}
        for joint_type in JointType:
            pose[joint_type] = 0.0  # 初始角度为0
        return pose