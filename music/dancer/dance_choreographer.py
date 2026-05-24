"""Dance Choreography Engine — Beat-driven keyframe generation.

Algorithm overview
------------------
1. Use beat timestamps as anchor points on the timeline.
2. For each beat, determine its position within the bar (0–3).
3. Look up local audio energy (RMS) and timbral character (spectral
   centroid) from the nearest analysis frame.
4. Select and blend gestures based on beat position + energy level.
5. Emit one Keyframe per beat.  All joints are defined simultaneously,
   so the robot receives a coherent whole-body pose at each beat.

Mapping rules
-------------
  Beat in bar 0 (downbeat)   → side_step_left  + arm_swing_right
  Beat in bar 1              → side_step_right + arm_swing_left
  Beat in bar 2 (back-beat)  → side_step_left  + arm_swing_right + accent
  Beat in bar 3              → side_step_right + arm_swing_left  + accent
  Head bobs on every beat.
  High-energy beats add arm raises or celebrate.
  Low-energy beats use low_energy overlay.
  Every 8 beats a body-lean is added for melodic phrasing.
"""

from typing import Dict, List, Any
import numpy as np

from . import gesture_library as G
from .types import Keyframe, JOINT_LIMITS


class DanceChoreographer:
    """Converts audio features into a time-sorted List[Keyframe]."""

    def __init__(self, robot_config: Dict = None):
        self.robot_config = robot_config or {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def choreograph_dance(self, audio_features: Dict[str, Any]) -> List[Keyframe]:
        """Generate a full dance from extracted audio features.

        Required keys in audio_features:
            beats_time   – np.ndarray of beat timestamps (seconds)
            tempo        – float BPM
            rms          – np.ndarray of RMS energy per frame
            spectral_centroid – np.ndarray of centroid Hz per frame
            sr           – int sample rate (default 22050)
            hop_length   – int (default 512)
            duration     – float total duration seconds
        """
        self._validate_features(audio_features)

        beat_times  = np.asarray(audio_features["beats_time"], dtype=float)
        tempo       = float(audio_features["tempo"])
        rms         = np.asarray(audio_features["rms"],               dtype=float)
        centroid    = np.asarray(audio_features["spectral_centroid"],  dtype=float)
        sr          = int(audio_features.get("sr",         22050))
        hop_length  = int(audio_features.get("hop_length", 512))
        duration    = float(audio_features.get("duration", float(beat_times[-1]) + 1.0))

        beat_interval = 60.0 / tempo
        # transition occupies 55% of beat interval, capped at 380 ms
        transition = min(beat_interval * 0.55, 0.38)

        # Normalise RMS to 0–1 range
        rms_max = float(np.max(rms)) + 1e-8
        rms_norm = rms / rms_max

        # Per-beat feature lookup (nearest-frame)
        beat_rms      = self._lookup_frames(beat_times, rms_norm,  sr, hop_length)
        beat_centroid = self._lookup_frames(beat_times, centroid,   sr, hop_length)

        # Energy thresholds (percentile-based → adapts to any song)
        thresh_high = float(np.percentile(beat_rms, 75))
        thresh_low  = float(np.percentile(beat_rms, 30))
        cent_median = float(np.median(beat_centroid))

        keyframes: List[Keyframe] = []

        # ── home pose at t=0 ──────────────────────────────────────────
        keyframes.append(Keyframe(
            time=0.0, pose=G.home(), transition=0.5, gesture_name="home"
        ))

        for i, beat_time in enumerate(beat_times):
            beat_in_bar = i % 4
            half_beat   = i % 2
            phrase_beat = i % 8   # 8-beat phrase position
            energy      = float(beat_rms[i])
            cent        = float(beat_centroid[i])

            # Scaled intensity 0.4–1.0 so even quiet passages have motion
            intensity = float(np.clip(energy * 1.3 + 0.35, 0.4, 1.0))

            # ── Step 1: base lower-body step (alternates every beat) ──
            if half_beat == 0:
                base = G.side_step_left(intensity)
                base_name = "side_step_left"
            else:
                base = G.side_step_right(intensity)
                base_name = "side_step_right"

            # ── Step 2: head bob (every beat) ─────────────────────────
            bob = G.head_bob(intensity * 0.65)
            base = G.blend_poses(base, bob, 1.0)

            # ── Step 3: alternating arm swing (every 2 beats) ─────────
            if half_beat == 0:
                arm = G.arm_swing_right(intensity * 0.85)
            else:
                arm = G.arm_swing_left(intensity * 0.85)
            base = G.blend_poses(base, arm, 1.0)

            # ── Step 4: accent on beats 2 & 3 of bar ─────────────────
            accent_name = base_name
            if beat_in_bar in (2, 3):
                if cent >= cent_median:
                    # High frequency content → upper-body accent
                    accent = (G.arm_raise_left(intensity * 0.72)
                              if beat_in_bar == 2
                              else G.arm_raise_right(intensity * 0.72))
                    base = G.blend_poses(base, accent, 0.75)
                    accent_name = "arm_raise"
                else:
                    # Low frequency content → lower-body punch
                    accent = G.knee_pump(intensity * 0.75)
                    base = G.blend_poses(base, accent, 0.65)
                    accent_name = "knee_pump"

            # ── Step 5: energy-level overlay ──────────────────────────
            if energy >= thresh_high:
                if beat_in_bar == 0:
                    climax = G.celebrate(intensity * 0.45)
                    base = G.blend_poses(base, climax, 0.42)
                    accent_name = "celebrate"
                elif beat_in_bar == 2:
                    # Alternate wave on high-energy back-beats
                    wave = (G.robot_wave_right(intensity * 0.6)
                            if (i // 4) % 2 == 0
                            else G.robot_wave_left(intensity * 0.6))
                    base = G.blend_poses(base, wave, 0.45)
                    accent_name = "robot_wave"
            elif energy <= thresh_low:
                low = G.low_energy(0.55)
                base = G.blend_poses(base, low, 0.50)
                if accent_name.startswith("side_step"):
                    accent_name = "low_energy"

            # ── Step 6: 8-beat phrase lean for musical phrasing ───────
            if phrase_beat == 0:
                lean = G.body_lean_left(intensity * 0.35)
                base = G.blend_poses(base, lean, 0.50)
            elif phrase_beat == 4:
                lean = G.body_lean_right(intensity * 0.35)
                base = G.blend_poses(base, lean, 0.50)

            keyframes.append(Keyframe(
                time=float(beat_time),
                pose=base,
                transition=transition,
                gesture_name=accent_name,
            ))

        # ── return to home at end ─────────────────────────────────────
        keyframes.append(Keyframe(
            time=duration, pose=G.home(), transition=1.0, gesture_name="home"
        ))

        return sorted(keyframes, key=lambda k: k.time)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _lookup_frames(
        times: np.ndarray,
        feature: np.ndarray,
        sr: int,
        hop_length: int,
    ) -> np.ndarray:
        """Return feature values at the frames nearest to each timestamp."""
        frames = np.round(times * sr / hop_length).astype(int)
        frames = np.clip(frames, 0, len(feature) - 1)
        return feature[frames]

    @staticmethod
    def _validate_features(features: Dict[str, Any]) -> None:
        required = {"beats_time", "tempo", "rms", "spectral_centroid"}
        missing = required - features.keys()
        if missing:
            raise ValueError(
                f"audio_features is missing required keys: {missing}. "
                "Run SpectrumAnalyzer.extract_spectral_features() first."
            )
        if len(features["beats_time"]) == 0:
            raise ValueError("beats_time array is empty — no beats detected in audio.")
