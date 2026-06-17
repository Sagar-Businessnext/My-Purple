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

## Local path (if you'd rather train on your own RTX 5070 Ti)

```bash
pip install openwakeword[training] piper-sample-generator
```

Then follow the same steps the notebook automates:
1. Generate positive clips of "hey purple" with piper-sample-generator (a few thousand,
   varied speakers/speeds).
2. Download openWakeWord's prebuilt negative/background feature sets (linked in their
   training docs).
3. Run their training script to produce `hey_purple.onnx`.

Full, current instructions live in the openWakeWord training docs — they change
occasionally, so follow theirs for the exact commands.

## Tuning

- If it triggers too easily, raise `PURPLE_WAKE_THRESHOLD` (e.g. 0.6–0.7).
- If it misses you, lower it (e.g. 0.4) or train with more/varied samples.
- More training samples = fewer false triggers. The notebook's defaults are a fine start.

Until you train it, leave `PURPLE_WAKE_MODEL=hey_jarvis` — everything else in the
voice loop works identically.
