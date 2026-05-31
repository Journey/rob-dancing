"""Unit tests for the DanceChoreographer and supporting modules.

These tests exercise the choreography pipeline without requiring a real
audio file.  They feed synthetic audio_features dicts directly into the
choreographer so the tests run quickly and deterministically.
"""

import math
import numpy as np
import pytest

from music.dancer.types import Pose, Keyframe, JOINT_LIMITS
from music.dancer.gesture_library import (
    clamp_pose, blend_poses, lerp_pose,
    home, side_step_left, side_step_right,
    arm_raise_both, celebrate, low_energy,
)
from music.dancer.dance_choreographer import DanceChoreographer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_features(n_beats: int = 16, tempo: float = 120.0, sr: int = 22050,
                  hop_length: int = 512, duration: float = 8.0) -> dict:
    """Synthetic audio_features dict for choreographer tests."""
    beat_interval = 60.0 / tempo
    beats_time = np.arange(n_beats) * beat_interval + 0.5

    n_frames = int(duration * sr / hop_length) + 1
    rms = np.random.RandomState(42).uniform(0.1, 0.9, n_frames)
    centroid = np.random.RandomState(7).uniform(500, 6000, n_frames)

    return {
        "beats_time":        beats_time,
        "tempo":             tempo,
        "rms":               rms,
        "spectral_centroid": centroid,
        "sr":                sr,
        "hop_length":        hop_length,
        "duration":          duration,
    }


# ---------------------------------------------------------------------------
# Gesture library tests
# ---------------------------------------------------------------------------

class TestGestureLibrary:
    def test_home_is_all_zeros(self):
        p = home()
        for field, val in vars(p).items():
            assert val == 0.0, f"{field} should be 0 for home pose"

    def test_clamp_enforces_limits(self):
        # Force out-of-range value
        p = Pose(head_yaw=999.0, elbow_left=-50.0)
        clamped = clamp_pose(p)
        lo, hi = JOINT_LIMITS["head_yaw"]
        assert lo <= clamped.head_yaw <= hi
        lo2, hi2 = JOINT_LIMITS["elbow_left"]
        assert lo2 <= clamped.elbow_left <= hi2

    def test_all_gestures_within_limits(self):
        gestures = [
            side_step_left(1.0), side_step_right(1.0),
            arm_raise_both(1.0), celebrate(1.0), low_energy(1.0),
        ]
        for pose in gestures:
            for joint, (lo, hi) in JOINT_LIMITS.items():
                val = getattr(pose, joint)
                assert lo <= val <= hi, (
                    f"{joint}={val:.1f} out of range [{lo}, {hi}]"
                )

    def test_blend_weight_zero_returns_base(self):
        base = side_step_left(0.8)
        overlay = celebrate(1.0)
        result = blend_poses(base, overlay, weight=0.0)
        assert result == base

    def test_lerp_at_t0_equals_a(self):
        a, b = side_step_left(0.5), side_step_right(0.5)
        result = lerp_pose(a, b, 0.0)
        for f in vars(a):
            assert abs(getattr(result, f) - getattr(a, f)) < 1e-9

    def test_lerp_at_t1_equals_b(self):
        a, b = side_step_left(0.5), side_step_right(0.5)
        result = lerp_pose(a, b, 1.0)
        for f in vars(b):
            assert abs(getattr(result, f) - getattr(b, f)) < 1e-9


# ---------------------------------------------------------------------------
# Choreographer tests
# ---------------------------------------------------------------------------

class TestDanceChoreographer:
    def setup_method(self):
        self.choreo = DanceChoreographer()

    def test_output_is_nonempty(self):
        feats = make_features(n_beats=16)
        kfs = self.choreo.choreograph_dance(feats)
        assert len(kfs) > 0

    def test_keyframes_are_time_sorted(self):
        feats = make_features(n_beats=32)
        kfs = self.choreo.choreograph_dance(feats)
        times = [kf.time for kf in kfs]
        assert times == sorted(times), "Keyframes must be in ascending time order"

    def test_first_keyframe_is_home_at_t0(self):
        feats = make_features(n_beats=8)
        kfs = self.choreo.choreograph_dance(feats)
        assert kfs[0].time == 0.0
        assert kfs[0].gesture_name == "home"
        assert kfs[0].pose == home()

    def test_last_keyframe_is_home_at_end(self):
        feats = make_features(n_beats=8, duration=10.0)
        kfs = self.choreo.choreograph_dance(feats)
        assert kfs[-1].gesture_name == "home"
        assert abs(kfs[-1].time - 10.0) < 1e-9

    def test_all_poses_within_joint_limits(self):
        feats = make_features(n_beats=32)
        kfs = self.choreo.choreograph_dance(feats)
        for kf in kfs:
            for joint, (lo, hi) in JOINT_LIMITS.items():
                val = getattr(kf.pose, joint)
                assert lo <= val <= hi, (
                    f"t={kf.time:.2f} {joint}={val:.1f} "
                    f"exceeds [{lo}, {hi}]  gesture={kf.gesture_name}"
                )

    def test_transition_durations_are_positive(self):
        feats = make_features(n_beats=16)
        kfs = self.choreo.choreograph_dance(feats)
        for kf in kfs:
            assert kf.transition > 0, f"transition must be > 0, got {kf.transition}"

    def test_keyframe_count_matches_beats_plus_two(self):
        n_beats = 20
        feats = make_features(n_beats=n_beats)
        kfs = self.choreo.choreograph_dance(feats)
        # one keyframe per beat + home at start + home at end
        assert len(kfs) == n_beats + 2

    def test_missing_required_key_raises_valueerror(self):
        feats = make_features()
        del feats["rms"]
        with pytest.raises(ValueError, match="missing required keys"):
            self.choreo.choreograph_dance(feats)

    def test_empty_beats_raises_valueerror(self):
        feats = make_features()
        feats["beats_time"] = np.array([])
        with pytest.raises(ValueError, match="empty"):
            self.choreo.choreograph_dance(feats)

    def test_alternating_side_steps(self):
        """Bar structure: downbeat (beat_in_bar=0) uses side_step_left base (hip_left > 0),
        back-beat (beat_in_bar=2) uses side_step_right base (hip_right > 0).
        Weak beats (1, 3) use ankle_bounce base which keeps hip values small.
        """
        feats = make_features(n_beats=8, tempo=120.0)
        kfs = self.choreo.choreograph_dance(feats)
        # skip home at index 0; beat keyframes start at index 1
        beat_kfs = kfs[1:-1]
        for i, kf in enumerate(beat_kfs):
            beat_in_bar = i % 4
            if beat_in_bar == 0:
                # Downbeat → side_step_left base → net hip_left should be positive
                assert kf.pose.hip_left >= 0, (
                    f"Beat {i} (downbeat): expected hip_left >= 0, got {kf.pose.hip_left:.1f}"
                )
            elif beat_in_bar == 2:
                # Back-beat → side_step_right base → net hip_right should be positive
                assert kf.pose.hip_right >= 0, (
                    f"Beat {i} (back-beat): expected hip_right >= 0, got {kf.pose.hip_right:.1f}"
                )
