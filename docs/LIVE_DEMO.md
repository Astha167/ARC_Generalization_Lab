# ARC Generalization Lab — 2-Minute Video Demo Script

> **Tone:** Friendly, confident, and curious — like walking a colleague through an interactive paper.  
> **Target Length:** 1:50 – 1:58 (allows natural pauses between clicks).  
> **Total Spoken Word Count:** ~240 words (ideal speaking pace: ~130 words/minute).  
> **Live Demo URL:** `https://frontend-navy-gamma-81.vercel.app/`

---

## 🎬 Video Overview & Timeline

```
0:00 ─── 0:25 ─── 0:50 ────────── 1:25 ────────── 1:55 ── 2:00
 Hook    Try &     Diagnostic Gap   BDH-CQ State   Wrap-up
 & ARC   Question  & Scientific     Recurrence     & URL
 Claim   (Step 1-2) Honesty (3-4)   Sandbox (Step 5)
```

---

## ⏱️ 0:00 – 0:25 | The Big Question: Reasoning or Memorization?

- **On Screen:** Start at `https://frontend-navy-gamma-81.vercel.app/`. Mouse hovers briefly over the hero question: *"Does an AI benchmark measure generalization—or familiarity?"* Then click the glowing **`⚡ Start 60-Second Guided Journey`** button.
- **Spoken Script (Natural & Engaging):**
  > "Public AI benchmarks like ARC-AGI have been floating around the web for years. Recent research by Bordes and others showed these tasks actually leaked into web-scale training data.
  > 
  > So when a model scores high on public ARC puzzles, is it genuinely reasoning... or just recalling familiar patterns?
  > 
  > We built the **ARC Generalization Lab** to test this live, comparing public tasks against freshly generated, distribution-matched tasks."

---

## ⏱️ 0:25 – 0:50 | Step 1 & 2: Hands-On ARC & The Conceptual Trap

- **On Screen:** 
  1. In **Step 1**, click **`🤖 Run Heuristic Solver`**, then click **`👁️ Reveal Reference Output`**. 
  2. Click **`Proceed to Step 2`**.
  3. In **Step 2**, click **`NO`** (*"NO — Public accuracy alone cannot distinguish..."*).
- **Spoken Script (Storytelling):**
  > "In Step 1, we see what makes ARC unique: inducing a visual rule from just a few examples. Here, our heuristic solver predicts the grid, and we can inspect the exact diff against ground truth.
  > 
  > But here's the trap in Step 2: if a model solves public puzzles, does that prove general intelligence?
  > 
  > We click **No**—because without testing on brand-new, unseen tasks, benchmark accuracy alone cannot prove generalization."

---

## ⏱️ 0:50 – 1:25 | Step 3 & 4: Live Diagnostic & Scientific Honesty

- **On Screen:** 
  1. Advance to **Step 3**, click **`▶ Run Diagnostic Comparison`**. 
  2. Point cursor at the **Public Score**, **Fresh Score**, the **Diagnostic Gap**, and the **95% Wilson Confidence Interval**.
  3. Click **`Proceed to Step 4`**, then click **Option C** (the nuanced explanation).
- **Spoken Script (Clear & Thoughtful):**
  > "In Step 3, we run the exact same solver across both public tasks and newly synthesized, distribution-matched tasks from the arc-task-gen pipeline. Notice the 95% Wilson confidence interval right here on the gap.
  > 
  > But here's our core scientific claim: **a performance gap does NOT prove memorization.**
  > 
  > As we show in Step 4, a gap is a diagnostic signal. It could be benchmark familiarity, but it could also come from generator artifacts, task ambiguity, or solver limitations."

---

## ⏱️ 1:25 – 1:55 | Step 5 & BDH-CQ: Test-Time Adaptation Without Backprop

- **On Screen:** 
  1. Click **`Proceed to Step 5`**, then click **`🔬 Inspect & Manipulate BDH-CQ Recurrent State ↓`**.
  2. In the interactive sandbox:
     - Change the **Pattern** dropdown.
     - Move the **Retention Rate $\alpha$** slider slightly.
     - Point cursor at the **$\nabla_W \mathcal{L} = 0$** badge and the **$4 \times 4$ State Heatmap**.
- **Spoken Script (Excited & Focused):**
  > "So how should a model adapt to brand-new tasks? 
  > 
  > Systems like TTT and HRM run gradient descent at test time, updating weights. But **BDH-CQ** keeps all weights permanently frozen—zero parameter updates—adapting entirely through forward-pass recurrent state accumulation.
  > 
  > In this live interactive substrate, you can watch that happen: as we adjust the retention rate $\alpha$ or feed new demonstrations, the associative state matrix $S_t$ updates in real time, sharpening the readout without touching a single weight."

---

## ⏱️ 1:55 – 2:00 | Clean Wrap-Up

- **On Screen:** Scroll smoothly to the top navbar or the references section at the bottom.
- **Spoken Script (Punchy finish):**
  > "Ground truth beside estimate, reproducible in 60 seconds, and completely open source. Try it yourself at the link below. Thanks for watching!"

---

## 🎙️ Speaker Pro-Tips

| Tip | Why it helps |
|---|---|
| **Pause for 0.5s when clicking** | Lets the viewer see the button press before hearing the result. |
| **Pronounce "BDH-CQ" as letters** | Say *"B-D-H C-Q"* cleanly and deliberately. |
| **Stress key terms** | Emphasize *familiarity*, *diagnostic signal*, *does not prove memorization*, and *zero gradient updates*. |
| **Keep mouse movement smooth** | Avoid circling or shaking the mouse erratically; move smoothly between panels. |
