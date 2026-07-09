#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ElevenLabs TTS 26 字母生成 - GitHub Actions 版
===============================================

环境变量：
    ELEVENLABS_API_KEY  - 必填，GitHub Secret 配置
"""

import os
import requests
from pathlib import Path

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# 8 个最匹配"播音员/主持人"风格的高音质音色
VOICES = [
    ("Daniel", "onwK4e9ZLuTAKqWW03F9", "letter_11labs_daniel"),    # ⭐⭐⭐⭐⭐ 新闻播音员
    ("Adam",   "pNInz6obpgDQGcFmaJgB", "letter_11labs_adam"),      # ⭐⭐⭐⭐⭐ 权威男声
    ("Brian",  "nPczCjzI2devNBz1zQrb", "letter_11labs_brian"),     # ⭐⭐⭐⭐  深沉共鸣
    ("Chris",  "iP95p4xoKVk53GoZ742B", "letter_11labs_chris"),      # ⭐⭐⭐⭐  迷人男声
    ("Alice",  "Xb7hH8MSUJpSbSDYk0k2", "letter_11labs_alice"),     # ⭐⭐⭐⭐  清晰教育
    ("George", "JBFqnCBsd6RMkjVDRZzb", "letter_11labs_george"),    # ⭐⭐⭐⭐  温暖讲述者
    ("Roger",  "CwhRBWXzGAHq8TQ4Fs17", "letter_11labs_roger"),     # ⭐⭐⭐⭐  沉稳自然
    ("Lily",   "pFZP5JQG7iQjIQuC4Bku", "letter_11labs_lily"),      # ⭐⭐⭐⭐  天鹅绒女声
]

OUT_BASE = "output"


def elevenlabs_tts(voice_id: str, text: str, api_key: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/wav",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.35,
            "similarity_boost": 0.75,
        },
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    if len(r.content) < 1000:
        raise RuntimeError(f"Small audio ({len(r.content)} bytes)")
    return r.content


def main() -> None:
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise SystemExit("ERROR: ELEVENLABS_API_KEY env var not set")

    print("=" * 60)
    print("ElevenLabs TTS - 26 字母 × 8 顶级音色")
    print(f"  Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"  Voices: {[v for v, _, _ in VOICES]}")
    print(f"  Total: {len(LETTERS) * len(VOICES)} wav")
    print("=" * 60)

    total_ok = total_fail = 0
    for sname, vid, dir_name in VOICES:
        out_dir = os.path.join(OUT_BASE, dir_name)
        os.makedirs(out_dir, exist_ok=True)
        print(f"\n=== {sname} -> {out_dir}/ ===")
        ok = fail = 0
        for i, c in enumerate(LETTERS, 1):
            out_path = os.path.join(out_dir, f"letter_{c}.wav")
            try:
                audio = elevenlabs_tts(vid, c, api_key)
                with open(out_path, "wb") as f:
                    f.write(audio)
                ok += 1
                total_ok += 1
                print(f"  [{i:>2}/{len(LETTERS)}] OK   {c}", flush=True)
            except Exception as e:  # noqa: BLE001
                fail += 1
                total_fail += 1
                print(f"  [{i:>2}/{len(LETTERS)}] FAIL {c}: {e}", flush=True)
        print(f"  {sname} 完成: {ok} 成功 / {fail} 失败")

    print("\n" + "=" * 60)
    print(f"全部完成：{total_ok} 成功 / {total_fail} 失败")
    print(f"输出目录：{OUT_BASE}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure TTS 26 字母生成 - GitHub Actions 版
===========================================

跑 6 个顶级 Azure Neural Voice（与 Edge TTS 同款引擎，输出 24kHz WAV）：

  Christopher  ⭐⭐⭐⭐⭐ 新闻男主播
  Jenny        ⭐⭐⭐⭐⭐ 专业女声
  Guy          ⭐⭐⭐⭐   沉稳男声
  Libby        ⭐⭐⭐⭐   英式女声
  Aria         ⭐⭐⭐⭐   清晰女声
  Andrew       ⭐⭐⭐⭐   播音男声

输出 wav 到 ./output/letter_azure_<voice>/letter_<X>.wav，
最后通过 upload-artifact 打包下载到本地。

环境变量：
    AZURE_TTS_KEY  - 必填，GitHub Secret 配置
"""

import os
import requests

# ============================ CONFIG ============================
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

VOICES = [
    ("Christopher", "en-US-ChristopherNeural", "letter_azure_christopher"),
    ("Jenny",       "en-US-JennyNeural",        "letter_azure_jenny"),
    ("Guy",         "en-US-GuyNeural",          "letter_azure_guy"),
    ("Libby",       "en-US-LibbyNeural",        "letter_azure_libby"),
    ("Aria",        "en-US-AriaNeural",         "letter_azure_aria"),
    ("Andrew",      "en-US-AndrewNeural",       "letter_azure_andrew"),
]

OUT_BASE = "output"
FORMAT = "riff-24khz-16bit-mono-pcm"  # 24kHz WAV

# 常见 Azure region，自动探测可用 region
REGIONS = [
    "eastasia", "southeastasia", "eastus", "eastus2",
    "westus", "westus2", "northeurope", "westeurope",
    "chinanorth2", "chinaeast2",
]
# =================================================================


def _find_region(key: str) -> tuple[str | None, str | None]:
    """遍历 regions，找到可用的 Azure Speech endpoint"""
    for region in REGIONS:
        url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
        ssml = "<speak version='1.0' xml:lang='en-US'><voice name='en-US-JennyNeural'>A</voice></speak>"
        headers = {
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": FORMAT,
        }
        try:
            r = requests.post(url, headers=headers, data=ssml.encode("utf-8"), timeout=10)
            if r.status_code == 200 and len(r.content) > 500:
                print(f"  Region OK: {region}")
                return region, url
        except Exception:
            pass
    return None, None


def azure_tts(letter: str, voice_name: str, region_url: str, key: str) -> bytes:
    ssml = f"<speak version='1.0' xml:lang='en-US'><voice name='{voice_name}'>{letter}</voice></speak>"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": FORMAT,
    }
    r = requests.post(region_url, headers=headers, data=ssml.encode("utf-8"), timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    if len(r.content) < 500:
        raise RuntimeError(f"Empty audio ({len(r.content)} bytes)")
    return r.content


def main() -> None:
    key = os.environ.get("AZURE_TTS_KEY", "")
    if not key:
        raise SystemExit("ERROR: AZURE_TTS_KEY env var not set")

    print("=" * 60)
    print("Azure TTS - 26 字母 × 6 顶级 Neural Voice")
    print(f"  Key: {key[:8]}...{key[-4:]}")
    print(f"  Voices: {[v for v, _, _ in VOICES]}")
    print(f"  Total: {len(LETTERS) * len(VOICES)} wav")
    print("=" * 60)

    print("\n[*] Detecting Azure region...")
    region, region_url = _find_region(key)
    if not region:
        raise SystemExit("ERROR: No working Azure region found. Check your AZURE_TTS_KEY and network.")
    print(f"    Using region: {region}")

    total_ok = total_fail = 0
    for sname, vname, dir_name in VOICES:
        out_dir = os.path.join(OUT_BASE, dir_name)
        os.makedirs(out_dir, exist_ok=True)
        print(f"\n=== {sname} ({vname}) -> {out_dir}/ ===")
        ok = fail = 0
        for i, c in enumerate(LETTERS, 1):
            out_path = os.path.join(out_dir, f"letter_{c}.wav")
            try:
                audio = azure_tts(c, vname, region_url, key)
                with open(out_path, "wb") as f:
                    f.write(audio)
                ok += 1
                total_ok += 1
                print(f"  [{i:>2}/{len(LETTERS)}] OK   {c}", flush=True)
            except Exception as e:  # noqa: BLE001
                fail += 1
                total_fail += 1
                print(f"  [{i:>2}/{len(LETTERS)}] FAIL {c}: {e}", flush=True)
        print(f"  {sname} 完成: {ok} 成功 / {fail} 失败")

    print("\n" + "=" * 60)
    print(f"全部完成：{total_ok} 成功 / {total_fail} 失败")
    print(f"输出目录：{OUT_BASE}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI TTS 26 字母生成 - GitHub Actions 版
==========================================

跑 6 个顶级音色（按播音员专业度排序）：
  onyx    ⭐⭐⭐⭐⭐ 新闻男主播（CNN/BBC）
  nova    ⭐⭐⭐⭐⭐ 专业女播（NBC）
  fable   ⭐⭐⭐⭐   英式播音
  echo    ⭐⭐⭐⭐   温和男声
  shimmer ⭐⭐⭐    柔和女声
  alloy   ⭐⭐⭐    中性标准

输出 wav 到 ./output/letter_openai_<voice>/letter_<X>.wav，
最后通过 upload-artifact 打包下载到本地。

环境变量：
    OPENAI_API_KEY  - 必填，GitHub Secret 配置
"""

import os
import io

import numpy as np
import requests
import soundfile as sf
from scipy.signal import resample

# ============================ CONFIG ============================
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# 顶级音色（6 个），按播音员专业度排序
VOICES = [
    ("onyx",    "letter_openai_onyx"),      # ⭐⭐⭐⭐⭐ 新闻男主播
    ("nova",    "letter_openai_nova"),      # ⭐⭐⭐⭐⭐ 专业女播
    ("fable",   "letter_openai_fable"),     # ⭐⭐⭐⭐   英式播音
    ("echo",    "letter_openai_echo"),      # ⭐⭐⭐⭐   温和男声
    ("shimmer", "letter_openai_shimmer"),   # ⭐⭐⭐    柔和女声
    ("alloy",   "letter_openai_alloy"),     # ⭐⭐⭐    中性标准
]

OUT_BASE = "output"
MODEL = "tts-1-hd"
TARGET_SR = 44100
PAD_SEC = 0.04
THRESHOLD = 0.01
# =================================================================


def openai_tts(text: str, voice: str, api_key: str) -> bytes:
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "voice": voice,
        "input": text,
        "response_format": "wav",
        "speed": 1.0,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    if len(r.content) < 100:
        raise RuntimeError(f"Empty audio ({len(r.content)} bytes)")
    return r.content


def wav_to_44100(audio_bytes: bytes, out_path: str) -> None:
    data, sr = sf.read(io.BytesIO(audio_bytes), dtype="int16", always_2d=False)
    if data.ndim > 1:
        data = data.mean(axis=1).astype(np.int16)
    if sr != TARGET_SR:
        n_out = int(len(data) * TARGET_SR / sr)
        pf = data.astype(np.float32) / 32768.0
        data = np.clip(resample(pf, n_out) * 32768.0, -32768, 32767).astype(np.int16)
        sr = TARGET_SR
    sf.write(out_path, data, sr, format="WAV", subtype="PCM_16")


def trim_wav(path: str) -> None:
    data, sr = sf.read(path, dtype="int16", always_2d=False)
    n = data.shape[0]
    dataf = data.astype(np.float32) / (float(np.iinfo(np.int16).max) + 1.0)
    energy = np.abs(dataf)
    above = energy > THRESHOLD
    if not above.any():
        return
    first = int(np.argmax(above))
    last = int(len(above) - 1 - np.argmax(above[::-1]))
    pad = int(PAD_SEC * sr)
    start = max(0, first - pad)
    end = min(n, last + 1 + pad)
    trimmed = data[start:end]
    tmp = path + ".tmp.wav"
    try:
        sf.write(tmp, trimmed, sr, subtype="PCM_16")
        os.replace(tmp, path)
    except Exception as e:  # noqa: BLE001
        if os.path.exists(tmp):
            os.remove(tmp)
        print(f"      [trim error] {os.path.basename(path)}: {e}")


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise SystemExit("ERROR: OPENAI_API_KEY env var not set")

    print("=" * 60)
    print("OpenAI TTS - 26 字母 × 6 顶级音色")
    print(f"  Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"  Model: {MODEL}")
    print(f"  Voices: {[v for v, _ in VOICES]}")
    print(f"  Total: {len(LETTERS) * len(VOICES)} wav")
    print("=" * 60)

    total_ok = 0
    total_fail = 0
    for voice, dir_name in VOICES:
        out_dir = os.path.join(OUT_BASE, dir_name)
        os.makedirs(out_dir, exist_ok=True)
        print(f"\n=== {voice} -> {out_dir}/ ===")
        ok = fail = 0
        for i, c in enumerate(LETTERS, 1):
            out_path = os.path.join(out_dir, f"letter_{c}.wav")
            try:
                audio = openai_tts(c, voice, api_key)
                wav_to_44100(audio, out_path)
                trim_wav(out_path)
                ok += 1
                total_ok += 1
                print(f"  [{i:>2}/{len(LETTERS)}] OK   {c}", flush=True)
            except Exception as e:  # noqa: BLE001
                fail += 1
                total_fail += 1
                print(f"  [{i:>2}/{len(LETTERS)}] FAIL {c}: {e}", flush=True)
        print(f"  {voice} 完成: {ok} 成功 / {fail} 失败")

    print("\n" + "=" * 60)
    print(f"全部完成：{total_ok} 成功 / {total_fail} 失败")
    print(f"输出目录：{OUT_BASE}/")
    print("=" * 60)


if __name__ == "__main__":
    main()