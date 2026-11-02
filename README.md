# 🎬 AI Content Material Engine (Pabrik Materi Video AI)

Engine khusus untuk memproduksi **materi, dekonstruksi video viral, dan master prompt** untuk di-generate ke dalam model video AI seperti **Wan2GP (Lokal)** dan **Wan 2.1 / 2.2 14B (RunPod Cloud)**.

---

## 🚀 Fitur Utama
1. **⚡ Preset Format Viral Siap Pakai**:
   - **Cute Toddler ASMR Mukbang**: 100% mulus di Wan 2.1 1.3B lokal (RTX 3070 8GB).
   - **3 Cat Chefs Making Strawberry Daifuku**: Animasi memasak kucing antropomorfik.
   - **3D Pixar Style Q&A Comedy (Pak Ustadz)**: Gaya kartun dialog ala @pingpongsiompong.
   - **Epic POV Interactive Storytelling (Padang Mahsyar)**: Gaya sinematik 60fps ala @ctmverse.
2. **🔍 Bedah Video URL Otomatis**:
   - Masukkan link Instagram Reels / TikTok / YouTube Shorts.
   - Otomatis download via `yt-dlp`.
   - Transkripsi suara + timecode dengan `Whisper AI`.
   - Ekstraksi keyframe visual dengan `FFmpeg`.
   - Menghasilkan tabel prompt per adegan yang siap dipakai.
3. **💡 Generator Ide / Script Baru**:
   - Tuliskan ide atau sinopsis singkat, engine akan menyusun 3 adegan terstruktur (Hook, Core Action, Outro).
4. **📋 1-Click Copy**:
   - Salin Image Prompt (Flux / Midjourney) per adegan.
   - Salin Wan2GP Motion Prompt per adegan.
   - Salin Negative Prompt.
5. **📦 Export Batch Package (RunPod)**:
   - Export 1-klik menjadi file `.zip` berisi `batch_jobs.json` dan `run_batch_runpod.py` untuk generate massal di cloud (RTX 4090 / A100).

---

## 🛠️ Cara Menjalankan Engine

Server engine berjalan di port **8500**:
```powershell
cd "d:\app daddy\ANTIGRAVITY\AI-Content-Engine"
& "D:\wan2GP\env_uv\Scripts\python.exe" -m uvicorn server:app --host 0.0.0.0 --port 8500
```
Buka di browser:
👉 **[http://localhost:8500](http://localhost:8500)**

---

## 🔗 Integrasi dengan Wan2GP Lokal
- Buka Wan2GP Desktop Launcher di browser: **[http://localhost:7861](http://localhost:7861)**
- Pilih scene dari dashboard AI Content Engine, klik tombol **[📋 Salin Image]** dan **[📋 Salin Motion]**, lalu paste langsung ke Wan2GP!
