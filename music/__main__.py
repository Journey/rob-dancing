"""CLI entry point for Rob-Dancing.

Usage:
    poetry run python -m music <audio_file> [options]

Examples:
    poetry run python -m music music/molihua.mp4
    poetry run python -m music song.mp3 --output web/data/song_dance.json
    poetry run python -m music song.mp3 --visualize
"""

import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m music",
        description="Rob-Dancing: generate robot choreography from music.",
    )
    parser.add_argument(
        "audio_file",
        help="Path to an audio file (mp3, mp4, wav, flac, ogg, …)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output JSON path (default: <audio_stem>_dance.json beside the audio file)",
    )
    parser.add_argument(
        "--visualize", "-v",
        action="store_true",
        help="Show a matplotlib joint-angle preview after generation",
    )
    args = parser.parse_args()

    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"Error: audio file not found: {args.audio_file}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else (
        audio_path.parent / f"{audio_path.stem}_dance.json"
    )

    from .dancer.dance_system import DanceSystem

    system = DanceSystem()
    dance_data = system.create_dance_from_music(str(audio_path))
    system.save_dance_sequence(dance_data, str(output_path))

    print(f"\nSummary")
    print(f"  Audio    : {audio_path.name}")
    print(f"  Tempo    : {dance_data['tempo']:.1f} BPM")
    print(f"  Duration : {dance_data['duration']:.1f}s")
    print(f"  Keyframes: {len(dance_data['keyframes'])}")
    print(f"  Output   : {output_path}")

    if args.visualize:
        system.visualize_dance(dance_data)


if __name__ == "__main__":
    main()
