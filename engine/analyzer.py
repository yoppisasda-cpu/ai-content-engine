"""
Video & Content Analyzer Engine
Extracts video, audio, transcripts, and keyframes from URLs (Instagram, TikTok, YouTube)
and deconstructs them into production storyboards and Wan2GP motion prompts.
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = BASE_DIR / "references"
IMAGES_DIR = BASE_DIR / "images"
VIDEOS_DIR = BASE_DIR / "videos"

REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


import shutil

# Ensure PATH includes Scripts directories (virtual environment) and WinGet links
scripts_dir = str(Path(sys.executable).parent)
wan_scripts = r"D:\wan2GP\env_uv\Scripts"
winget_dir = str(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Links")

for p in [scripts_dir, wan_scripts, winget_dir]:
    if p and os.path.exists(p) and p not in os.environ.get("PATH", ""):
        os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")


def _find_bin(name: str) -> str:
    """Find binary executable with multiple fallbacks."""
    found = shutil.which(name)
    if found:
        return found
    candidates_dirs = [
        Path(sys.executable).parent,
        Path(sys.executable).parent / "Scripts",
        Path(r"D:\wan2GP\env_uv\Scripts"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Links",
    ]
    for d in candidates_dirs:
        for ext in [".exe", ".cmd", ".bat", ""]:
            cand = d / f"{name}{ext}"
            if cand.exists():
                return str(cand)
    return name


def _get_ytdlp_cmd() -> list:
    """Return command list for invoking yt-dlp."""
    bin_path = _find_bin("yt-dlp")
    if bin_path and (shutil.which(bin_path) or Path(bin_path).exists()):
        return [bin_path]
    return [sys.executable, "-m", "yt_dlp"]


class ContentAnalyzer:
    def __init__(self):
        self.whisper_model = None

    def _get_whisper(self):
        if self.whisper_model is None:
            import whisper
            # Use 'tiny' or 'base' for quick inference without high VRAM usage
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model

    def download_reference_video(self, url: str, output_name: str = "reference_video") -> dict:
        """
        Download video from URL using yt-dlp and extract metadata.
        """
        # Clean up any existing files with this prefix
        for old_file in REFERENCES_DIR.glob(f"{output_name}.*"):
            try:
                old_file.unlink()
            except Exception:
                pass

        output_template = str(REFERENCES_DIR / f"{output_name}.%(ext)s")
        cmd = _get_ytdlp_cmd() + [
            "-f", "mp4/bestvideo+bestaudio/best",
            "--no-playlist",
            "--force-overwrites",
            "--windows-filenames",
            "-o", output_template,
            url
        ]

        print(f"[Analyzer] Downloading video from {url}...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[Analyzer] yt-dlp error: {res.stderr}")
            raise RuntimeError(f"Gagal mendownload video: {res.stderr[:200]}")

        # Find the downloaded file
        downloaded_files = list(REFERENCES_DIR.glob(f"{output_name}.*"))
        video_file = None
        for f in downloaded_files:
            if f.suffix.lower() in [".mp4", ".mkv", ".webm"]:
                video_file = f
                break

        if not video_file or not video_file.exists():
            raise FileNotFoundError("Video berhasil di-download tapi file tidak ditemukan.")

        # Probe video metadata using ffprobe
        ffprobe_bin = _find_bin("ffprobe")
        probe_cmd = [
            ffprobe_bin, "-v", "error",
            "-show_entries", "format=duration:stream=width,height,r_frame_rate,duration",
            "-of", "json",
            str(video_file)
        ]
        probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
        meta = {}
        if probe_res.returncode == 0:
            try:
                meta = json.loads(probe_res.stdout)
            except Exception:
                pass

        duration = 0.0
        if "format" in meta and "duration" in meta["format"]:
            try:
                duration = float(meta["format"]["duration"])
            except Exception:
                pass

        if duration <= 0.0 and "streams" in meta:
            for s in meta.get("streams", []):
                if "duration" in s:
                    try:
                        duration = float(s["duration"])
                        if duration > 0:
                            break
                    except Exception:
                        pass

        if duration <= 0.0:
            duration = 15.0

        return {
            "video_path": str(video_file),
            "filename": video_file.name,
            "duration": round(duration, 2),
            "metadata": meta
        }

    def extract_audio_and_transcribe(self, video_path: str) -> dict:
        """
        Extract audio from video using FFmpeg and transcribe using Whisper.
        """
        audio_path = REFERENCES_DIR / "temp_audio.wav"
        if audio_path.exists():
            try:
                audio_path.unlink()
            except Exception:
                pass

        ffmpeg_bin = _find_bin("ffmpeg")
        extract_cmd = [
            ffmpeg_bin, "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            str(audio_path)
        ]
        subprocess.run(extract_cmd, capture_output=True)

        if not audio_path.exists():
            return {"text": "", "segments": []}

        try:
            model = self._get_whisper()
            result = model.transcribe(str(audio_path))
            return {
                "text": result.get("text", "").strip(),
                "segments": result.get("segments", [])
            }
        except Exception as e:
            print(f"[Analyzer] Whisper transcription warning: {e}")
            return {"text": "", "segments": []}

    def detect_scene_boundaries(self, video_path: str, total_dur: float, whisper_segments: list, mode: str = "smart", max_scene_dur: float = 5.0) -> list:
        """
        High-precision scene boundary detection using FFmpeg visual scene cuts + Whisper speech sync.
        Modes:
          - 'smart': Combines real visual cuts with dialogue pause subdivisions for Wan2GP (3s - 5s).
          - 'visual_cut': Strict camera angle changes only.
          - 'speech_beat': Cuts strictly per Whisper sentence / dialogue pause.
          - 'fixed': Regular time slices (default max_scene_dur).
        """
        ffmpeg_bin = _find_bin("ffmpeg")
        total_dur = max(float(total_dur), 1.0)
        
        # Mode: Fixed time slices
        if mode == "fixed":
            step = max_scene_dur if max_scene_dur > 0 else 4.0
            bounds = [0.0]
            cur = step
            while cur < (total_dur - 1.0):
                bounds.append(round(cur, 2))
                cur += step
            bounds.append(round(total_dur, 2))
            return bounds

        # 1. Detect visual cuts via FFmpeg
        raw_cuts = []
        if mode in ["smart", "visual_cut"]:
            cmd = [
                ffmpeg_bin, "-i", video_path,
                "-filter:v", "select=gt(scene\\,0.20),showinfo",
                "-f", "null", "-"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
            matches = re.findall(r"pts_time:([0-9\.]+)", res.stderr)
            raw_cuts = [float(t) for t in matches]

        # Filter out cuts too close to edges (< 0.8s) or too close to each other (< 1.2s)
        filtered_cuts = []
        for c in raw_cuts:
            if 0.8 <= c <= (total_dur - 0.8):
                if not filtered_cuts or (c - filtered_cuts[-1]) >= 1.2:
                    filtered_cuts.append(round(c, 2))

        # Initial boundaries
        raw_bounds = [0.0] + filtered_cuts + [round(total_dur, 2)]
        bounds = [raw_bounds[0]]
        for b in raw_bounds[1:]:
            if (b - bounds[-1]) >= 1.0:
                bounds.append(b)
            else:
                bounds[-1] = b

        # If speech_beat mode OR no visual cuts found in a multi-second video, use Whisper segments
        if mode == "speech_beat" or (len(bounds) <= 2 and whisper_segments and total_dur > 4.0):
            speech_bounds = [0.0]
            for s in whisper_segments:
                s_end = round(s.get("end", 0.0), 2)
                if (s_end - speech_bounds[-1]) >= 2.2 and (total_dur - s_end) >= 1.5:
                    speech_bounds.append(s_end)
            if round(total_dur, 2) not in speech_bounds:
                speech_bounds.append(round(total_dur, 2))
            bounds = speech_bounds

        # If smart mode and max_scene_dur > 0, subdivide long cuts (> 1.25 * max_scene_dur)
        final_bounds = []
        for i in range(len(bounds) - 1):
            st = bounds[i]
            et = bounds[i + 1]
            shot_dur = et - st
            final_bounds.append(st)

            if mode == "smart" and max_scene_dur > 0 and shot_dur > (max_scene_dur * 1.25):
                target_splits = int(round(shot_dur / max_scene_dur))
                if target_splits < 2:
                    target_splits = 2
                ideal_interval = shot_dur / target_splits

                last_split = st
                for s_idx in range(1, target_splits):
                    ideal_split = st + s_idx * ideal_interval
                    best_sub = None
                    best_diff = 999.0
                    for seg in whisper_segments:
                        seg_end = round(seg.get("end", 0.0), 2)
                        if (seg_end - last_split) >= 2.0 and (et - seg_end) >= 1.8:
                            diff = abs(seg_end - ideal_split)
                            if diff < best_diff and diff <= 1.8:
                                best_diff = diff
                                best_sub = seg_end
                    if best_sub is None:
                        best_sub = round(ideal_split, 2)
                    final_bounds.append(best_sub)
                    last_split = best_sub

        final_bounds.append(round(total_dur, 2))
        return final_bounds

    def extract_keyframes_for_scenes(self, video_path: str, boundaries: list) -> list:
        """
        Extract high quality keyframe for each detected scene at its stable midpoint.
        """
        ffmpeg_bin = _find_bin("ffmpeg")
        frames = []

        for i in range(len(boundaries) - 1):
            st = boundaries[i]
            et = boundaries[i + 1]
            # Sample at 38% into the scene (stable frame, avoiding cut transition artifacts)
            frame_time = round(st + (et - st) * 0.38, 2)
            frame_name = f"scene_{i + 1}_{int(frame_time * 100)}ms.jpg"
            frame_path = IMAGES_DIR / frame_name

            extract_frame = [
                ffmpeg_bin, "-y", "-ss", str(frame_time),
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "2",
                str(frame_path)
            ]
            subprocess.run(extract_frame, capture_output=True)
            if frame_path.exists():
                frames.append({
                    "scene_num": i + 1,
                    "timestamp": frame_time,
                    "frame_path": f"/images/{frame_name}",
                    "abs_path": str(frame_path)
                })
            else:
                frames.append({
                    "scene_num": i + 1,
                    "timestamp": frame_time,
                    "frame_path": "",
                    "abs_path": ""
                })

        return frames

    def deconstruct_into_storyboard(self, video_info: dict, transcription: dict, keyframes: list, boundaries: list = None) -> dict:
        """
        Takes raw video analysis and constructed boundaries to produce precise Storyboard Scenes.
        """
        duration = video_info.get("duration", 15.0)
        speech_text = transcription.get("text", "")
        segments = transcription.get("segments", [])

        if not boundaries or len(boundaries) < 2:
            boundaries = [0.0, round(duration, 2)]

        num_scenes = len(boundaries) - 1
        scenes = []

        for i in range(num_scenes):
            start_t = boundaries[i]
            end_t = boundaries[i + 1]
            scene_dur = round(end_t - start_t, 2)

            # Precise timecode e.g. 00:00.0 - 00:03.7
            tc_start = f"{int(start_t // 60):02d}:{start_t % 60:04.1f}"
            tc_end = f"{int(end_t // 60):02d}:{end_t % 60:04.1f}"
            timecode = f"{tc_start} - {tc_end}"

            # Match segments overlapping this scene
            matched_texts = []
            for s in segments:
                s_st = s.get("start", 0.0)
                s_et = s.get("end", 0.0)
                # Overlap test with 0.25s tolerance
                if (s_st < (end_t + 0.15) and s_et > (start_t - 0.15)):
                    matched_texts.append(s.get("text", "").strip())
            
            # Deduplicate text
            clean_texts = []
            for t in matched_texts:
                if t and t not in clean_texts:
                    clean_texts.append(t)
            scene_speech = " ".join(clean_texts).strip()

            frame_preview = keyframes[i]["frame_path"] if i < len(keyframes) else ""

            # Dynamic shot classification based on progression and duration
            if i == 0:
                shot_type = "Hook & Pembuka Visual"
                img_prompt = f"Dramatic opening hook shot, photorealistic 8k vertical 9:16 master composition, intense cinematic lighting, centered hero subject captivating the viewer immediately. Detail: '{scene_speech or 'High energy opening'}'"
                motion_prompt = "Dynamic slow forward camera zoom-in, natural micro-movements of subject, crisp lighting, high quality motion blur, stable framing."
                audio_sfx = f"Punchy sound effect, whoosh transition. Voiceover: \"{scene_speech or 'Opening Hook'}\""
                edit_notes = f"Pacing sangat cepat ({scene_dur}s). Munculkan hook visual dan teks judul di 1 detik pertama untuk retensi penonton."
            elif i == num_scenes - 1:
                shot_type = "Climax & Outro CTA"
                img_prompt = f"Satisfying resolution shot, golden hour cinematic backlight, premium 8k vertical composition. Subject delivers punchline: '{scene_speech or 'Follow for more'}'"
                motion_prompt = "Subtle cinematic camera drift, character delivers a friendly expression or smile, peaceful ambient atmospheric motion."
                audio_sfx = f"Triumphant musical cue, outro bell chime. Voiceover: \"{scene_speech or 'Follow for more'}\""
                edit_notes = f"Pacing penutup ({scene_dur}s). Beri ruang untuk teks Call-To-Action (Follow / Komentar) di sepertiga bawah layar."
            elif scene_speech:
                shot_type = f"Dialog & Reaksi #{i}"
                img_prompt = f"Detailed medium vertical shot, cinematic lighting, vivid emotional expression. Context: '{scene_speech[:75]}'"
                motion_prompt = "Steady medium-close shot, subtle head and hand micro-gestures synchronized with dialogue pacing, realistic physics, smooth camera stabilization."
                audio_sfx = f"Natural Foley textures matching action. Voiceover: \"{scene_speech}\""
                edit_notes = f"Cut tepat pada jeda dialog ({scene_dur}s). Pertahankan tempo dinamis mengikuti alur percakapan."
            else:
                shot_type = f"Action Beat #{i}"
                img_prompt = "Detailed dynamic shot showing main action, warm atmospheric lighting, high fidelity textures and depth of field."
                motion_prompt = "Smooth fluid movement tracking the action, realistic physics, steady cinematography, vivid lighting highlights."
                audio_sfx = "Ambient room atmosphere, Foley textures matching the movement."
                edit_notes = f"Match cut on action ({scene_dur}s), sinkronkan dengan beat musik latar."

            scenes.append({
                "scene_num": i + 1,
                "timecode": timecode,
                "duration": f"{scene_dur}s",
                "shot_type": shot_type,
                "frame_preview": frame_preview,
                "image_prompt": img_prompt,
                "motion_prompt": motion_prompt,
                "negative_prompt": "blurry, low quality, distorted anatomy, jitter, glitch, artifacts, ugly, deformed limbs.",
                "audio_sfx": audio_sfx,
                "editing_notes": edit_notes
            })

        return {
            "title": f"Bedah Video: {video_info.get('filename', 'Reference')}",
            "duration": f"{round(duration, 2)}s",
            "detection_summary": f"Terdeteksi {num_scenes} adegan presisi (rata-rata {round(duration / num_scenes, 1)}s per scene)",
            "transcription": speech_text,
            "transcription_segments": segments,
            "scenes": scenes,
            "keyframes": keyframes
        }

    def analyze_and_deconstruct(self, vid_info: dict, transcription: dict, mode: str = "smart", max_scene_duration: float = 5.0) -> dict:
        """
        Full orchestration of precision scene detection, keyframing, and storyboard generation.
        """
        video_path = vid_info["video_path"]
        duration = vid_info.get("duration", 15.0)
        whisper_segments = transcription.get("segments", [])

        print(f"[Analyzer] Detecting scene cuts with mode='{mode}', max_dur={max_scene_duration}s...")
        boundaries = self.detect_scene_boundaries(
            video_path=video_path,
            total_dur=duration,
            whisper_segments=whisper_segments,
            mode=mode,
            max_scene_dur=max_scene_duration
        )
        print(f"[Analyzer] Found {len(boundaries) - 1} scenes: {boundaries}")

        print("[Analyzer] Extracting precision keyframes per scene...")
        keyframes = self.extract_keyframes_for_scenes(video_path, boundaries)

        print("[Analyzer] Deconstructing into actionable Wan2GP storyboards...")
        storyboard = self.deconstruct_into_storyboard(
            video_info=vid_info,
            transcription=transcription,
            keyframes=keyframes,
            boundaries=boundaries
        )
        return storyboard
