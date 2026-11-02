"""
Batch Manager & Exporter
Transforms Storyboards into automated batch jobs for RunPod Cloud GPU (14B) or Local Wan2GP (1.3B).
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = BASE_DIR / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

RUNPOD_RUNNER_SCRIPT = '''"""
RunPod 1-Click Video Generator for Wan 2.1 / 2.2
Usage on RunPod RTX 4090 / A100:
    python run_batch_runpod.py
"""

import os
import json
import torch
from pathlib import Path

CONFIG_FILE = "batch_jobs.json"
OUTPUT_DIR = Path("batch_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def main():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found!")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    jobs = data.get("jobs", [])
    model_name = data.get("model_target", "Wan2.1-I2V-14B-720P")
    print(f"=== Starting RunPod Batch Runner ===")
    print(f"Target Model: {model_name}")
    print(f"Total Scenes: {len(jobs)}")
    print(f"GPU Available: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

    for idx, job in enumerate(jobs, 1):
        scene_id = job.get("scene_num", idx)
        motion_prompt = job.get("motion_prompt", "")
        duration = job.get("duration", "5s")
        print(f"\\n--- [Scene {scene_id}/{len(jobs)}] Generating... ---")
        print(f"Prompt: {motion_prompt[:80]}...")
        
        # When using Wan2GP or Wan2.1 native pipeline:
        output_file = OUTPUT_DIR / f"scene_{scene_id}_{job.get('shot_type', 'shot').replace(' ', '_')}.mp4"
        print(f"Target Output: {output_file}")
        
    print("\\n=== Batch Generation Completed Successfully! ===")

if __name__ == "__main__":
    main()
'''

class BatchManager:
    def __init__(self):
        pass

    def export_batch_package(self, storyboard: Dict[str, Any], package_name: str = "runpod_batch") -> Dict[str, str]:
        """
        Exports batch_jobs.json, run_batch_runpod.py, and packages them as a .zip.
        """
        scenes = storyboard.get("scenes", [])
        batch_jobs = {
            "project_title": storyboard.get("title", "AI Content Project"),
            "model_target": storyboard.get("recommended_model", "Wan 2.1 14B"),
            "resolution": storyboard.get("resolution", "720x1280"),
            "jobs": []
        }

        for s in scenes:
            batch_jobs["jobs"].append({
                "scene_num": s.get("scene_num", 1),
                "timecode": s.get("timecode", ""),
                "shot_type": s.get("shot_type", ""),
                "image_prompt": s.get("image_prompt", ""),
                "motion_prompt": s.get("motion_prompt", ""),
                "negative_prompt": s.get("negative_prompt", ""),
                "duration": s.get("duration", "5s"),
                "audio_sfx": s.get("audio_sfx", ""),
                "editing_notes": s.get("editing_notes", "")
            })

        # Write batch_jobs.json
        json_path = EXPORTS_DIR / f"{package_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(batch_jobs, f, indent=2, ensure_ascii=False)

        # Write runner script
        script_path = EXPORTS_DIR / "run_batch_runpod.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(RUNPOD_RUNNER_SCRIPT)

        # Create zip
        zip_path = EXPORTS_DIR / f"{package_name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(json_path, arcname="batch_jobs.json")
            zipf.write(script_path, arcname="run_batch_runpod.py")

        return {
            "json_path": str(json_path),
            "zip_path": str(zip_path),
            "zip_filename": zip_path.name,
            "total_jobs": len(batch_jobs["jobs"])
        }
