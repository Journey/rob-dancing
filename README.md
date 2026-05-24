# rob-dancing

Analyze music → generate robot choreography → visualize in 3D.

Given an audio file, the system detects beats and tempo with [librosa](https://librosa.org/), maps beat events to whole-body keyframe poses using a gesture library, and exports a JSON sequence that drives an [Astro Boy (铁臂阿童木)](https://en.wikipedia.org/wiki/Astro_Boy) Three.js model in the browser.

---

## Architecture

```
music/
  analyzer/
    spectrum_analyzer.py   # librosa: tempo, beats, duration, spectral features
    audio_visualizer.py    # matplotlib spectrum plots
  dancer/
    types.py               # Pose (12 joints), Keyframe, JOINT_LIMITS
    gesture_library.py     # 19+ named gestures + blend/lerp utilities
    dance_choreographer.py # beat-anchored keyframe generation
    dance_executor.py      # SimulatedExecutor for offline testing
    dance_system.py        # full pipeline: audio file → keyframe JSON
  __main__.py              # CLI entry point

web/
  index.html               # main page
  js/robtic.js             # Three.js Astro Boy model + keyframe animation
  css/style.css
  data/                    # generated dance JSON lives here
  statics/                 # audio file(s)
```

### 12 controlled joints

| Group | Joints |
|-------|--------|
| Head | `head_yaw`, `head_pitch` |
| Arms | `shoulder_left`, `shoulder_right`, `elbow_left`, `elbow_right` |
| Legs | `hip_left`, `hip_right`, `knee_left`, `knee_right`, `ankle_left`, `ankle_right` |

### Dance JSON format

```json
{
  "audio_file": "examples/song.mp3",
  "duration": 175.08,
  "tempo": 99.4,
  "keyframes": [
    {
      "time": 1.857,
      "transition": 0.33,
      "gesture": "side_step_left",
      "pose": {
        "head_yaw": -15.0, "head_pitch": 0.0,
        "shoulder_left": -45.0, "shoulder_right": 20.0,
        "elbow_left": 30.0, "elbow_right": 0.0,
        "hip_left": 10.0, "hip_right": -5.0,
        "knee_left": 0.0, "knee_right": 0.0,
        "ankle_left": 0.0, "ankle_right": 0.0
      }
    }
  ]
}
```

One keyframe is generated per detected beat. The web viewer interpolates between keyframes using `easeInOut` blending.

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

# Or specify a custom output path
poetry run python -m music path/to/song.mp3 --output web/data/song_dance.json

# Also show a matplotlib joint-angle preview
poetry run python -m music path/to/song.mp3 --visualize
```

### View in the browser

```bash
make web
# → http://localhost:8000
```

Open the page, press **播放** (Play). The 3D Astro Boy model animates in sync with the audio.

> **Note:** The web viewer fetches `data/molihua_dance.json` by default. Pass `--output web/data/molihua_dance.json` or edit the `fetch(...)` URL in `web/js/robtic.js` to match your filename.

### Analyze spectrum only

```bash
make analyze AUDIO=path/to/song.mp3
```

---

## Development

```bash
make test          # run all pytest tests
make example       # run examples/basic_usage.py
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
