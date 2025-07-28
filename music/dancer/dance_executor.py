from typing import List, Dict
from .types import DanceMove

class DanceExecutor:
    """舞蹈执行器"""
    
    def __init__(self, robot_interface):
        self.robot_interface = robot_interface
        self.current_time = 0.0
        self.execution_queue = []
        
    def execute_dance(self, dance_sequence: List[DanceMove], 
                     audio_duration: float):
        """执行舞蹈序列"""
        # 将舞蹈动作转换为机器人指令
        robot_commands = self._convert_to_robot_commands(dance_sequence)
        
        # 按时间执行
        for command in robot_commands:
            self.robot_interface.execute_command(command)
            
    def _convert_to_robot_commands(self, dance_sequence: List[DanceMove]) -> List[Dict]:
        """转换为机器人指令"""
        commands = []
        
        for move in dance_sequence:
            command = {
                'joint': move.joint.value,
                'target_angle': move.target_angle,
                'duration': move.duration,
                'style': move.style.value,
                'intensity': move.intensity
            }
            commands.append(command)
        
        return commands