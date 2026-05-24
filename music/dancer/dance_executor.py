from typing import List, Dict, Optional
from .types import DanceMove


class DanceExecutor:
    """Base dance executor — wraps a real robot interface."""

    def __init__(self, robot_interface: Optional[object] = None):
        self.robot_interface = robot_interface
        self.current_time = 0.0
        self.execution_queue: List[Dict] = []

    def execute_dance(self, dance_sequence: List[DanceMove],
                      audio_duration: float) -> None:
        """Execute a dance sequence via the robot interface."""
        if self.robot_interface is None:
            raise RuntimeError(
                "No robot interface configured. "
                "Use SimulatedExecutor for dry-run testing, or pass a real "
                "robot_interface that implements execute_command()."
            )
        commands = self._convert_to_robot_commands(dance_sequence)
        for command in commands:
            self.robot_interface.execute_command(command)

    def _convert_to_robot_commands(self, dance_sequence: List[DanceMove]) -> List[Dict]:
        commands = []
        for move in dance_sequence:
            commands.append({
                "joint":        move.joint.value,
                "target_angle": move.target_angle,
                "duration":     move.duration,
                "style":        move.style.value,
                "intensity":    move.intensity,
            })
        return commands


class SimulatedExecutor(DanceExecutor):
    """Dry-run executor — prints commands to stdout, no hardware required."""

    def __init__(self) -> None:
        super().__init__(robot_interface=None)

    def execute_dance(self, dance_sequence: List[DanceMove],
                      audio_duration: float) -> None:
        print(f"[SIM] Starting dance: {len(dance_sequence)} moves, "
              f"duration={audio_duration:.1f}s")
        for cmd in self._convert_to_robot_commands(dance_sequence):
            print(f"[SIM]   {cmd['joint']:20s} → {cmd['target_angle']:6.1f}°  "
                  f"dur={cmd['duration']:.3f}s  ({cmd['style']})")
        print("[SIM] Dance execution complete.")
