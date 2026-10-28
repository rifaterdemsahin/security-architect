# 🇬🇧 UK Gov Security Architect: Interview Prep 🛡️

Flashcards, a revision sheet and a timed mock interview board for **UK Central Government Security Architect** roles (SFIA 3 and SFIA 5). Every question and model answer can also be played as audio. 🔊

🌐 **Live site:** https://rifaterdemsahin.github.io/security-architect/
📦 **Repository:** https://github.com/rifaterdemsahin/security-architect

---

## 📚 What's inside

26 interview questions with model answers, buzzwords and hints, grouped by topic:

| Topic | Questions |
| --- | --- |
| 🏛️ UK Gov Assurance (SIRO, IRAR, GovAssure) | 5 |
| ☁️ AWS Security & Cloud | 6 |
| 🛡️ Network, Edge, WSO2 & PKI | 5 |
| 👁️ Protective Monitoring & SIEM | 3 |
| 🎖️ Leadership & SFIA 3 vs 5 | 6 |
| 🎯 Mock Board Question | 1 |

The content follows the 🏛️ [NCSC Cloud Security Principles](https://www.ncsc.gov.uk/collection/cloud/the-cloud-security-principles), 📐 [NIST CSF](https://www.nist.gov/cyberframework), ☁️ the [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html) and ✅ [GovAssure](https://www.gov.uk/government/publications/govassure).

## 🧠 The learning tactic

The site is built around four study habits that work well together: **active recall**, **spaced review**, **dual coding with audio** and **rehearsal under pressure**. Use the three modes in this order:

### 1️⃣ Flashcards: active recall 🃏
- Read the question on the front and **answer out loud before you flip**. Use the 💡 hint only if you're stuck.
- Press <kbd>Space</kbd> to flip and compare your answer with the model answer and the 🔑 buzzwords.
- Be honest when you rate yourself:
  - ✅ **Mastered**: you covered the key points and the buzzwords without help.
  - 🔄 **Needs Review**: you missed something, hesitated or needed the hint.
- 🔀 **Shuffle** the deck so you don't learn answers by their position.
- Your progress is saved in your browser, so you can pick it up later.

### 2️⃣ Spaced review: target your weak spots 🔁
- Go back to the 🔄 **Needs Review** cards first, ideally a day later and again a few days after that.
- Use the topic filters and 🔍 search (e.g. `SIRO`, `GuardDuty`, `mTLS`) to drill one area at a time.
- A card only becomes ✅ Mastered once you get it right on a later day, not just straight after reading it.

### 3️⃣ Listen: learn by ear 🎧
- Press 🔊 **Play Question** and answer before the model answer plays, just like a real panel.
- Press 🔊 **Play Answer** to hear how a strong answer is structured and how long it takes to say.
- Good for commutes and walks: open the 📄 **Revision Sheet** and play through the answers.
- Hearing the answer and reading it at the same time helps it stick (dual coding).

### 4️⃣ Mock Simulator: rehearse under pressure 🎯⏱️
- 🎲 **Draw a random panel question**. A **3-minute timer** starts, which is about the length of a real board answer.
- Answer out loud, ideally recording yourself, then reveal the model answer and tick off the key terms you used.
- Aim for a clear structure: **context, risk, controls, trade-offs, recommendation**.

> 💡 **Tip:** in the last week before the interview, run 5 mock questions a day and listen to the 🔄 Needs Review answers on the go.

## ⌨️ Keyboard shortcuts (Flashcards)

| Key | Action |
| --- | --- |
| <kbd>Space</kbd> | Flip card |
| <kbd>←</kbd> / <kbd>→</kbd> | Previous / next card |
| <kbd>K</kbd> | Mark ✅ Mastered |
| <kbd>R</kbd> | Mark 🔄 Needs Review |

## 🔊 Audio

Every flashcard has a spoken question and model answer in [`audio/`](audio/):

- `audio/q{id}-question.mp3`: the question, voice "Dean"
- `audio/q{id}-answer.mp3`: the model answer, voice "Mia"

They were generated with 🤖 [Xiaomi MiMo](https://platform.xiaomimimo.com/) TTS (`mimo-v2.5-tts`) by [`scripts/generate_audio.py`](scripts/generate_audio.py).

### ♻️ Regenerating after editing questions

You need 🐍 Python 3, 🎬 [ffmpeg](https://ffmpeg.org/) and the ☁️ [Azure CLI](https://learn.microsoft.com/cli/azure/) logged in to the deliverypilot tenant (`az login`).

```bash
python3 scripts/generate_audio.py           # only missing files
python3 scripts/generate_audio.py --force   # everything
python3 scripts/generate_audio.py --ids 3 7 # specific questions
```

🔐 The MiMo API key is read from Azure Key Vault `dp-kv-deliverypilot`, secret `live-asistant-xiamimimo`. It never lives in the repo. To skip the vault, set `XIAOMI_MIMO_API_KEY` instead.

## 🗂️ Project structure

```
📄 index.html                  # the whole app: questions, flashcards, revision sheet, simulator
🔊 audio/                      # generated question/answer MP3s
🐍 scripts/generate_audio.py   # MiMo TTS generator
⚙️ .github/workflows/          # GitHub Pages deployment
```

## 💻 Run locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000. Audio needs a web server, so opening the file directly may not play it.

## 🚀 Deployment

Every push to `main` deploys to 🌐 [GitHub Pages](https://rifaterdemsahin.github.io/security-architect/) through [`.github/workflows`](.github/workflows/).
