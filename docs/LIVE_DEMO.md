# ARC Generalization Lab — Voiceover Video Script (~1:50)

> **Format:** Voiceover Cue Sheet (read aloud while the screen recording plays).  
> **Pacing:** Calm, conversational, and natural. Don't rush to fill dead air—let the screen actions breathe.  
> **Live Site:** `https://frontend-navy-gamma-81.vercel.app/`

---

## 🎬 Master Voiceover Cue Sheet

### ⏱️ [0:00 – 0:18] | INTRO & THE QUESTION

| Video Action on Screen | Voiceover Line (What you say) |
|---|---|
| Screen shows homepage hero banner. Mouse hovers over *"Does an AI benchmark measure generalization—or familiarity?"* | *"Have you ever wondered if AI models that crush public benchmarks are actually reasoning... or if they just memorized the test set from training data?"* |
| Cursor clicks **`⚡ Start 60-Second Guided Journey`**. Page smoothly scrolls down to Step 1. | *"ARC-AGI tasks have been on the web since 2019. We built this lab to test what happens when you evaluate models on brand-new, unseen puzzles."* |

---

### ⏱️ [0:18 – 0:42] | STEPS 1 & 2: THE ARC TEST & THE TRAP

| Video Action on Screen | Voiceover Line (What you say) |
|---|---|
| Step 1 is visible. Cursor clicks **`🤖 Run Heuristic Solver`**, grid renders, then clicks **`👁️ Reveal Reference Output`**. | *"Starting in Step 1, here's how ARC works: look at a couple of grid examples, infer the pattern, and predict the output. Our solver gets this one right."* |
| Clicks **`Proceed to Step 2`**. Step 2 question appears. Cursor clicks the red **`NO`** button. | *"Now in Step 2, here's the trap: does solving this prove general reasoning? We click No—because a high score on public puzzles might just be familiarity."* |

---

### ⏱️ [0:42 – 1:12] | STEPS 3 & 4: THE GAP & WHY NUANCE MATTERS

| Video Action on Screen | Voiceover Line (What you say) |
|---|---|
| Clicks **`Proceed to Step 3`**. Cursor clicks **`▶ Run Diagnostic Comparison`**. Spinner spins briefly, then score cards populate with 95% CI. | *"In Step 3, we run the real test: the exact same solver tested on public puzzles versus freshly generated puzzles. Look at that drop—that's our diagnostic gap."* |
| Clicks **`Proceed to Step 4`**. Quiz choices appear. Cursor clicks **Option C**. Green feedback box opens. | *"In Step 4, we highlight a crucial scientific point: this gap does NOT prove memorization. The fresh puzzles might be harder, or the generator might have subtle biases. It’s a diagnostic clue, not instant proof."* |

---

### ⏱️ [1:12 – 1:42] | STEP 5: LEARNING WITHOUT RETRAINING (BDH-CQ)

| Video Action on Screen | Voiceover Line (What you say) |
|---|---|
| Clicks **`Proceed to Step 5`**, then clicks **`🔬 Inspect & Manipulate BDH-CQ Recurrent State ↓`**. Sandbox scrolls into view. | *"So how can a model learn new rules without retraining? Instead of running backprop on test examples, models like BDH-CQ adapt through a fast recurrent memory—with weights permanently frozen."* |
| Cursor changes the **Pattern** dropdown, nudges the **Retention Rate** slider, and hovers over the $4 \times 4$ heatmap and `∇W L = 0` badge. | *"In this live interactive sandbox, you can see it in action. As I adjust the memory slider or change patterns, the internal state matrix updates instantly, learning the rule in real time without retraining."* |

---

### ⏱️ [1:42 – 1:52] | WRAP-UP

| Video Action on Screen | Voiceover Line (What you say) |
|---|---|
| Page scrolls back up to the clean top view or repository link in the footer. | *"An interactive, scientifically honest look at whether AI benchmark performance survives fresh tasks. Try the live demo at the link below. Thanks for watching!"* |

---

## 🎧 Voiceover Timing Tips

1. **Match the Clicks:** If the video takes 2 seconds to click a button, wait for the click before delivering the punchline.
2. **Natural Pauses:** Between Step 2 and Step 3, take a one-second breath. Silence while a button is clicked feels professional and deliberate.
3. **Conversational Pitch:** Imagine you're narrating a Loom video for a teammate. Keep your tone light, curious, and clear.
