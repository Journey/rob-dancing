"""Dance Choreography Engine — Beat-driven keyframe generation.

Algorithm overview
------------------
Musical structure is organised in nested time layers:

  Beat level (beat_in_bar = i % 4):
    - Downbeat (0):  full-body power gesture — lower body + arms together
    - Back-beat (2): upper-body accent — arm raise or shoulder shimmy
    - Weak beats (1, 3): ankle bounce + light fill — micro-rhythm continuity

  Phrase level (phrase_beat = i % 8):
    - Beat 0: phrase entrance — body lean (left) + possible cross_step
    - Beat 4: phrase mid-pivot — body lean (right) + direction reversal

  Section level (section_beat = i % 16):
    - Beat 0: section climax — celebrate or wave_hands_up
    - Beat 8: section mid — arm_raise_both or shoulder_shimmy

Spectral band mapping:
    - Low centroid  (bass-heavy)   → hip_pop, knee_pump, running_man
    - High centroid (treble-heavy) → point, arm_raise, robot_wave
    - Mid centroid                 → shoulder_shimmy, cross_step, body_lean

Anti-repetition: tracks last 3 gesture names; if the same gesture fills
two consecutive slots a break-gesture is blended in.

Adaptive transition speed:
    - High energy  → fast snap  (beat_interval × 0.22)
    - Low energy   → slow flow  (beat_interval × 0.65)
    - Normal       → balanced   (beat_interval × 0.42)
"""

from collections import deque
from typing import Deque, Dict, List, Any
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
            beats_time        – np.ndarray of beat timestamps (seconds)
            tempo             – float BPM
            rms               – np.ndarray of RMS energy per frame
            spectral_centroid – np.ndarray of centroid Hz per frame
            sr                – int sample rate (default 22050)
            hop_length        – int (default 512)
            duration          – float total duration seconds
        """
        self._validate_features(audio_features)

        beat_times = np.asarray(audio_features["beats_time"], dtype=float)
        tempo      = float(audio_features["tempo"])
        rms        = np.asarray(audio_features["rms"],              dtype=float)
        centroid   = np.asarray(audio_features["spectral_centroid"], dtype=float)
        sr         = int(audio_features.get("sr",         22050))
        hop_length = int(audio_features.get("hop_length", 512))
        duration   = float(audio_features.get("duration", float(beat_times[-1]) + 1.0))

        beat_interval = 60.0 / tempo

        # Normalise RMS to 0–1
        rms_norm = rms / (float(np.max(rms)) + 1e-8)

        # Per-beat feature lookup (nearest analysis frame)
        beat_rms      = self._lookup_frames(beat_times, rms_norm,  sr, hop_length)
        beat_centroid = self._lookup_frames(beat_times, centroid,   sr, hop_length)

        # Adaptive thresholds — percentile-based so they work for any song
        thresh_high = float(np.percentile(beat_rms, 75))
        thresh_low  = float(np.percentile(beat_rms, 30))
        cent_p33    = float(np.percentile(beat_centroid, 33))
        cent_p66    = float(np.percentile(beat_centroid, 66))

        keyframes: List[Keyframe] = []
        last_gestures: Deque[str] = deque(maxlen=3)

        # ── home pose at t=0 ──────────────────────────────────────────
        keyframes.append(Keyframe(
            time=0.0, pose=G.home(), transition=0.5, gesture_name="home"
        ))

        for i, beat_time in enumerate(beat_times):
            beat_in_bar  = i % 4
            half_beat    = i % 2
            phrase_beat  = i % 8
            section_beat = i % 16
            bar_num      = i // 4
            energy       = float(beat_rms[i])
            cent         = float(beat_centroid[i])

            # Intensity 0.4–1.0 so even quiet passages have visible motion
            intensity = float(np.clip(energy * 1.3 + 0.35, 0.4, 1.0))

            # Adaptive transition time
            if intensity > 0.75:
                transition = min(beat_interval * 0.22, 0.18)   # fast snap
            elif intensity < 0.45:
                transition = min(beat_interval * 0.65, 0.45)   # slow flow
            else:
                transition = min(beat_interval * 0.42, 0.35)   # balanced

            # Frequency band category
            if cent < cent_p33:
                freq_band = "bass"
            elif cent > cent_p66:
                freq_band = "treble"
            else:
                freq_band = "mid"

            # ── Layer 1: base lower-body ───────────────────────────────
            # Downbeat / back-beat → full stepping gesture
            # Weak beats (1, 3)   → ankle bounce for micro-rhythm
            if beat_in_bar in (0, 2):
                if freq_band == "bass" and energy >= thresh_high * 0.8:
                    # Bass hit → sharp hip pop
                    base = (G.hip_pop_left(intensity) if beat_in_bar == 0
                            else G.hip_pop_right(intensity))
                    base_name = "hip_pop_left" if beat_in_bar == 0 else "hip_pop_right"
                elif phrase_beat == 0 and beat_in_bar == 0:
                    # Phrase entrance → cross step for variety
                    base = G.cross_step(intensity * 0.9)
                    base_name = "cross_step"
                else:
                    base = (G.side_step_left(intensity) if beat_in_bar == 0
                            else G.side_step_right(intensity))
                    base_name = ("side_step_left" if beat_in_bar == 0
                                 else "side_step_right")
            else:
                # Weak beat: ankle bounce base + light step blend
                base = G.ankle_bounce(intensity * 0.70)
                base_name = "ankle_bounce"
                step = (G.side_step_right(intensity * 0.45) if beat_in_bar == 1
                        else G.side_step_left(intensity * 0.45))
                base = G.blend_poses(base, step, 0.55)

            # ── Layer 2: head movement (varied per bar/beat) ───────────
            if beat_in_bar in (0, 1):
                head_g = G.head_bob(intensity * 0.55)
            elif beat_in_bar == 2:
                head_g = (G.head_sway_left(intensity * 0.60) if bar_num % 2 == 0
                          else G.head_sway_right(intensity * 0.60))
            else:
                head_g = (G.head_sway_right(intensity * 0.50) if bar_num % 2 == 0
                          else G.head_sway_left(intensity * 0.50))
            base = G.blend_poses(base, head_g, 1.0)

            # ── Layer 3: arm movement (frequency-band driven) ──────────
            arm_name = base_name
            if beat_in_bar in (0, 2):
                if freq_band == "treble" and energy >= thresh_high * 0.7:
                    # Bright/high content → alternate point and dab every 3 bars
                    if bar_num % 3 == 2:
                        arm = (G.robot_dab_left(intensity * 0.80) if beat_in_bar == 0
                               else G.robot_dab_right(intensity * 0.80))
                        arm_name = "robot_dab_left" if beat_in_bar == 0 else "robot_dab_right"
                    else:
                        arm = (G.point_left(intensity * 0.80) if beat_in_bar == 0
                               else G.point_right(intensity * 0.80))
                        arm_name = "point_left" if beat_in_bar == 0 else "point_right"
                    base = G.blend_poses(base, arm, 0.70)
                elif freq_band == "mid" and phrase_beat in (2, 6):
                    # Mid-frequency, mid-phrase → shoulder shimmy
                    base = G.blend_poses(base, G.shoulder_shimmy(intensity * 0.90), 0.80)
                    arm_name = "shoulder_shimmy"
                elif freq_band == "bass" and phrase_beat in (0, 1):
                    # Bass + phrase start → running man; downbeat=left, back-beat=right
                    arm = (G.running_man_left(intensity * 0.85) if beat_in_bar == 0
                           else G.running_man_right(intensity * 0.85))
                    arm_name = "running_man_left" if beat_in_bar == 0 else "running_man_right"
                    base = G.blend_poses(base, arm, 0.75)
                else:
                    # Default: arm swing; use lateral spread every 4th bar for variety
                    if bar_num % 4 == 2:
                        arm = (G.arm_spread_left(intensity * 0.80) if half_beat == 0
                               else G.arm_spread_right(intensity * 0.80))
                    else:
                        arm = (G.arm_swing_right(intensity * 0.85) if half_beat == 0
                               else G.arm_swing_left(intensity * 0.85))
                    base = G.blend_poses(base, arm, 1.0)
            else:
                # Weak beats: light arm fill on treble passages
                if freq_band == "treble":
                    arm = (G.robot_wave_right(intensity * 0.40) if beat_in_bar == 1
                           else G.robot_wave_left(intensity * 0.40))
                    base = G.blend_poses(base, arm, 0.50)

            # ── Layer 4: back-beat (beat 2) upper-body accent ──────────
            # Only applies when Layer 3 used the default arm-swing path
            # (arm_name unchanged from base_name), so specialized gestures are preserved.
            if beat_in_bar == 2 and arm_name == base_name:
                if freq_band == "treble":
                    # Alternate arm raise and lateral spread every 2 bars
                    if bar_num % 4 < 2:
                        accent = (G.arm_raise_left(intensity * 0.72) if bar_num % 2 == 0
                                  else G.arm_raise_right(intensity * 0.72))
                        arm_name = "arm_raise"
                    else:
                        accent = (G.arm_spread_left(intensity * 0.72) if bar_num % 2 == 0
                                  else G.arm_spread_right(intensity * 0.72))
                        arm_name = "arm_spread"
                    base = G.blend_poses(base, accent, 0.72)
                elif freq_band == "bass":
                    base = G.blend_poses(base, G.knee_pump(intensity * 0.75), 0.65)
                    arm_name = "knee_pump"
                else:
                    # Mid-freq back-beat → shoulder shimmy
                    base = G.blend_poses(base, G.shoulder_shimmy(intensity * 0.60), 0.55)
                    arm_name = "shoulder_shimmy"

            # ── Layer 5: phrase-level body lean + torso twist (every 8 beats) ─
            if phrase_beat == 0:
                base = G.blend_poses(base, G.body_lean_left(intensity * 0.55), 0.55)
                base = G.blend_poses(base, G.torso_twist_left(intensity * 0.30), 0.30)
            elif phrase_beat == 4:
                base = G.blend_poses(base, G.body_lean_right(intensity * 0.55), 0.55)
                base = G.blend_poses(base, G.torso_twist_right(intensity * 0.30), 0.30)

            # ── Layer 6: section climax (every 16 beats) ──────────────
            gesture_name = arm_name
            if section_beat == 0 and energy >= thresh_high * 0.85:
                # 4-gesture rotation: celebrate → wave_hands_up → cheer → arm_spread_both
                _climax_funcs = [G.celebrate, G.wave_hands_up, G.cheer, G.arm_spread_both]
                _climax_names = ["celebrate", "wave_hands_up", "cheer", "arm_spread_both"]
                climax = _climax_funcs[bar_num % 4](intensity * 0.55)
                base = G.blend_poses(base, climax, 0.48)
                gesture_name = _climax_names[bar_num % 4]
            elif section_beat == 8 and energy >= thresh_high * 0.70:
                base = G.blend_poses(base, G.arm_raise_both(intensity * 0.50), 0.45)
                gesture_name = "arm_raise_both"

            # ── Layer 7: energy extreme overlays ──────────────────────
            if energy >= thresh_high and beat_in_bar == 0 and section_beat not in (0, 8):
                # Periodic freeze on high-energy downbeats (every 12 beats)
                if i % 12 == 0:
                    base = G.blend_poses(base, G.freeze(intensity * 0.45), 0.40)
                    gesture_name = "freeze"
            elif energy <= thresh_low:
                base = G.blend_poses(base, G.low_energy(0.55), 0.45)
                if gesture_name in ("side_step_left", "side_step_right", "ankle_bounce"):
                    gesture_name = "low_energy"

            # ── Anti-repetition: break consecutive same-gesture runs ──
            if (len(last_gestures) >= 2
                    and all(g == gesture_name for g in list(last_gestures)[-2:])):
                if beat_in_bar in (0, 2):
                    break_g = (G.shoulder_shimmy(intensity * 0.50)
                               if freq_band != "mid"
                               else G.cross_step(intensity * 0.50))
                    base = G.blend_poses(base, break_g, 0.35)
                    gesture_name = "break_" + gesture_name

            last_gestures.append(gesture_name)

            keyframes.append(Keyframe(
                time=float(beat_time),
                pose=base,
                transition=transition,
                gesture_name=gesture_name,
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
