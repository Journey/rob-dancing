"""Gesture Library — robot-friendly named dance poses.

Each gesture is a function that returns a Pose (delta from neutral).
All values are in degrees and respect JOINT_LIMITS.

Design principles:
  - Simple, achievable moves for a humanoid robot with 12 DOF
  - Bilateral symmetry where appropriate
  - Balance constraints: arm raises are counterbalanced by opposite hip/knee
  - Deterministic: same intensity → same pose (no randomness here)
"""

from dataclasses import asdict
from .types import Pose, JOINT_LIMITS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clamp_pose(pose: Pose) -> Pose:
    """Clamp all joint values to their hardware limits."""
    d = asdict(pose)
    for joint, (lo, hi) in JOINT_LIMITS.items():
        d[joint] = max(lo, min(hi, d[joint]))
    return Pose(**d)


def blend_poses(base: Pose, overlay: Pose, weight: float = 1.0) -> Pose:
    """Additively blend overlay onto base, then clamp.

    weight=1.0 → full overlay added; weight=0.5 → half overlay.
    """
    bd = asdict(base)
    od = asdict(overlay)
    result = {k: bd[k] + od[k] * weight for k in bd}
    return clamp_pose(Pose(**result))


def lerp_pose(a: Pose, b: Pose, t: float) -> Pose:
    """Linear interpolation between two poses. t=0 → a, t=1 → b."""
    t = max(0.0, min(1.0, t))
    ad, bd = asdict(a), asdict(b)
    result = {k: ad[k] * (1.0 - t) + bd[k] * t for k in ad}
    return Pose(**result)


# ---------------------------------------------------------------------------
# Core gestures
# ---------------------------------------------------------------------------

def home() -> Pose:
    """Neutral standing pose — all joints at zero."""
    return Pose()


def head_bob(intensity: float = 1.0) -> Pose:
    """Head nods forward on beat."""
    return Pose(head_pitch=15.0 * intensity)


def head_bob_back(intensity: float = 1.0) -> Pose:
    """Head tilts back slightly (after nod)."""
    return Pose(head_pitch=-8.0 * intensity)


def head_sway_left(intensity: float = 1.0) -> Pose:
    """Head turns left — follows melody direction."""
    return Pose(head_yaw=-20.0 * intensity)


def head_sway_right(intensity: float = 1.0) -> Pose:
    """Head turns right."""
    return Pose(head_yaw=20.0 * intensity)


# ---------------------------------------------------------------------------
# Lower body — beat-driven stepping
# ---------------------------------------------------------------------------

def side_step_left(intensity: float = 1.0) -> Pose:
    """Weight shift to left. Hip tilts left, right knee lifts, right ankle tilts.
    This is the primary on-beat pose for even beats.
    """
    return clamp_pose(Pose(
        hip_left=18.0 * intensity,
        hip_right=-8.0 * intensity,
        knee_right=15.0 * intensity,
        ankle_right=8.0 * intensity,   # lifted foot tilt
        head_yaw=-10.0 * intensity,
    ))


def side_step_right(intensity: float = 1.0) -> Pose:
    """Weight shift to right. Hip tilts right, left knee lifts, left ankle tilts."""
    return clamp_pose(Pose(
        hip_right=18.0 * intensity,
        hip_left=-8.0 * intensity,
        knee_left=15.0 * intensity,
        ankle_left=8.0 * intensity,    # lifted foot tilt
        head_yaw=10.0 * intensity,
    ))


def knee_pump(intensity: float = 1.0) -> Pose:
    """Both knees bend simultaneously — strong beat accent, lower body focus."""
    return clamp_pose(Pose(
        knee_left=28.0 * intensity,
        knee_right=28.0 * intensity,
        hip_left=6.0 * intensity,
        hip_right=6.0 * intensity,
        head_pitch=8.0 * intensity,
    ))


def body_lean_left(intensity: float = 1.0) -> Pose:
    """Whole body leans left — melodic sway. Bigger amplitude for visible phrasing."""
    return clamp_pose(Pose(
        hip_left=20.0 * intensity,
        hip_right=-6.0 * intensity,
        head_yaw=-10.0 * intensity,
        shoulder_left=18.0 * intensity,
        shoulder_right=-12.0 * intensity,
        knee_right=8.0 * intensity,
    ))


def body_lean_right(intensity: float = 1.0) -> Pose:
    """Whole body leans right."""
    return clamp_pose(Pose(
        hip_right=20.0 * intensity,
        hip_left=-6.0 * intensity,
        head_yaw=10.0 * intensity,
        shoulder_right=18.0 * intensity,
        shoulder_left=-12.0 * intensity,
        knee_left=8.0 * intensity,
    ))


# ---------------------------------------------------------------------------
# Upper body — arm movements
# ---------------------------------------------------------------------------

def arm_swing_left(intensity: float = 1.0) -> Pose:
    """Left arm swings forward, right arm back — walking rhythm."""
    return clamp_pose(Pose(
        shoulder_left=-35.0 * intensity,
        shoulder_right=20.0 * intensity,
        elbow_left=15.0 * intensity,
        elbow_right=8.0 * intensity,
    ))


def arm_swing_right(intensity: float = 1.0) -> Pose:
    """Right arm swings forward, left arm back."""
    return clamp_pose(Pose(
        shoulder_right=-35.0 * intensity,
        shoulder_left=20.0 * intensity,
        elbow_right=15.0 * intensity,
        elbow_left=8.0 * intensity,
    ))


def arm_raise_left(intensity: float = 1.0) -> Pose:
    """Left arm raised high — accent on strong beat or melodic peak.
    Counterbalanced: right hip/knee stabilize the pose.
    """
    return clamp_pose(Pose(
        shoulder_left=-62.0 * intensity,
        elbow_left=35.0 * intensity,
        shoulder_right=15.0 * intensity,
        hip_right=6.0 * intensity,
        head_yaw=-10.0 * intensity,
    ))


def arm_raise_right(intensity: float = 1.0) -> Pose:
    """Right arm raised high."""
    return clamp_pose(Pose(
        shoulder_right=-62.0 * intensity,
        elbow_right=35.0 * intensity,
        shoulder_left=15.0 * intensity,
        hip_left=6.0 * intensity,
        head_yaw=10.0 * intensity,
    ))


def arm_raise_both(intensity: float = 1.0) -> Pose:
    """Both arms raised — chorus climax or high-energy peak.
    Knees bend for balance.
    """
    return clamp_pose(Pose(
        shoulder_left=-72.0 * intensity,
        shoulder_right=-72.0 * intensity,
        elbow_left=48.0 * intensity,
        elbow_right=48.0 * intensity,
        head_pitch=-12.0 * intensity,
        knee_left=18.0 * intensity,
        knee_right=18.0 * intensity,
    ))


def robot_wave_right(intensity: float = 1.0) -> Pose:
    """Classic robot wave — right arm up with bent elbow.
    Robotic/mechanical character.
    """
    return clamp_pose(Pose(
        shoulder_right=-55.0 * intensity,
        elbow_right=80.0 * intensity,
        head_yaw=12.0 * intensity,
        hip_left=5.0 * intensity,
    ))


def robot_wave_left(intensity: float = 1.0) -> Pose:
    """Classic robot wave — left arm up."""
    return clamp_pose(Pose(
        shoulder_left=-55.0 * intensity,
        elbow_left=80.0 * intensity,
        head_yaw=-12.0 * intensity,
        hip_right=5.0 * intensity,
    ))


# ---------------------------------------------------------------------------
# Expressive gestures
# ---------------------------------------------------------------------------

def celebrate(intensity: float = 1.0) -> Pose:
    """Both arms up, head back, tiptoe — climax / chorus peak celebration."""
    return clamp_pose(Pose(
        shoulder_left=-80.0 * intensity,
        shoulder_right=-80.0 * intensity,
        elbow_left=60.0 * intensity,
        elbow_right=60.0 * intensity,
        head_pitch=-20.0 * intensity,
        knee_left=22.0 * intensity,
        knee_right=22.0 * intensity,
        ankle_left=14.0 * intensity,   # tiptoe
        ankle_right=14.0 * intensity,
    ))


def low_energy(intensity: float = 1.0) -> Pose:
    """Subtle slouch — quiet sections, bridge, or intro."""
    return clamp_pose(Pose(
        knee_left=18.0 * intensity,
        knee_right=18.0 * intensity,
        shoulder_left=12.0 * intensity,
        shoulder_right=12.0 * intensity,
        head_pitch=10.0 * intensity,
        hip_left=3.0 * intensity,
        hip_right=3.0 * intensity,
    ))


def attention(intensity: float = 1.0) -> Pose:
    """Stand at attention — section transition, or a rest beat."""
    return clamp_pose(Pose(
        head_pitch=-5.0 * intensity,
        shoulder_left=5.0 * intensity,
        shoulder_right=5.0 * intensity,
    ))


# ---------------------------------------------------------------------------
# New expressive gestures
# ---------------------------------------------------------------------------

def hip_pop_left(intensity: float = 1.0) -> Pose:
    """Sharp hip pop to the left — bass hit accent with push-off ankle."""
    return clamp_pose(Pose(
        hip_left=22.0 * intensity,
        hip_right=-10.0 * intensity,
        knee_right=18.0 * intensity,
        ankle_left=-8.0 * intensity,   # push-off foot
        shoulder_left=-12.0 * intensity,
        shoulder_right=8.0 * intensity,
        head_yaw=-8.0 * intensity,
    ))


def hip_pop_right(intensity: float = 1.0) -> Pose:
    """Sharp hip pop to the right."""
    return clamp_pose(Pose(
        hip_right=22.0 * intensity,
        hip_left=-10.0 * intensity,
        knee_left=18.0 * intensity,
        ankle_right=-8.0 * intensity,
        shoulder_right=-12.0 * intensity,
        shoulder_left=8.0 * intensity,
        head_yaw=8.0 * intensity,
    ))


def shoulder_shimmy(intensity: float = 1.0) -> Pose:
    """Left shoulder rolls forward, right back — mid-frequency groove."""
    return clamp_pose(Pose(
        shoulder_left=-30.0 * intensity,
        shoulder_right=25.0 * intensity,
        elbow_left=45.0 * intensity,
        elbow_right=35.0 * intensity,
        head_yaw=-8.0 * intensity,
        hip_left=5.0 * intensity,
    ))


def point_left(intensity: float = 1.0) -> Pose:
    """Left arm extends to the side — declarative, treble-driven gesture."""
    return clamp_pose(Pose(
        shoulder_left=-70.0 * intensity,
        elbow_left=5.0 * intensity,    # nearly straight
        shoulder_right=15.0 * intensity,
        head_yaw=-18.0 * intensity,
        hip_right=5.0 * intensity,
    ))


def point_right(intensity: float = 1.0) -> Pose:
    """Right arm extends to the side."""
    return clamp_pose(Pose(
        shoulder_right=-70.0 * intensity,
        elbow_right=5.0 * intensity,
        shoulder_left=15.0 * intensity,
        head_yaw=18.0 * intensity,
        hip_left=5.0 * intensity,
    ))


def wave_hands_up(intensity: float = 1.0) -> Pose:
    """Both arms spread upward and out — open, celebratory chorus arrival."""
    return clamp_pose(Pose(
        shoulder_left=-65.0 * intensity,
        shoulder_right=-65.0 * intensity,
        elbow_left=22.0 * intensity,
        elbow_right=22.0 * intensity,
        head_pitch=-12.0 * intensity,
        knee_left=15.0 * intensity,
        knee_right=15.0 * intensity,
        ankle_left=10.0 * intensity,
        ankle_right=10.0 * intensity,
    ))


def cross_step(intensity: float = 1.0) -> Pose:
    """Weight crosses: left hip pushes while right foot steps.
    Creates cha-cha / cross-step character at phrase entrances.
    """
    return clamp_pose(Pose(
        hip_left=20.0 * intensity,
        hip_right=-18.0 * intensity,
        knee_right=22.0 * intensity,
        ankle_right=10.0 * intensity,
        shoulder_left=-25.0 * intensity,
        shoulder_right=12.0 * intensity,
        head_yaw=-12.0 * intensity,
    ))


def ankle_bounce(intensity: float = 1.0) -> Pose:
    """Subtle ankle/knee bounce — fills weak beats with micro-rhythm."""
    return clamp_pose(Pose(
        ankle_left=15.0 * intensity,
        ankle_right=15.0 * intensity,
        knee_left=10.0 * intensity,
        knee_right=10.0 * intensity,
        head_pitch=5.0 * intensity,
    ))


def freeze(intensity: float = 1.0) -> Pose:
    """Sudden pose lock — dramatic pause on a percussive hit."""
    return clamp_pose(Pose(
        knee_left=25.0 * intensity,
        knee_right=25.0 * intensity,
        hip_left=10.0 * intensity,
        hip_right=-10.0 * intensity,
        shoulder_left=-30.0 * intensity,
        shoulder_right=20.0 * intensity,
        elbow_left=40.0 * intensity,
        head_pitch=8.0 * intensity,
        head_yaw=-6.0 * intensity,
        ankle_left=12.0 * intensity,
    ))


def running_man_left(intensity: float = 1.0) -> Pose:
    """Running-man: left knee pumps high, right arm swings forward."""
    return clamp_pose(Pose(
        hip_left=18.0 * intensity,
        knee_left=35.0 * intensity,
        ankle_left=12.0 * intensity,
        hip_right=-8.0 * intensity,
        shoulder_right=-32.0 * intensity,
        elbow_right=22.0 * intensity,
        shoulder_left=15.0 * intensity,
        head_yaw=-5.0 * intensity,
    ))


def running_man_right(intensity: float = 1.0) -> Pose:
    """Running-man: right knee pumps high, left arm swings forward."""
    return clamp_pose(Pose(
        hip_right=18.0 * intensity,
        knee_right=35.0 * intensity,
        ankle_right=12.0 * intensity,
        hip_left=-8.0 * intensity,
        shoulder_left=-32.0 * intensity,
        elbow_left=22.0 * intensity,
        shoulder_right=15.0 * intensity,
        head_yaw=5.0 * intensity,
    ))
