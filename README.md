# rob-dancing

Analyze music → generate robot choreography → visualize in 3D.

Given an audio file, the system detects beats and spectral features with [librosa](https://librosa.org/), maps each beat event to a full-body keyframe pose using a multi-layer choreography algorithm, and exports a JSON sequence that drives a custom NOVA Three.js character in the browser.

---

## Demo

Two built-in tracks:

| Track | Style | Duration |
|-------|-------|----------|
| ⚡ 双节棍 (Jay Chou) | Hip-hop / Energetic | ~3 min |
| 🌸 茉莉花 (Folk) | Gentle / Lyrical | ~3 min |

```bash
make web   # serve at http://localhost:8000
```

Switch tracks with the buttons at the top of the page. Press **播放** to start.

---

## Architecture

```
music/
  analyzer/
    spectrum_analyzer.py   # librosa: tempo, beats, RMS, spectral centroid, etc.
    audio_visualizer.py    # matplotlib spectrum plots
  dancer/
    types.py               # Pose (15 joints), Keyframe, JOINT_LIMITS
    gesture_library.py     # 30+ named gesture functions + blend/lerp utilities
    dance_choreographer.py # 7-layer beat-anchored keyframe generation
    dance_executor.py      # SimulatedExecutor for offline testing
    dance_system.py        # full pipeline: audio file → keyframe JSON
  __main__.py              # CLI entry point

web/
  index.html               # track switcher UI
  js/robtic.js             # Three.js NOVA character + keyframe animation
  css/style.css            # dark neon theme
  data/                    # generated dance JSON files
  statics/                 # audio files (mp3/mp4)
```

---

## From Music to Dance: the Full Pipeline

### Stage 1 — Audio Feature Extraction (`spectrum_analyzer.py`)

`SpectrumAnalyzer.extract_spectral_features()` loads the audio via librosa (22 050 Hz, hop_length=512) and extracts:

| Feature | What it captures | Used for |
|---------|-----------------|----------|
| `tempo` | BPM (beat_track) | sets the base beat interval |
| `beats_time` | timestamp of every detected beat | one keyframe per beat |
| `rms` | per-frame energy (loudness) | drive intensity and transition speed |
| `spectral_centroid` | brightness / high-frequency content | choose arm vs. hip gestures |
| `spectral_bandwidth` | frequency spread | auxiliary (available for future layers) |
| `mfcc` | timbral fingerprint | available for future style classification |

### Stage 2 — Per-Beat Feature Lookup

For each beat timestamp, the nearest analysis frame is computed:

```
frame_index = round(beat_time × sr / hop_length)
```

This gives per-beat values of `rms` (energy) and `spectral_centroid` (brightness). Adaptive percentile thresholds are then derived from the full-song distribution:

```
thresh_high = 75th percentile of beat RMS   → high-energy beats
thresh_low  = 30th percentile of beat RMS   → quiet/rest beats
cent_p33 / cent_p66                         → bass / mid / treble classification
```

Using percentiles instead of fixed values makes the system work equally well for loud pop tracks and quiet folk songs.

### Stage 3 — 7-Layer Choreography (`dance_choreographer.py`)

Each beat is processed through seven additive layers. Later layers are blended *on top of* earlier ones using `blend_poses(base, overlay, weight)`.

```
beat i
 │
 ├─ Layer 1: Base lower-body step
 │     Downbeat (i%4==0): side_step_left / hip_pop_left / cross_step
 │     Back-beat (i%4==2): side_step_right / hip_pop_right
 │     Weak beats (i%4==1,3): ankle_bounce (light)
 │
 ├─ Layer 2: Head movement
 │     Downbeat/1: head_bob  ·  Back-beat: head_sway (alternating L/R every bar)
 │
 ├─ Layer 3: Arm movement — frequency-band driven
 │     treble (high centroid): point_left/right ↔ robot_dab_left/right (every 3 bars)
 │     mid: shoulder_shimmy at phrase mid-points
 │     bass + phrase start: running_man_left/right
 │     default: arm_swing  ·  arm_spread_left/right every 4th bar
 │
 ├─ Layer 4: Back-beat upper-body accent (beat 2, only if Layer 3 used default)
 │     treble: arm_raise ↔ arm_spread (alternates 2-bar blocks)
 │     bass:   knee_pump
 │     mid:    shoulder_shimmy
 │
 ├─ Layer 5: Phrase-level body lean + torso twist (every 8 beats)
 │     Beat 0 of phrase: body_lean_left  + torso_twist_left  (×0.30)
 │     Beat 4 of phrase: body_lean_right + torso_twist_right (×0.30)
 │
 ├─ Layer 6: Section climax (every 16 beats, high energy)
 │     Beat 0:  4-gesture rotation → celebrate / wave_hands_up / cheer / arm_spread_both
 │     Beat 8:  arm_raise_both
 │
 └─ Layer 7: Energy extremes + anti-repetition
       High energy downbeat every 12 beats → freeze
       Low energy → low_energy overlay
       Same gesture 3× in a row → inject shoulder_shimmy or cross_step break
```

**Transition speed** is also energy-driven:

| Intensity | Formula | Result |
|-----------|---------|--------|
| > 0.75 | `beat_interval × 0.22` | fast snap (≤ 0.18 s) |
| 0.45 – 0.75 | `beat_interval × 0.42` | balanced (≤ 0.35 s) |
| < 0.45 | `beat_interval × 0.65` | slow flow (≤ 0.45 s) |

### Stage 4 — Gesture Library (`gesture_library.py`)

Each gesture is a pure function `gesture(intensity: float) -> Pose`. Intensity scales all joint angles proportionally (0–1), so the same gesture looks natural at half or full energy.

Key gesture groups:

| Group | Examples |
|-------|---------|
| Head | `head_bob`, `head_sway_left/right` |
| Lower body | `side_step_left/right`, `hip_pop_left/right`, `ankle_bounce`, `cross_step`, `running_man_left/right`, `knee_pump` |
| Arms — forward/back | `arm_swing_left/right`, `arm_raise_left/right/both`, `point_left/right`, `robot_wave_left/right`, `shoulder_shimmy` |
| Arms — **lateral (Z-axis)** | `arm_spread_left/right/both`, `cheer`, `robot_dab_left/right` |
| Torso | `body_lean_left/right`, `torso_twist_left/right` |
| Climax | `celebrate`, `wave_hands_up`, `freeze`, `low_energy` |

Poses are **additively blended** — `blend_poses(base, overlay, weight)` adds the overlay's joint deltas to the base, then clamps to hardware limits. Layers accumulate without overwriting each other.

### Stage 5 — Pose Data Model (`types.py`)

```python
@dataclass
class Pose:
    # Head (2 DOF)
    head_yaw: float = 0.0        # ±45° left/right look
    head_pitch: float = 0.0      # ±30° up/down nod

    # Arms — forward/back X-axis (4 DOF)
    shoulder_left: float = 0.0   # negative = arm raised/forward
    shoulder_right: float = 0.0
    elbow_left: float = 0.0      # 0–135° bend
    elbow_right: float = 0.0

    # Arms — lateral Z-axis (2 DOF)
    shoulder_left_z: float = 0.0   # ±80° abduction (arm spreads outward)
    shoulder_right_z: float = 0.0

    # Torso (1 DOF)
    torso_twist: float = 0.0     # ±25° Y-axis rotation

    # Legs (6 DOF)
    hip_left: float = 0.0
    hip_right: float = 0.0
    knee_left: float = 0.0
    knee_right: float = 0.0
    ankle_left: float = 0.0
    ankle_right: float = 0.0
```

Total: **15 DOF**. All values are in degrees. `default=0.0` everywhere ensures JSON generated before new fields were added still loads correctly in the browser.

### Stage 6 — JSON Output

One keyframe per detected beat, plus a `home` frame at t=0 and t=duration:

```json
{
  "audio_file": "shuangjiegun.mp3",
  "duration": 201.0,
  "tempo": 99.4,
  "keyframes": [
    {
      "time": 1.857,
      "transition": 0.33,
      "gesture": "robot_dab_left",
      "pose": {
        "head_yaw": -10.0, "head_pitch": 5.0,
        "shoulder_left": -52.0, "shoulder_right": -30.0,
        "elbow_left": 8.0, "elbow_right": 80.0,
        "shoulder_left_z": 12.0, "shoulder_right_z": 0.0,
        "torso_twist": -4.0,
        "hip_left": 3.0, "hip_right": 1.0,
        "knee_left": 0.0, "knee_right": 0.0,
        "ankle_left": 0.0, "ankle_right": 0.0
      }
    }
  ]
}
```

### Stage 7 — 3D Rendering (`robtic.js`)

The browser loads the JSON, then on every animation frame:

1. Finds the two keyframes bracketing `audioPlayer.currentTime`
2. Computes `t = (now − kf_a.time) / kf_a.transition` (clamped 0–1)
3. Applies `easeInOut(t)` for smooth motion
4. `lerpPose(a, b, t)` interpolates all 15 joint values
5. `applyPose(pose)` maps each joint to the corresponding Three.js bone:

```
head_yaw/pitch        → headGroup           rotation.y / rotation.x
shoulder_left/right   → leftShoulderPivot   rotation.x  (forward/back)
shoulder_left/right_z → leftShoulderPivot   rotation.z  (lateral spread)
elbow_left/right      → leftElbowPivot      rotation.x
torso_twist           → upperTorso          rotation.y
hip/knee/ankle        → corresponding leg pivots
```

The NOVA character is built from procedural Three.js geometry (MeshStandardMaterial, PBR, ACESFilmic tone-mapping). No external model files are required.

---

## 15 Controlled Joints

| Group | Joint | Axis | Range |
|-------|-------|------|-------|
| Head | `head_yaw` | Y | ±45° |
| Head | `head_pitch` | X | ±30° |
| Arms (front/back) | `shoulder_left/right` | X | ±90° |
| Arms (lateral) | `shoulder_left/right_z` | Z | ±80° |
| Elbows | `elbow_left/right` | X | 0–135° |
| Torso | `torso_twist` | Y | ±25° |
| Hips | `hip_left/right` | X | ±30° |
| Knees | `knee_left/right` | X | 0–90° |
| Ankles | `ankle_left/right` | X | ±20° |

---

## Setup

**Requirements:** Python 3.12+, [Poetry](https://python-poetry.org/)

```bash
git clone <repo>
cd rob-dancing
poetry install
```

---

## Usage

### Generate a dance file

```bash
# Output goes to web/data/dance.json
make dance AUDIO=path/to/song.mp3

# Specify output file
poetry run python -m music path/to/song.mp3 --output web/data/song_dance.json

# Also show a matplotlib joint-angle preview
poetry run python -m music path/to/song.mp3 --visualize
```

### View in the browser

```bash
make web   # → http://localhost:8000
```

Use the track buttons (⚡ 双节棍 / 🌸 茉莉花) to switch songs. Hard-refresh (Cmd+Shift+R) after regenerating JSON files.

### Analyze spectrum only

```bash
make analyze AUDIO=path/to/song.mp3
```

---

## Development

```bash
make test      # run all 16 pytest tests
make example   # run examples/basic_usage.py
```

**Python API**

```python
from music.dancer.dance_system import DanceSystem

system = DanceSystem()
data = system.create_dance_from_music("song.mp3")
system.save_dance_sequence(data, "web/data/song_dance.json")

# optional matplotlib preview
system.visualize_dance(data)
```

---

## Dependencies

| Layer | Package | Version |
|-------|---------|---------|
| Audio analysis | [librosa](https://librosa.org/) | `^0.10.2` |
| Numerics | numpy | `^1.24` |
| Plots | matplotlib | `^3.8` |
| Audio I/O | soundfile | `^0.13` |
| 3D rendering | [Three.js](https://threejs.org/) r128 | CDN |
| Tests | pytest | `^9.0` |
