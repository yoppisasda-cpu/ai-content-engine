"""
Dialogue Analyzer
Speaker diarization (who speaks when) via sherpa-onnx (pyannote-segmentation-3.0 ONNX + WeSpeaker
embedding), merged with Whisper sentences into a per-line dialogue script for TTS / lip-sync.

sherpa-onnx is used instead of pyannote.audio / speechbrain because those are incompatible with
torchaudio 2.10 in the Wan2GP environment. This runs on ONNX Runtime and needs no HF token.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "diarization"
SEG_MODEL = MODELS_DIR / "sherpa-onnx-pyannote-segmentation-3-0" / "model.onnx"
EMB_MODEL = MODELS_DIR / "embedding.onnx"

SPEAKER_LABELS = "ABCDEFGHIJ"


class DialogueAnalyzer:
    def __init__(self):
        self._sd = None
        self._sd_key = None

    def models_available(self) -> bool:
        return SEG_MODEL.exists() and EMB_MODEL.exists()

    def _get_diarizer(self, num_speakers: int, threshold: float):
        import sherpa_onnx
        key = (num_speakers, threshold)
        if self._sd is not None and self._sd_key == key:
            return self._sd

        config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
            segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
                pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(model=str(SEG_MODEL)),
            ),
            embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(EMB_MODEL)),
            clustering=sherpa_onnx.FastClusteringConfig(
                num_clusters=num_speakers if num_speakers > 0 else -1,
                threshold=threshold,
            ),
            min_duration_on=0.2,
            min_duration_off=0.4,
        )
        if not config.validate():
            raise RuntimeError("Konfigurasi diarization tidak valid. Cek file model di models/diarization.")
        self._sd = sherpa_onnx.OfflineSpeakerDiarization(config)
        self._sd_key = key
        return self._sd

    def diarize(self, wav_path: str, num_speakers: int = 0, threshold: float = 0.6) -> List[Dict[str, Any]]:
        """Return list of {start, end, speaker} turns. num_speakers=0 means auto-detect."""
        import numpy as np
        import soundfile as sf

        audio, sr = sf.read(wav_path, dtype="float32", always_2d=True)
        audio = audio.mean(axis=1)
        sd = self._get_diarizer(num_speakers, threshold)
        if sr != sd.sample_rate:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=sd.sample_rate)
        result = sd.process(np.ascontiguousarray(audio)).sort_by_start_time()
        return [{"start": float(r.start), "end": float(r.end), "speaker": int(r.speaker)} for r in result]

    @staticmethod
    def _speaker_for(seg_start: float, seg_end: float, turns: List[Dict[str, Any]]) -> Optional[int]:
        overlap: Dict[int, float] = {}
        for t in turns:
            ov = min(seg_end, t["end"]) - max(seg_start, t["start"])
            if ov > 0:
                overlap[t["speaker"]] = overlap.get(t["speaker"], 0.0) + ov
        if overlap:
            return max(overlap, key=overlap.get)
        # No overlap: take nearest turn
        if not turns:
            return None
        mid = (seg_start + seg_end) / 2
        return min(turns, key=lambda t: min(abs(mid - t["start"]), abs(mid - t["end"])))["speaker"]

    def build_script(self, whisper_segments: List[Dict[str, Any]], turns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge Whisper sentences with diarization turns into a dialogue script."""
        # Relabel speakers in order of first appearance -> A, B, C ...
        order: Dict[int, str] = {}
        lines = []
        for seg in whisper_segments:
            text = (seg.get("text") or "").strip()
            if not text:
                continue
            st, et = float(seg.get("start", 0)), float(seg.get("end", 0))
            spk = self._speaker_for(st, et, turns)
            if spk is None:
                label = "A"
            else:
                if spk not in order:
                    order[spk] = SPEAKER_LABELS[len(order) % len(SPEAKER_LABELS)]
                label = order[spk]
            lines.append({
                "start": round(st, 2),
                "end": round(et, 2),
                "duration": round(et - st, 2),
                "speaker": label,
                "text": text,
            })

        speakers = {}
        for ln in lines:
            s = speakers.setdefault(ln["speaker"], {"label": ln["speaker"], "name": f"Speaker {ln['speaker']}",
                                                     "line_count": 0, "talk_time": 0.0})
            s["line_count"] += 1
            s["talk_time"] = round(s["talk_time"] + ln["duration"], 2)

        return {"speakers": list(speakers.values()), "lines": lines}

    def analyze(self, wav_path: str, whisper_segments: List[Dict[str, Any]], num_speakers: int = 0) -> Dict[str, Any]:
        if not self.models_available():
            raise RuntimeError("Model diarization belum ada di models/diarization.")
        turns = self.diarize(wav_path, num_speakers=num_speakers)
        script = self.build_script(whisper_segments, turns)
        script["num_speakers_requested"] = num_speakers
        return script
