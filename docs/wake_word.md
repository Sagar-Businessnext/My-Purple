# Training a custom "hey purple" wake word

Purple's wake-word detector (openWakeWord) only recognises the exact phrase a model
was trained on. It ships pretrained words like `hey_jarvis` (Purple's default), but
"hey purple" has to be trained once. The code already supports it — after training,
you just point `PURPLE_WAKE_MODEL` at the model file. No code changes.

Training needs a GPU and runs on your PC (or free Google Colab), not inside Cowork.

## Easiest path — openWakeWord's automatic training notebook (recommended)

openWakeWord provides a Colab notebook that does everything: it generates thousands
of synthetic "hey purple" clips with TTS, mixes in background noise, and trains.

1. Open the official notebook:
   https://github.com/dscripka/openWakeWord → `notebooks/automatic_model_training.ipynb`
   (there's a "Open in Colab" badge).
2. Set the target phrase to: `hey purple`
3. Run all cells (≈30–60 min on Colab's free GPU). It produces `hey_purple.onnx`
   (and a `.tflite`).
4. Download `hey_purple.onnx` into `D:\Purple\models\`.
5. In `.env`:
   ```
   PURPLE_ENABLE_WAKE=true
   PURPLE_WAKE_MODEL=models/hey_purple.onnx
   ```
6. Run `python -m purple.voice` and say "hey purple".

## Local path — one command (train on your own RTX 5070 Ti)

A helper script automates the whole openWakeWord local flow (clone the tools, install
training deps, generate synthetic "hey purple" clips, augment, train, and copy the model
into `models/`):

```bash
python scripts/train_wake.py --word "hey purple"
```

- Options: `--samples 2000` (more clips = sturdier, slower), `--name hey_purple`,
  `--workdir .wake_training`, `--out models`.
- First run downloads a few GB (a Piper TTS voice + background/augmentation data) and,
  on a GPU, takes roughly 20-60 min. The result lands at `models/hey_purple.onnx`.
- Then set in `.env`:
  ```
  PURPLE_ENABLE_WAKE=true
  PURPLE_WAKE_MODEL=models/hey_purple.onnx
  ```
  Restart Purple and say "hey purple".

The script wraps openWakeWord's **own** training code (it doesn't reinvent training). If
openWakeWord changes their training API and a phase fails, fall back to the Colab notebook
above — it produces the same `hey_purple.onnx`, which you just drop into `models/`. Either
way the rest of Purple is unchanged.

## Tuning

- If it triggers too easily, raise `PURPLE_WAKE_THRESHOLD` (e.g. 0.6–0.7).
- If it misses you, lower it (e.g. 0.4) or train with more/varied samples.
- More training samples = fewer false triggers. The notebook's defaults are a fine start.

Until you train it, leave `PURPLE_WAKE_MODEL=hey_jarvis` — everything else in the
voice loop works identically.
