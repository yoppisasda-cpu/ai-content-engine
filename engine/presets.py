"""
Presets for Viral Video Deconstructions
Contains tested and production-ready prompts, timecodes, motion descriptors,
audio/SFX cues, and editing notes for high-performing formats.
"""

PRESETS = {
    "toddler_mukbang": {
        "id": "toddler_mukbang",
        "title": "🍜 Cute Toddler ASMR Mukbang",
        "description": "Format viral ASMR makan anak kecil dengan ekspresi lucu. Terbukti 100% jalan mulus di Wan 2.1 1.3B lokal (RTX 3070 8GB).",
        "category": "ASMR / Food",
        "recommended_model": "Wan 2.1 1.3B (Local OK - 8GB VRAM)",
        "resolution": "480x848 (9:16)",
        "aspect_ratio": "9:16",
        "scenes": [
            {
                "scene_num": 1,
                "timecode": "00:00 - 00:05",
                "duration": "5s",
                "shot_type": "Medium Close-Up (Hook)",
                "image_prompt": "A cute 3-year-old Asian toddler with chubby cheeks and large curious eyes sitting on a wooden high chair in a warm modern kitchen. The toddler is happily holding chopsticks with curly noodles lifting to their mouth. Soft morning natural light, rim lighting, 8k resolution, photorealistic, cinematic depth of field.",
                "motion_prompt": "The toddler brings the noodles closer to their mouth, slurping enthusiastically with cute cheek twitches. Cheerful eye blinking, slight natural head tilt, wispy hair moving gently. High quality, realistic physics, smooth motion.",
                "negative_prompt": "distorted fingers, extra limbs, bad face, deformed chopsticks, flickering, jittery movement, low quality, cartoon.",
                "audio_sfx": "Crisp ASMR slurping sounds, cute toddler giggle, soft ambient kitchen room tone.",
                "editing_notes": "Hard cut hook. Zoom-in 10% during slurp to emphasize cuteness. Warm color grade."
            },
            {
                "scene_num": 2,
                "timecode": "00:05 - 00:10",
                "duration": "5s",
                "shot_type": "Macro B-Roll (Food Texture)",
                "image_prompt": "Extreme macro close-up of savory ramen noodles with glistening soy broth, chopped scallions, and golden sesame seeds. Rising appetizing hot steam, shallow depth of field, food photography award-winning shot, bokeh background.",
                "motion_prompt": "Gentle curly steam rising continuously from the hot noodles. Glistening broth droplets vibrating subtly. Very slow cinematic camera push-in.",
                "negative_prompt": "static, blurry, muddy colors, artificial smoke, lowres.",
                "audio_sfx": "Faint simmering bubbling sound, satisfying sizzle, ASMR high-frequency crunch.",
                "editing_notes": "Match cut from chopsticks. Pacing slows down for sensory satisfaction."
            },
            {
                "scene_num": 3,
                "timecode": "00:10 - 00:15",
                "duration": "5s",
                "shot_type": "Close-Up (Emotional Reaction)",
                "image_prompt": "Extreme close up on the toddler's face, big round sparkling eyes, joyful wide mouth smile showing tiny baby teeth, cheeks slightly flushed pink with happiness, warm sunlight.",
                "motion_prompt": "The toddler tilts head in pure joy, blinking happily, dimples appearing as they chew and giggle, natural organic facial micro-expressions.",
                "negative_prompt": "plastic skin, unnatural grin, creepy eyes, disfigured mouth, jitter.",
                "audio_sfx": "Cute high-pitched toddler exclamation 'Mmm yummy!', pleasant bell chime note.",
                "editing_notes": "Hold for 3 seconds then whip pan to final call to action."
            }
        ]
    },
    "cat_chef": {
        "id": "cat_chef",
        "title": "🐱 3 Cat Chefs Making Strawberry Daifuku",
        "description": "Video animasi kucing chef membuat mochi tradisional Jepang. Sangat viral di Reels/TikTok. Disarankan Wan 2.1 14B (RunPod) untuk fisika animasi kompleks.",
        "category": "Animated / Cute",
        "recommended_model": "Wan 2.1 14B / RunPod Cloud (Kompleks Antropomorfik)",
        "resolution": "720x1280 (9:16)",
        "aspect_ratio": "9:16",
        "scenes": [
            {
                "scene_num": 1,
                "timecode": "00:00 - 00:04",
                "duration": "4s",
                "shot_type": "Wide Action (Mochitsuki - Pounding)",
                "image_prompt": "Three cute anthropomorphic cats dressed as Japanese pastry chefs wearing white chef hats and aprons, working in a cozy traditional Japanese wooden kitchen. In the center is a wooden mortar filled with white elastic mochi rice dough. Warm ambient lighting, Studio Ghibli meets 3D Pixar photorealism.",
                "motion_prompt": "The ginger cat raises a large wooden mallet and rhythmically pounds the mochi dough in the mortar. The white cat quickly pats and turns the dough between strikes. Flour dust puffs up gracefully. Synchronized dynamic motion.",
                "negative_prompt": "melting cat faces, extra paws, deformed mallet, unnatural morphing, low quality, glitchy frame.",
                "audio_sfx": "Heavy rhythmic wooden thuds 'BOK... BOK', flour puff whoosh, energetic Japanese koto flute BGM.",
                "editing_notes": "High tempo beat-sync. Cut on the impact of the mallet."
            },
            {
                "scene_num": 2,
                "timecode": "00:04 - 00:08",
                "duration": "4s",
                "shot_type": "Medium Close-Up (Dough Stretch & Strawberry)",
                "image_prompt": "The white cat chef delicately stretching soft powdery white mochi dough over a glossy ripe red strawberry coated in sweet red bean paste (anko). Golden hour sunlight filtering through shoji screen.",
                "motion_prompt": "The cat's fluffy paws gently wrap the elastic mochi dough smoothly around the strawberry, pinching the bottom seamlessly. Flour dust dances in sunlight beam.",
                "negative_prompt": "liquid melting hands, distorted fruit, jerky camera, flat lighting.",
                "audio_sfx": "Soft stretchy squish sound, powdery dusting SFX, gentle cat purr.",
                "editing_notes": "Slow-motion 0.75x effect for tactile satisfaction."
            },
            {
                "scene_num": 3,
                "timecode": "00:08 - 00:12",
                "duration": "4s",
                "shot_type": "Macro Reveal (Cross-Section Slice)",
                "image_prompt": "A sharp ceramic knife cleanly slicing a finished strawberry mochi daifuku in half on a bamboo board. Perfect cross-section revealing the vibrant red strawberry, dark red bean paste, and translucent mochi layer.",
                "motion_prompt": "The knife glides smoothly through the mochi, parting both halves to reveal the juicy glossy interior with moisture droplets.",
                "negative_prompt": "rough jagged cuts, mushy textures, blur, static.",
                "audio_sfx": "Crisp knife slice sound 'shhhk', mouthwatering juicy squish, triumphant chime.",
                "editing_notes": "Slow reveal, end with subscribe/follow watermark."
            }
        ]
    },
    "pixar_comedy": {
        "id": "pixar_comedy",
        "title": "🕌 3D Pixar Style Q&A Comedy (Pak Ustadz)",
        "description": "Format viral animasi komedi tanya jawab agama gaya 3D kartun (mirip @pingpongsiompong). Menggabungkan karakter ekspresif dengan audio dialog lucu.",
        "category": "Comedy / 3D Cartoon",
        "recommended_model": "Wan 2.1 1.3B (Ekspresi) + Hedra/LivePortrait (Lip-Sync)",
        "resolution": "720x1280 (9:16)",
        "aspect_ratio": "9:16",
        "scenes": [
            {
                "scene_num": 1,
                "timecode": "00:00 - 00:04",
                "duration": "4s",
                "shot_type": "Over-The-Shoulder (Hook Pertanyaan)",
                "image_prompt": "3D Pixar animated Indonesian youth with funny confused expression wearing a sarung and peci, leaning forward holding a smartphone, asking a question inside a colorful warm mosque corridor. Vibrant 3D animation, stylized Disney Pixar render, subsurface scattering on skin, rich lighting.",
                "motion_prompt": "The character scratches head comically with one hand, eyebrows raising in disbelief, lips moving as if asking a bizarre question. Dynamic camera push.",
                "negative_prompt": "photorealistic, uncanny valley, ugly, distorted peci, bad hand anatomy.",
                "audio_sfx": "Voiceover: 'Pak Ustadz, boleh gak nikahin orang sekampung sekaligus?', playful quirky cartoon BGM.",
                "editing_notes": "Text sticker pop-up on screen with question highlighted."
            },
            {
                "scene_num": 2,
                "timecode": "00:04 - 00:09",
                "duration": "5s",
                "shot_type": "Close-Up (Reaksi & Jawaban Ustadz)",
                "image_prompt": "Kind, wise, and funny elderly Indonesian Ustadz in Pixar 3D style, white beard, wearing green koko shirt and white sorban, holding a microphone, smiling warmly with humorous sparkle in eyes.",
                "motion_prompt": "The Ustadz pauses, smiles knowingly, takes a deep breath and gestures calmly with hand explaining while holding back laughter.",
                "negative_prompt": "angry expression, bad teeth, blurry sorban, low polygon.",
                "audio_sfx": "Voiceover: 'Ya boleh aja Mas, asal sekampung itu isinya cuma 4 orang!', audience laughing track SFX.",
                "editing_notes": "Punchline timing, zoom in right as the word '4 orang' is uttered."
            },
            {
                "scene_num": 3,
                "timecode": "00:09 - 00:13",
                "duration": "4s",
                "shot_type": "Extreme Close-Up (Jaw-Drop Outro)",
                "image_prompt": "The young boy with wide open jaw, eyeballs popping out cartoonishly in comic shock, hands clutching cheeks, colorful background with floating question marks and funny sweat drops.",
                "motion_prompt": "Extreme comical reaction, head vibrating with funny shock, blinking rapidly in confusion.",
                "negative_prompt": "serious face, realistic skin, deformed hands.",
                "audio_sfx": "Classic cartoon boing sound effect, funny slide whistle downward, laughter fade.",
                "editing_notes": "Freeze frame on maximum shock with funny sound effect."
            }
        ]
    },
    "mahsyar_pov": {
        "id": "mahsyar_pov",
        "title": "⚡ Epic POV Interactive Storytelling (Padang Mahsyar)",
        "description": "Format viral storytelling POV dramatis dengan 60fps pacing cepat dan tombol pilihan interaktif (mirip @ctmverse). Menggunakan 3D Eevee/Wan 2.1 cinematic.",
        "category": "Cinematic / Drama",
        "recommended_model": "Wan 2.1 14B / Blender Eevee Engine + HyperFrames UI",
        "resolution": "1080x1920 (9:16)",
        "aspect_ratio": "9:16",
        "scenes": [
            {
                "scene_num": 1,
                "timecode": "00:00 - 00:06",
                "duration": "6s",
                "shot_type": "Extreme Wide Cinematic (The Gathering)",
                "image_prompt": "Endless barren scorched earth under a deep crimson sky with swirling dark storm clouds and celestial golden light beams breaking through. Countless silhouetted human figures walking solemnly towards the horizon. Cinematic unreal engine 5, volumetric fog, dramatic lighting, 8k masterpiece.",
                "motion_prompt": "Slow dramatic crane shot rising upwards. Heavy dust storm blowing across the desert floor. Celestial light rays shimmering and pulsating through thick clouds.",
                "negative_prompt": "modern buildings, green grass, peaceful sunny day, cartoon, blurry.",
                "audio_sfx": "Ominous deep drone bass, desert wind howling, distant ethereal choir chant.",
                "editing_notes": "Epic title card overlay: 'TIUPAN SANGKAKALA - EPISODE 4' with glowing gold particles."
            },
            {
                "scene_num": 2,
                "timecode": "00:06 - 00:12",
                "duration": "6s",
                "shot_type": "POV Close-Up (The Horn Shockwave)",
                "image_prompt": "First-person POV looking down at trembling hands covered in fine white dust, then looking up to see an immense golden celestial trumpet in the heavens vibrating with cosmic energy.",
                "motion_prompt": "Massive sonic shockwave ripples through the air, vibrating the camera lens violently with motion blur. Dust kicks up in circular waves.",
                "negative_prompt": "static, calm, clean hands, distorted fingers.",
                "audio_sfx": "Earth-shaking horn blast sound with massive sub-bass rumble, heartbeat thumping fast in ears.",
                "editing_notes": "Screen shake distortion effect. Glitch chromatic aberration."
            },
            {
                "scene_num": 3,
                "timecode": "00:12 - 00:18",
                "duration": "6s",
                "shot_type": "Interactive Choice Screen (HUD UI)",
                "image_prompt": "Two glowing portals in the desert storm: Left portal is surrounded by cool blue soothing light with tranquil mist; Right portal is surrounded by roaring intense golden fire. Dark cinematic background.",
                "motion_prompt": "Camera drifts slowly forward between both portals. Embers and blue sparks drifting in parallax.",
                "negative_prompt": "ugly UI, flat colors, low resolution.",
                "audio_sfx": "Dramatic countdown ticking sound 'TICK... TICK... TICK...', whispering voices.",
                "editing_notes": "HyperFrames interactive decision overlay: [PILIHAN A: Lari ke Telaga] vs [PILIHAN B: Cari Perlindungan]."
            }
        ]
    }
}
