"""
Prompt Builder & Storyboard Generator
Generates production-grade Storyboard Sheets from raw text ideas, scripts, or creative briefs.
"""

from typing import Dict, Any, List

class PromptBuilder:
    def __init__(self):
        pass

    def generate_from_concept(self, title: str, concept: str, style: str = "Photorealistic", model_target: str = "Wan 2.1 1.3B (Local)") -> Dict[str, Any]:
        """
        Creates a 3-4 scene production storyboard based on user concept.
        """
        is_cartoon = "cartoon" in style.lower() or "pixar" in style.lower() or "3d" in style.lower()
        is_anime = "anime" in style.lower() or "ghibli" in style.lower()

        if is_cartoon:
            style_desc = "3D Pixar Disney style animation, vibrant colors, expressive facial features, subsurface scattering, whimsical warm cinematic lighting"
            neg_prompt = "photorealistic, live action, uncanny valley, ugly, low poly, distorted limbs, jerky camera."
        elif is_anime:
            style_desc = "Makoto Shinkai and Studio Ghibli inspired anime aesthetic, lush painted backgrounds, glowing golden sunlight, rich emotional color palette"
            neg_prompt = "3D render, western cartoon, flat colors, blurry, noisy, bad anatomy."
        else:
            style_desc = "Photorealistic 8k vertical 9:16 cinematic video, natural directional lighting, shallow depth of field, shot on 35mm lens, award-winning cinematography"
            neg_prompt = "cartoon, 3d render, plastic skin, distorted fingers, extra limbs, jittery movement, low resolution, blurry."

        scenes: List[Dict[str, Any]] = [
            {
                "scene_num": 1,
                "timecode": "00:00 - 00:04",
                "duration": "4s",
                "shot_type": "Hook (Establishing / Action Intro)",
                "image_prompt": f"Dramatic opening shot of {concept}. {style_desc}, perfectly centered hero subject, eye-catching composition designed to stop the scroll.",
                "motion_prompt": f"Cinematic slow forward camera push-in. Natural organic motion of the subject engaging directly towards the frame. Subtle atmospheric dust and lighting particles.",
                "negative_prompt": neg_prompt,
                "audio_sfx": "Impactful bass whoosh hook, energetic upbeat ambient intro sound, crisp Foley sound.",
                "editing_notes": "Hard cut hook. Add bold animated dynamic title on screen within the first 1.2 seconds."
            },
            {
                "scene_num": 2,
                "timecode": "00:04 - 00:09",
                "duration": "5s",
                "shot_type": "Core Action (Detail & Motion)",
                "image_prompt": f"Close-up medium shot focusing on the key activity of {concept}. {style_desc}, intense textural details, vivid highlights, dynamic depth of field.",
                "motion_prompt": f"Smooth tracking shot following the main action. Realistic physics and fluid movement. Consistent subject identity, lifelike gestures.",
                "negative_prompt": neg_prompt,
                "audio_sfx": "Rich Foley textures matching the hand/body action, satisfying tactile sound effects, rhythm-driven beat.",
                "editing_notes": "Pacing rhythm: cut exactly on the peak motion beat. Speed ramp 1.2x -> 0.9x for dramatic effect."
            },
            {
                "scene_num": 3,
                "timecode": "00:09 - 00:14",
                "duration": "5s",
                "shot_type": "Climax & Outro (Call to Action)",
                "image_prompt": f"Hero resolution shot of {concept}, subject smiling or celebrating the outcome. {style_desc}, golden backlight rim, warm comforting atmosphere.",
                "motion_prompt": f"Gentle slow-motion camera drift. Subject delivers a friendly micro-expression or gesture towards the camera. Smooth cinematic wind and hair motion.",
                "negative_prompt": neg_prompt,
                "audio_sfx": "Uplifting musical crescendo, cheerful notification chime, warm outro fade.",
                "editing_notes": "Hold final frame for 1.5 seconds. Display call to action ('Comment for Part 2' or Follow button)."
            }
        ]

        return {
            "title": title or "New Creative Storyboard",
            "concept": concept,
            "style": style,
            "recommended_model": model_target,
            "resolution": "480x848 (Local 1.3B) / 720x1280 (RunPod 14B)",
            "scenes": scenes
        }
