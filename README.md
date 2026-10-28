# security-architect
Security Architects concerns


https://rifaterdemsahin.github.io/security-architect/

## Audio

Every flashcard has a spoken question and model answer in `audio/q{id}-question.mp3` and `audio/q{id}-answer.mp3`, generated with Xiaomi MiMo TTS (`mimo-v2.5-tts`).

To regenerate after editing questions in `index.html` (needs `az login` to the deliverypilot tenant and `ffmpeg`):

```bash
python3 scripts/generate_audio.py           # only missing files
python3 scripts/generate_audio.py --force   # everything
python3 scripts/generate_audio.py --ids 3 7 # specific questions
```

The MiMo API key is read from Azure Key Vault `dp-kv-deliverypilot`, secret `live-asistant-xiamimimo`.
