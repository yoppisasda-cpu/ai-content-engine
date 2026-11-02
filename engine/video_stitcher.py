"""
Video Stitcher & Assembler
Combines generated video shots and audio tracks into a finished master MP4 using FFmpeg.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any
from engine.analyzer import _find_bin

BASE_DIR = Path(__file__).resolve().parent.parent
VIDEOS_DIR = BASE_DIR / "videos"
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

class VideoStitcher:
    def __init__(self):
        pass

    def stitch_clips(self, clip_paths: List[str], audio_path: str = None, output_name: str = "final_stitched_video.mp4") -> Dict[str, Any]:
        """
        Stitches a list of video clips into one cohesive video using FFmpeg concat.
        """
        valid_clips = [p for p in clip_paths if Path(p).exists()]
        if not valid_clips:
            raise FileNotFoundError("Tidak ada klip video valid yang ditemukan untuk digabung.")

        # Create concat text file
        concat_file = VIDEOS_DIR / "concat_list.txt"
        with open(concat_file, "w", encoding="utf-8") as f:
            for p in valid_clips:
                clean_path = str(Path(p).resolve()).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        output_path = VIDEOS_DIR / output_name

        ffmpeg_bin = _find_bin("ffmpeg")
        if audio_path and Path(audio_path).exists():
            # Concat with external audio overlay
            cmd = [
                ffmpeg_bin, "-y",
                "-f", "concat", "-safe", "0", "-i", str(concat_file),
                "-i", audio_path,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(output_path)
            ]
        else:
            # Simple concat
            cmd = [
                ffmpeg_bin, "-y",
                "-f", "concat", "-safe", "0", "-i", str(concat_file),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                str(output_path)
            ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {res.stderr[:200]}")

        return {
            "success": True,
            "output_path": str(output_path),
            "filename": output_path.name,
            "total_clips": len(valid_clips)
        }
