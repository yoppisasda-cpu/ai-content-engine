document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const tabs = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const presetsContainer = document.getElementById("presets-container");
  
  const urlInput = document.getElementById("url-input");
  const btnAnalyzeUrl = document.getElementById("btn-analyze-url");
  const urlStatus = document.getElementById("url-status");

  const btnGenerateConcept = document.getElementById("btn-generate-concept");
  const customTitle = document.getElementById("custom-title");
  const customStyle = document.getElementById("custom-style");
  const customConcept = document.getElementById("custom-concept");
  const customModel = document.getElementById("custom-model");

  const outputSection = document.getElementById("output-section");
  const storyboardCategory = document.getElementById("storyboard-category");
  const storyboardTitle = document.getElementById("storyboard-title");
  const storyboardModel = document.getElementById("storyboard-model");
  const storyboardResolution = document.getElementById("storyboard-resolution");
  const storyboardScenesCount = document.getElementById("storyboard-scenes-count");
  const transcriptBanner = document.getElementById("transcript-banner");
  const transcriptText = document.getElementById("transcript-text");
  const scenesContainer = document.getElementById("scenes-container");

  const btnExportRunpod = document.getElementById("btn-export-runpod");
  const btnCopyAll = document.getElementById("btn-copy-all");
  const btnCopyWan2gpBatch = document.getElementById("btn-copy-wan2gp-batch");
  const toast = document.getElementById("toast");

  let currentStoryboard = null;

  // Tab switching
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      const target = document.getElementById(tab.dataset.tab);
      if (target) target.classList.add("active");
    });
  });

  // Load Presets
  async function loadPresets() {
    try {
      const res = await fetch("/api/presets");
      const presets = await res.json();
      renderPresets(presets);
    } catch (err) {
      presetsContainer.innerHTML = `<div class="status-box error">Gagal memuat preset: ${err.message}</div>`;
    }
  }

  function renderPresets(presets) {
    presetsContainer.innerHTML = "";
    presets.forEach(p => {
      const card = document.createElement("div");
      card.className = "preset-card";
      card.innerHTML = `
        <span class="preset-badge">${p.category}</span>
        <h3 class="preset-title">${p.title}</h3>
        <p class="preset-desc">${p.description}</p>
        <div class="preset-footer">
          <span class="preset-model">${p.recommended_model}</span>
          <span>${p.scenes.length} Adegan</span>
        </div>
      `;
      card.addEventListener("click", () => {
        loadStoryboard(p);
      });
      presetsContainer.appendChild(card);
    });
  }

  // Load Storyboard into UI
  function loadStoryboard(data) {
    currentStoryboard = data;
    outputSection.classList.remove("hidden");

    storyboardTitle.textContent = data.title || "Production Storyboard";
    storyboardCategory.textContent = data.category || "KONTEN AI";
    storyboardModel.textContent = `🎯 ${data.recommended_model || 'Wan 2.1'}`;
    storyboardResolution.textContent = `📐 ${data.resolution || '9:16'}`;
    storyboardScenesCount.textContent = `🎬 ${data.scenes ? data.scenes.length : 0} Adegan`;

    if (data.transcription && data.transcription.trim().length > 0) {
      transcriptBanner.classList.remove("hidden");
      transcriptText.textContent = `"${data.transcription}"`;
    } else {
      transcriptBanner.classList.add("hidden");
    }

    renderDialogue(data.dialogue, data.id);
    renderScenes(data.scenes || []);

    // Scroll smoothly to output
    outputSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderScenes(scenes) {
    scenesContainer.innerHTML = "";
    scenes.forEach(scene => {
      const card = document.createElement("div");
      card.className = "scene-card";

      const previewHtml = scene.frame_preview
        ? `<div class="scene-thumb-wrapper" style="position:relative;display:inline-block;width:100%;">
            <a href="${scene.frame_preview}" target="_blank" title="Klik untuk lihat ukuran penuh">
              <img class="scene-thumb" src="${scene.frame_preview}" alt="Frame Adegan ${scene.scene_num}" style="cursor:zoom-in;display:block;width:100%;border-radius:10px;" />
            </a>
            <a href="${scene.frame_preview}" download="scene_${scene.scene_num}_reference.jpg" class="btn-download-thumb" style="margin-top:6px;display:flex;align-items:center;justify-content:center;gap:5px;width:100%;padding:6px 8px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.18);border-radius:8px;color:#e2e8f0;font-size:11px;font-weight:600;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,242,254,0.2)';this.style.borderColor='#00f2fe';" onmouseout="this.style.background='rgba(255,255,255,0.08)';this.style.borderColor='rgba(255,255,255,0.18)';">
              💾 Unduh Gambar Ref
            </a>
          </div>`
        : `<div class="scene-thumb" style="display:flex;align-items:center;justify-content:center;color:#64748b;font-size:12px;">9:16 Ratio</div>`;

      card.innerHTML = `
        <div class="scene-sidebar">
          <div class="scene-number">ADEGAN #${scene.scene_num}</div>
          <div class="scene-timecode" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:4px 0;">
            <span style="font-size:12px;">⏱️ ${scene.timecode || ''}</span>
            <span style="background:rgba(0,242,254,0.18);color:#38bdf8;border:1px solid rgba(0,242,254,0.3);padding:1px 7px;border-radius:6px;font-size:11px;font-weight:700;">${scene.duration}</span>
          </div>
          <div class="scene-shot-type">${scene.shot_type || 'Shot'}</div>
          ${previewHtml}
        </div>
        <div class="scene-body">
          <!-- Image Prompt -->
          <div class="prompt-block">
            <div class="prompt-header">
              <span class="prompt-label cyan">🖼️ 1. Image Keyframe Prompt (Flux / Midjourney)</span>
              <button class="btn-copy" data-copy="${encodeURIComponent(scene.image_prompt || '')}">📋 Salin Image</button>
            </div>
            <div class="prompt-text">${escapeHtml(scene.image_prompt || '')}</div>
          </div>

          <!-- Motion Prompt for Wan2GP -->
          <div class="prompt-block">
            <div class="prompt-header">
              <span class="prompt-label purple">🎥 2. Wan2GP Motion Video Prompt</span>
              <button class="btn-copy" data-copy="${encodeURIComponent(scene.motion_prompt || '')}">📋 Salin Motion</button>
            </div>
            <div class="prompt-text">${escapeHtml(scene.motion_prompt || '')}</div>
          </div>

          <!-- Negative Prompt -->
          ${scene.negative_prompt ? `
          <div class="prompt-block" style="padding:10px 14px;">
            <div class="prompt-header">
              <span class="prompt-label" style="font-size:11px;">⚠️ Negative Prompt</span>
              <button class="btn-copy" style="padding:3px 8px;font-size:11px;" data-copy="${encodeURIComponent(scene.negative_prompt)}">📋 Salin</button>
            </div>
            <div class="prompt-text" style="font-size:11px;color:#94a3b8;">${escapeHtml(scene.negative_prompt)}</div>
          </div>
          ` : ''}

          <!-- Audio & Editing Meta -->
          <div class="scene-meta-grid">
            <div class="meta-block">
              <div class="meta-block-title">🎙️ Audio / Voiceover & SFX</div>
              <div class="meta-block-content">${escapeHtml(scene.audio_sfx || '-')}</div>
            </div>
            <div class="meta-block">
              <div class="meta-block-title">✂️ Pacing & Catatan Editing</div>
              <div class="meta-block-content">${escapeHtml(scene.editing_notes || '-')}</div>
            </div>
          </div>
        </div>
      `;
      scenesContainer.appendChild(card);
    });

    // Attach copy listeners
    document.querySelectorAll(".btn-copy").forEach(btn => {
      btn.addEventListener("click", () => {
        const textToCopy = decodeURIComponent(btn.dataset.copy);
        copyToClipboard(textToCopy);
      });
    });
  }

  // URL Analyzer Handler
  btnAnalyzeUrl.addEventListener("click", async () => {
    const url = urlInput.value.trim();
    if (!url) {
      alert("Silakan masukkan URL Instagram Reels, TikTok, atau YouTube Shorts.");
      return;
    }

    const detectionModeEl = document.getElementById("detection-mode");
    const maxDurationEl = document.getElementById("max-duration");
    const numSpeakersEl = document.getElementById("num-speakers");
    const detection_mode = detectionModeEl ? detectionModeEl.value : "smart";
    const max_scene_duration = maxDurationEl ? parseFloat(maxDurationEl.value) : 5.0;
    const num_speakers = numSpeakersEl ? parseInt(numSpeakersEl.value) : 0;
    const forceEl = document.getElementById("force-refresh");
    const force_refresh = forceEl ? forceEl.checked : false;

    urlStatus.classList.remove("hidden", "error");
    urlStatus.classList.add("loading");
    urlStatus.innerHTML = `⏳ <strong>Sedang Memproses...</strong><br>1. Mengunduh video dengan yt-dlp...<br>2. Transkripsi suara dengan Whisper AI...<br>3. Mendeteksi perpindahan kamera secara presisi (${detection_mode})...<br>4. Membedah percakapan & identifikasi pembicara...<br>5. Mengekstrak keyframe per adegan dengan FFmpeg...`;
    btnAnalyzeUrl.disabled = true;

    try {
      const res = await fetch("/api/analyze-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, detection_mode, max_scene_duration, num_speakers, force_refresh })
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.detail || "Gagal memproses video.");
      }

      urlStatus.classList.remove("loading");
      const summaryText = data.data.detection_summary || `Berhasil dibedah menjadi ${data.data.scenes.length} adegan presisi.`;
      urlStatus.innerHTML = data.cached
        ? `💾 <strong>Dimuat dari hasil tersimpan</strong> (${data.data.saved_at || ''}). ${summaryText}<br><small>Centang "Paksa analisis ulang" jika ingin memproses ulang.</small>`
        : `✅ <strong>Selesai & tersimpan!</strong> ${summaryText}`;
      loadStoryboard(data.data);
      loadHistory();
    } catch (err) {
      urlStatus.classList.remove("loading");
      urlStatus.classList.add("error");
      urlStatus.innerHTML = `❌ <strong>Error:</strong> ${err.message}`;
    } finally {
      btnAnalyzeUrl.disabled = false;
    }
  });

  // Saved history
  const historyList = document.getElementById("history-list");
  const modeLabels = { smart: "Presisi Cerdas", visual_cut: "Visual Cut", speech_beat: "Speech Beat", fixed: "Fixed" };

  const speakerColors = {
    "A": { bg: "rgba(0, 242, 254, 0.15)", border: "rgba(0, 242, 254, 0.4)", text: "#38bdf8" },
    "B": { bg: "rgba(16, 185, 129, 0.15)", border: "rgba(16, 185, 129, 0.4)", text: "#34d399" },
    "C": { bg: "rgba(168, 85, 247, 0.15)", border: "rgba(168, 85, 247, 0.4)", text: "#c084fc" },
    "D": { bg: "rgba(245, 158, 11, 0.15)", border: "rgba(245, 158, 11, 0.4)", text: "#fbbf24" }
  };

  function renderDialogue(dialogue, sbId) {
    const dialogueSection = document.getElementById("dialogue-section");
    const speakersTags = document.getElementById("speakers-tags");
    const linesContainer = document.getElementById("dialogue-lines-container");
    if (!dialogueSection) return;

    if (!dialogue || !dialogue.lines || dialogue.lines.length === 0) {
      dialogueSection.classList.add("hidden");
      return;
    }
    dialogueSection.classList.remove("hidden");

    // Sync dropdown with current requested speaker count
    const reDiarizeEl = document.getElementById("re-diarize-speakers");
    if (reDiarizeEl && dialogue.num_speakers_requested !== undefined) {
      reDiarizeEl.value = String(dialogue.num_speakers_requested);
    }

    // Render Speaker summary chips
    speakersTags.innerHTML = "";
    (dialogue.speakers || []).forEach(spk => {
      const col = speakerColors[spk.label] || speakerColors["A"];
      const tag = document.createElement("div");
      tag.style.cssText = `display:flex;align-items:center;gap:6px;background:${col.bg};border:1px solid ${col.border};padding:4px 10px;border-radius:20px;font-size:12px;color:${col.text};cursor:pointer;`;
      tag.title = "Klik untuk ganti nama karakter";
      tag.innerHTML = `<strong>${escapeHtml(spk.name || spk.label)}</strong> <span style="opacity:0.75;font-size:11px;">(${spk.line_count} baris · ${spk.talk_time}s) ✏️</span>`;
      tag.addEventListener("click", async () => {
        const newName = prompt(`Ubah nama untuk ${spk.label}:`, spk.name || spk.label);
        if (newName && newName.trim() && sbId) {
          const names = {};
          dialogue.speakers.forEach(s => names[s.label] = s.name);
          names[spk.label] = newName.trim();
          const r = await fetch(`/api/storyboards/${sbId}/dialogue`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ speaker_names: names })
          });
          const resData = await r.json();
          if (resData.success) {
            currentStoryboard = resData.data;
            renderDialogue(resData.data.dialogue, sbId);
            showToast("Nama karakter berhasil disimpan!");
          }
        }
      });
      speakersTags.appendChild(tag);
    });

    // Render lines
    linesContainer.innerHTML = "";
    dialogue.lines.forEach((line) => {
      const col = speakerColors[line.speaker] || speakerColors["A"];
      const spkObj = (dialogue.speakers || []).find(s => s.label === line.speaker);
      const spkName = spkObj ? spkObj.name : `Speaker ${line.speaker}`;

      const row = document.createElement("div");
      row.style.cssText = "display:flex;align-items:flex-start;gap:10px;padding:8px 10px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:8px;font-size:13px;";
      row.innerHTML = `
        <span style="font-size:11px;font-family:monospace;color:#64748b;white-space:nowrap;margin-top:2px;">⏱️ ${line.start}s - ${line.end}s</span>
        <span style="background:${col.bg};color:${col.text};border:1px solid ${col.border};padding:2px 8px;border-radius:6px;font-size:11px;font-weight:700;white-space:nowrap;">${escapeHtml(spkName)}</span>
        <span style="flex:1;color:#e2e8f0;line-height:1.4;">${escapeHtml(line.text)}</span>
        <button class="btn-copy" style="padding:2px 7px;font-size:11px;" data-copy="${encodeURIComponent(line.text)}">📋 Salin</button>
      `;
      row.querySelector(".btn-copy").addEventListener("click", () => {
        copyToClipboard(line.text);
      });
      linesContainer.appendChild(row);
    });

    // Re-diarize button handler
    const btnReDiarize = document.getElementById("btn-re-diarize");
    if (btnReDiarize && sbId) {
      btnReDiarize.onclick = async () => {
        const num = parseInt(document.getElementById("re-diarize-speakers").value) || 0;
        btnReDiarize.disabled = true;
        btnReDiarize.textContent = "⏳ Memproses...";
        try {
          const r = await fetch(`/api/storyboards/${sbId}/dialogue`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ num_speakers: num })
          });
          const resData = await r.json();
          if (resData.success) {
            currentStoryboard = resData.data;
            renderDialogue(resData.data.dialogue, sbId);
            showToast("Percakapan berhasil dianalisis ulang!");
          }
        } catch (e) {
          alert("Gagal memproses ulang percakapan: " + e.message);
        } finally {
          btnReDiarize.disabled = false;
          btnReDiarize.textContent = "🔄 Proses Ulang";
        }
      };
    }

    // Copy full dialogue
    const btnCopyDiag = document.getElementById("btn-copy-dialogue");
    if (btnCopyDiag) {
      btnCopyDiag.onclick = () => {
        let text = "";
        dialogue.lines.forEach(l => {
          const spkObj = (dialogue.speakers || []).find(s => s.label === l.speaker);
          const spkName = spkObj ? spkObj.name : `Speaker ${l.speaker}`;
          text += `[${l.start}s - ${l.end}s] ${spkName}: "${l.text}"\n`;
        });
        copyToClipboard(text);
      };
    }

    // Download SRT
    const btnDownloadSrt = document.getElementById("btn-download-srt");
    if (btnDownloadSrt) {
      btnDownloadSrt.onclick = () => {
        function toSrtTime(sec) {
          const hrs = Math.floor(sec / 3600);
          const mins = Math.floor((sec % 3600) / 60);
          const secs = Math.floor(sec % 60);
          const millis = Math.floor((sec % 1) * 1000);
          return `${String(hrs).padStart(2,'0')}:${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')},${String(millis).padStart(3,'0')}`;
        }
        let srt = "";
        dialogue.lines.forEach((l, i) => {
          const spkObj = (dialogue.speakers || []).find(s => s.label === l.speaker);
          const spkName = spkObj ? spkObj.name : `Speaker ${l.speaker}`;
          srt += `${i + 1}\n${toSrtTime(l.start)} --> ${toSrtTime(l.end)}\n[${spkName}] ${l.text}\n\n`;
        });
        const blob = new Blob([srt], { type: "text/plain;charset=utf-8" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `dialogue_${sbId || "script"}.srt`;
        a.click();
      };
    }
  }

  async function loadHistory() {
    if (!historyList) return;
    try {
      const res = await fetch("/api/storyboards");
      const items = await res.json();
      if (!items.length) {
        historyList.innerHTML = `<div style="color:#64748b;font-size:13px;">Belum ada hasil tersimpan.</div>`;
        return;
      }
      historyList.innerHTML = "";
      items.forEach(it => {
        const el = document.createElement("div");
        el.style.cssText = "display:flex;gap:10px;padding:10px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;cursor:pointer;transition:border-color .2s;";
        el.onmouseenter = () => el.style.borderColor = "rgba(0,242,254,0.5)";
        el.onmouseleave = () => el.style.borderColor = "rgba(255,255,255,0.08)";
        el.innerHTML = `
          ${it.thumbnail ? `<img src="${it.thumbnail}" style="width:48px;height:85px;object-fit:cover;border-radius:6px;flex-shrink:0;" />` : ""}
          <div style="flex:1;min-width:0;font-size:12px;color:#94a3b8;">
            <div style="color:#e2e8f0;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${escapeHtml(it.source_url)}">${escapeHtml(it.source_url || it.title)}</div>
            <div style="margin-top:4px;">🎬 ${it.scene_count} adegan · ⏱️ ${it.duration}</div>
            <div>🎯 ${modeLabels[it.detection_mode] || it.detection_mode} · maks ${it.max_scene_duration || "∞"}s</div>
            <div style="color:#64748b;">💾 ${it.saved_at}</div>
          </div>
          <button class="btn-copy" data-del="${it.id}" title="Hapus" style="align-self:flex-start;">🗑️</button>
        `;
        el.addEventListener("click", async (e) => {
          if (e.target.closest("[data-del]")) return;
          const r = await fetch(`/api/storyboards/${it.id}`);
          const d = await r.json();
          if (d.success) {
            urlStatus.classList.remove("hidden", "error", "loading");
            urlStatus.innerHTML = `💾 <strong>Dimuat dari riwayat:</strong> ${escapeHtml(it.source_url)}`;
            loadStoryboard(d.data);
          }
        });
        el.querySelector("[data-del]").addEventListener("click", async (e) => {
          e.stopPropagation();
          if (!confirm("Hapus hasil bedah video ini?")) return;
          await fetch(`/api/storyboards/${it.id}`, { method: "DELETE" });
          loadHistory();
        });
        historyList.appendChild(el);
      });
    } catch (err) {
      historyList.innerHTML = `<div style="color:#f87171;font-size:13px;">Gagal memuat riwayat: ${err.message}</div>`;
    }
  }

  const btnRefreshHistory = document.getElementById("btn-refresh-history");
  if (btnRefreshHistory) btnRefreshHistory.addEventListener("click", loadHistory);
  loadHistory();

  // Custom Idea Generator Handler
  btnGenerateConcept.addEventListener("click", async () => {
    const title = customTitle.value.trim();
    const concept = customConcept.value.trim();
    const style = customStyle.value;
    const model = customModel.value;

    if (!concept) {
      alert("Silakan isi konsep atau ide ceritanya terlebih dahulu.");
      return;
    }

    btnGenerateConcept.disabled = true;
    btnGenerateConcept.textContent = "Sedang menyusun...";

    try {
      const res = await fetch("/api/generate-concept", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title || "Ide Konten Baru",
          concept,
          style,
          model_target: model
        })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.detail || "Gagal membuat storyboard.");
      }
      loadStoryboard(data.data);
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      btnGenerateConcept.disabled = false;
      btnGenerateConcept.textContent = "⚡ Susun Master Storyboard";
    }
  });

  // Export RunPod Package Handler
  btnExportRunpod.addEventListener("click", async () => {
    if (!currentStoryboard) return;

    btnExportRunpod.disabled = true;
    btnExportRunpod.textContent = "Menyiapkan Package...";

    try {
      const res = await fetch("/api/export-batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          storyboard: currentStoryboard,
          package_name: "runpod_batch"
        })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.detail || "Gagal export package.");
      }

      // Trigger download
      const a = document.createElement("a");
      a.href = data.download_url;
      a.download = data.data.zip_filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      showToast(`📦 Package RunPod (${data.data.total_jobs} adegan) berhasil didownload!`);
    } catch (err) {
      alert(`Export error: ${err.message}`);
    } finally {
      btnExportRunpod.disabled = false;
      btnExportRunpod.textContent = "📦 Export RunPod Batch (.zip)";
    }
  });

  // Download ComfyUI Workflow Handler
  const btnExportComfyui = document.getElementById("btn-export-comfyui");
  if (btnExportComfyui) {
    btnExportComfyui.addEventListener("click", () => {
      const a = document.createElement("a");
      a.href = "/workflows/official_wan_14b_i2v.json";
      a.download = "comfyui_wan_14b_i2v_workflow.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast("🎛️ ComfyUI Workflow Wan 14B I2V berhasil diunduh! Siap di-drag & drop ke ComfyUI.");
    });
  }

  // Copy All Storyboard as Markdown
  btnCopyAll.addEventListener("click", () => {
    if (!currentStoryboard) return;

    let md = `# 🎬 ${currentStoryboard.title}\n`;
    md += `Target Engine: ${currentStoryboard.recommended_model || 'Wan 2.1'}\n\n`;

    if (currentStoryboard.transcription) {
      md += `### 🎙️ Transkrip Suara:\n"${currentStoryboard.transcription}"\n\n`;
    }

    md += `## 📋 DAFTAR ADEGAN & PROMPT:\n\n`;
    (currentStoryboard.scenes || []).forEach(s => {
      md += `### Adegan ${s.scene_num}: ${s.shot_type} (${s.timecode || s.duration})\n`;
      md += `**Image Prompt (Flux/Midjourney):**\n\`${s.image_prompt}\`\n\n`;
      md += `**Wan2GP Motion Prompt:**\n\`${s.motion_prompt}\`\n\n`;
      if (s.negative_prompt) {
        md += `**Negative Prompt:**\n\`${s.negative_prompt}\`\n\n`;
      }
      md += `**Audio/SFX:** ${s.audio_sfx}\n`;
      md += `**Editing Notes:** ${s.editing_notes}\n\n---\n\n`;
    });

    copyToClipboard(md);
    showToast("Seluruh Storyboard disalin sebagai Markdown!");
  });

  // Copy All Wan2GP Motion Prompts as Batch (separated by empty lines)
  if (btnCopyWan2gpBatch) {
    btnCopyWan2gpBatch.addEventListener("click", () => {
      if (!currentStoryboard || !currentStoryboard.scenes || currentStoryboard.scenes.length === 0) return;

      // Extract each motion prompt and join with double newlines (empty line separator)
      const batchPrompts = currentStoryboard.scenes
        .map(s => (s.motion_prompt || "").trim())
        .filter(p => p.length > 0)
        .join("\n\n");

      copyToClipboard(batchPrompts);
      showToast(`⚡ ${currentStoryboard.scenes.length} Motion Prompt disalin siap paste ke Wan2GP!`);
    });
  }

  // Utility: Clipboard
  function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        showToast("Prompt berhasil disalin ke clipboard!");
      });
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      showToast("Prompt berhasil disalin ke clipboard!");
    }
  }

  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.remove("hidden");
    setTimeout(() => {
      toast.classList.add("hidden");
    }, 2800);
  }

  function escapeHtml(string) {
    return String(string)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Initial load
  loadPresets();
});
