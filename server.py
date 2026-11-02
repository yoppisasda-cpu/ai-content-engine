"""
AI Content Material Engine Server
FastAPI Server providing API for video analysis, prompt extraction,
production storyboarding, and batch exporting.
"""

import sys
import os
import re
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure proper path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Ensure tools in virtual environment Scripts and winget are in PATH
scripts_dir = str(Path(sys.executable).parent)
wan_scripts = r"D:\wan2GP\env_uv\Scripts"
winget_dir = str(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Links")

for p in [scripts_dir, wan_scripts, winget_dir]:
    if p and os.path.exists(p) and p not in os.environ.get("PATH", ""):
        os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")

from engine.presets import PRESETS
from engine.analyzer import ContentAnalyzer
from engine.prompt_builder import PromptBuilder
from engine.batch_manager import BatchManager
from engine.video_stitcher import VideoStitcher
from engine.dialogue import DialogueAnalyzer

app = FastAPI(title="AI Content Material Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
analyzer = ContentAnalyzer()
prompt_builder = PromptBuilder()
batch_manager = BatchManager()
video_stitcher = VideoStitcher()
dialogue_analyzer = DialogueAnalyzer()

# Models
class AnalyzeUrlRequest(BaseModel):
    url: str
    detection_mode: Optional[str] = "smart"
    max_scene_duration: Optional[float] = 5.0
    num_speakers: Optional[int] = 0
    force_refresh: Optional[bool] = False


# ---------- Storyboard persistence ----------
STORYBOARDS_DIR = BASE_DIR / "storyboards"
SAVED_IMAGES_DIR = BASE_DIR / "images" / "saved"
STORYBOARDS_DIR.mkdir(parents=True, exist_ok=True)
SAVED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def _cache_key(url: str, mode: str, max_dur: float, num_speakers: int = 0) -> str:
    clean_url = url.strip().split("?")[0].rstrip("/")
    return hashlib.md5(f"{clean_url}|{mode}|{max_dur}|{num_speakers}".encode()).hexdigest()[:12]


def _safe_id(sb_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", sb_id or ""):
        raise HTTPException(status_code=400, detail="ID storyboard tidak valid.")
    return sb_id


def _save_storyboard(storyboard: dict, url: str, mode: str, max_dur: float, num_speakers: int = 0) -> dict:
    key = _cache_key(url, mode, max_dur, num_speakers)
    img_dir = SAVED_IMAGES_DIR / key
    if img_dir.exists():
        shutil.rmtree(img_dir, ignore_errors=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    # Save audio if present
    temp_audio = BASE_DIR / "references" / "temp_audio.wav"
    if temp_audio.exists():
        dst_audio = img_dir / "audio.wav"
        shutil.copy2(temp_audio, dst_audio)
        storyboard["audio_url"] = f"/images/saved/{key}/audio.wav"
        storyboard["audio_abs_path"] = str(dst_audio)

    # Copy keyframes into a dedicated folder so later analyses don't overwrite them
    path_map = {}
    for kf in storyboard.get("keyframes", []):
        src = kf.get("abs_path")
        if src and Path(src).exists():
            dst = img_dir / Path(src).name
            shutil.copy2(src, dst)
            new_url = f"/images/saved/{key}/{dst.name}"
            path_map[kf["frame_path"]] = new_url
            kf["frame_path"] = new_url
            kf["abs_path"] = str(dst)
    for sc in storyboard.get("scenes", []):
        if sc.get("frame_preview") in path_map:
            sc["frame_preview"] = path_map[sc["frame_preview"]]

    storyboard["id"] = key
    storyboard["source_url"] = url
    storyboard["detection_mode"] = mode
    storyboard["max_scene_duration"] = max_dur
    storyboard["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    storyboard["thumbnail"] = storyboard["scenes"][0].get("frame_preview", "") if storyboard.get("scenes") else ""

    with open(STORYBOARDS_DIR / f"{key}.json", "w", encoding="utf-8") as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)
    return storyboard

class GenerateConceptRequest(BaseModel):
    title: str
    concept: str
    style: str = "Photorealistic"
    model_target: str = "Wan 2.1 1.3B (Local)"

class ExportBatchRequest(BaseModel):
    storyboard: Dict[str, Any]
    package_name: Optional[str] = "runpod_batch"

class StitchRequest(BaseModel):
    clip_paths: List[str]
    audio_path: Optional[str] = None
    output_name: Optional[str] = "final_output.mp4"

# API Endpoints
@app.get("/api/presets")
def get_presets():
    """Return all curated viral format presets."""
    return list(PRESETS.values())

@app.get("/api/presets/{preset_id}")
def get_preset_detail(preset_id: str):
    """Return single preset."""
    if preset_id not in PRESETS:
        raise HTTPException(status_code=404, detail="Preset tidak ditemukan")
    return PRESETS[preset_id]

@app.post("/api/analyze-url")
def analyze_url(req: AnalyzeUrlRequest):
    """
    Download video via yt-dlp, transcribe with Whisper,
    detect precision scene cuts with FFmpeg, and build production prompt sheet.
    """
    if not req.url or not req.url.startswith("http"):
        raise HTTPException(status_code=400, detail="URL video tidak valid.")

    mode = req.detection_mode or "smart"
    max_dur = req.max_scene_duration if req.max_scene_duration is not None else 5.0
    num_spk = req.num_speakers if req.num_speakers is not None else 0

    # Return cached result if this URL + settings was analyzed before
    cached_file = STORYBOARDS_DIR / f"{_cache_key(req.url, mode, max_dur, num_spk)}.json"
    if cached_file.exists() and not req.force_refresh:
        with open(cached_file, "r", encoding="utf-8") as f:
            return {"success": True, "cached": True, "data": json.load(f)}

    try:
        vid_info = analyzer.download_reference_video(req.url, output_name="ref_download")
        transcription = analyzer.extract_audio_and_transcribe(vid_info["video_path"])
        storyboard = analyzer.analyze_and_deconstruct(
            vid_info=vid_info,
            transcription=transcription,
            mode=mode,
            max_scene_duration=max_dur
        )

        # Diarize dialogue if models available and segments exist
        temp_audio = BASE_DIR / "references" / "temp_audio.wav"
        if temp_audio.exists() and transcription.get("segments") and dialogue_analyzer.models_available():
            try:
                storyboard["dialogue"] = dialogue_analyzer.analyze(
                    str(temp_audio),
                    transcription.get("segments", []),
                    num_speakers=num_spk
                )
            except Exception as e:
                print(f"[Server] Dialogue diarization error: {e}")

        storyboard = _save_storyboard(storyboard, req.url, mode, max_dur, num_spk)
        return {
            "success": True,
            "cached": False,
            "data": storyboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateDialogueRequest(BaseModel):
    num_speakers: Optional[int] = None
    speaker_names: Optional[Dict[str, str]] = None


@app.post("/api/storyboards/{sb_id}/dialogue")
def update_storyboard_dialogue(sb_id: str, req: UpdateDialogueRequest):
    """Re-run diarization or update speaker names for a saved storyboard."""
    sb_id = _safe_id(sb_id)
    fp = STORYBOARDS_DIR / f"{sb_id}.json"
    if not fp.exists():
        raise HTTPException(status_code=404, detail="Storyboard tidak ditemukan.")
    with open(fp, "r", encoding="utf-8") as f:
        storyboard = json.load(f)

    # Rename speakers only
    if req.speaker_names is not None and req.num_speakers is None:
        if "dialogue" in storyboard and "speakers" in storyboard["dialogue"]:
            for spk in storyboard["dialogue"]["speakers"]:
                if spk["label"] in req.speaker_names:
                    spk["name"] = req.speaker_names[spk["label"]]
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)
        return {"success": True, "data": storyboard}

    # Re-run diarization with new speaker count
    audio_path = SAVED_IMAGES_DIR / sb_id / "audio.wav"
    if not audio_path.exists():
        audio_path = BASE_DIR / "references" / "temp_audio.wav"
    if not audio_path.exists():
        raise HTTPException(status_code=400, detail="File audio tidak ditemukan untuk diarization.")

    segs = storyboard.get("transcription_segments") or []
    if not segs and "dialogue" in storyboard and "lines" in storyboard["dialogue"]:
        segs = [{"start": l["start"], "end": l["end"], "text": l["text"]} for l in storyboard["dialogue"]["lines"]]

    dialogue_script = dialogue_analyzer.analyze(
        str(audio_path),
        segs,
        num_speakers=req.num_speakers if req.num_speakers is not None else 0
    )
    if req.speaker_names:
        for spk in dialogue_script["speakers"]:
            if spk["label"] in req.speaker_names:
                spk["name"] = req.speaker_names[spk["label"]]

    storyboard["dialogue"] = dialogue_script
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)
    return {"success": True, "data": storyboard}


@app.get("/api/storyboards")
def list_storyboards():
    """List all saved storyboards (newest first)."""
    items = []
    for fp in STORYBOARDS_DIR.glob("*.json"):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                d = json.load(f)
            items.append({
                "id": d.get("id", fp.stem),
                "title": d.get("title", fp.stem),
                "source_url": d.get("source_url", ""),
                "duration": d.get("duration", ""),
                "scene_count": len(d.get("scenes", [])),
                "detection_mode": d.get("detection_mode", ""),
                "max_scene_duration": d.get("max_scene_duration"),
                "saved_at": d.get("saved_at", ""),
                "thumbnail": d.get("thumbnail", ""),
            })
        except Exception:
            continue
    items.sort(key=lambda x: x["saved_at"], reverse=True)
    return items


@app.get("/api/storyboards/{sb_id}")
def get_storyboard(sb_id: str):
    fp = STORYBOARDS_DIR / f"{_safe_id(sb_id)}.json"
    if not fp.exists():
        raise HTTPException(status_code=404, detail="Storyboard tidak ditemukan.")
    with open(fp, "r", encoding="utf-8") as f:
        return {"success": True, "data": json.load(f)}


@app.delete("/api/storyboards/{sb_id}")
def delete_storyboard(sb_id: str):
    sb_id = _safe_id(sb_id)
    fp = STORYBOARDS_DIR / f"{sb_id}.json"
    if fp.exists():
        fp.unlink()
    shutil.rmtree(SAVED_IMAGES_DIR / sb_id, ignore_errors=True)
    return {"success": True}

@app.post("/api/generate-concept")
def generate_concept(req: GenerateConceptRequest):
    """Generate production prompt storyboard from raw concept / script."""
    try:
        storyboard = prompt_builder.generate_from_concept(
            title=req.title,
            concept=req.concept,
            style=req.style,
            model_target=req.model_target
        )
        return {
            "success": True,
            "data": storyboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export-batch")
def export_batch(req: ExportBatchRequest):
    """Export RunPod / Wan2GP batch jobs JSON and runner zip package."""
    try:
        result = batch_manager.export_batch_package(
            storyboard=req.storyboard,
            package_name=req.package_name or "runpod_batch"
        )
        return {
            "success": True,
            "data": result,
            "download_url": f"/exports/{result['zip_filename']}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stitch")
def stitch_video(req: StitchRequest):
    """Stitch clips using FFmpeg."""
    try:
        result = video_stitcher.stitch_clips(
            clip_paths=req.clip_paths,
            audio_path=req.audio_path,
            output_name=req.output_name or "final_stitched_video.mp4"
        )
        return {
            "success": True,
            "data": result,
            "video_url": f"/videos/{result['filename']}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
def get_system_status():
    """Returns local system status and Wan2GP link."""
    return {
        "engine": "AI Content Material Engine v1.0",
        "wan2gp_url": "http://localhost:7861",
        "status": "Online",
        "gpu_available": True
    }

# Mount static folders for images, exports, videos, and frontend
app.mount("/images", StaticFiles(directory=str(BASE_DIR / "images")), name="images")
app.mount("/exports", StaticFiles(directory=str(BASE_DIR / "exports")), name="exports")
app.mount("/videos", StaticFiles(directory=str(BASE_DIR / "videos")), name="videos")
app.mount("/workflows", StaticFiles(directory=str(BASE_DIR / "workflows")), name="workflows")

# Mount frontend
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("[AI Content Engine] Starting on http://localhost:8500 ...")
    uvicorn.run("server:app", host="0.0.0.0", port=8500, reload=True)
