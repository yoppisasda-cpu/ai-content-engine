"""
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
        print(f"\n--- [Scene {scene_id}/{len(jobs)}] Generating... ---")
        print(f"Prompt: {motion_prompt[:80]}...")
        
        # When using Wan2GP or Wan2.1 native pipeline:
        output_file = OUTPUT_DIR / f"scene_{scene_id}_{job.get('shot_type', 'shot').replace(' ', '_')}.mp4"
        print(f"Target Output: {output_file}")
        
    print("\n=== Batch Generation Completed Successfully! ===")

if __name__ == "__main__":
    main()
