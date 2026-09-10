# DataForge — Conversational Demo Video Script (2 Minutes)

> **Speaker Note:** Talk like you're showing a cool project to a colleague over coffee. Don't read word-for-word—use these natural phrases, conversational pauses, and cues. Keep your mouse steady while speaking.

---

## ⏱️ 0:00 – 0:20 | The Hook & The Big Question

- **What you're doing:** Open [ARC Generalization Lab](https://frontend-navy-gamma-81.vercel.app/) (or `localhost:5173`). Circle your mouse slightly over the main question on screen, then click **`⚡ Start 60-Second Guided Journey`**.
- **What to say (Casual & Confident):**
  > "Hey everyone. So, public AI benchmarks like ARC-AGI have been floating around the web since 2019. And that brings up a really uncomfortable question: when a model crushes these benchmarks, is it actually reasoning... or did it just memorize the test set from its training data? 
  > 
  > That's exactly what we built **DataForge** to investigate. Our central thesis is simple: a high benchmark score doesn't prove generalization on its own. We need to compare it against freshly generated, distribution-matched tasks."

---

## ⏱️ 0:20 – 0:45 | Step 1 & 2: Hands-On ARC & The Conceptual Trap

- **What you're doing:** 
  1. In Step 1, click **`🤖 Run Heuristic Solver`**, then click **`👁️ Reveal Reference Output`**. 
  2. Click **`Proceed to Step 2`**. 
  3. Under Step 2, click the **`NO`** option (*"NO — Public accuracy alone cannot distinguish..."*).
- **What to say (Storytelling tone):**
  > "Let's kick off with Step 1. ARC is all about figuring out a visual rule from just a couple of examples. Here, we can run our heuristic solver to predict the pattern, and immediately reveal the ground truth to check its work. 
  > 
  > Now in Step 2, we tackle the classic pitfall: if a model gets 85% on public ARC, does that prove it's reasoning? We click 'NO'—because without testing on brand-new, unseen puzzles, there's just no way to tell true rule induction apart from simple benchmark familiarity."

---

## ⏱️ 0:45 – 1:10 | Step 3 & 4: The Live Diagnostic & Scientific Honesty

- **What you're doing:** 
  1. Go to Step 3, click **`▶ Run Diagnostic Comparison`**. Point out the public score, fresh score, and the gap badge.
  2. Advance to Step 4, click **Option C** (the nuanced explanation).
- **What to say (Authentic & Thoughtful):**
  > "Now watch this. In Step 3, we take the exact same solver and test it side-by-side on public tasks versus freshly generated tasks. And notice our transparency badge right here—if live credentials aren't plugged in, we explicitly label this as fallback demo data rather than faking numbers.
  > 
  > But here’s the most important scientific point in our project: when you see a performance drop, **it does NOT automatically prove memorization**. In Step 4, we teach learners that a gap is a diagnostic signal. It could mean familiarity, sure—but it could also stem from generator artifacts, distribution mismatch, or baseline solver limits."

---

## ⏱️ 1:10 – 1:45 | Step 5 & BDH-CQ: Recurrent Memory in Action

- **What you're doing:** 
  1. Advance to Step 5 and click **`🔬 Inspect & Manipulate BDH-CQ Recurrent State ↓`**.
  2. In the interactive sandbox:
     - Change the **Demonstration Rule** dropdown to **Pattern B (Directional Shift)**.
     - Toggle **Demonstrations** from `2` to `3`.
     - Nudge the **Retention Rate $\alpha$** slider.
- **What to say (Excited & Clear):**
  > "So how *should* a model adapt to new examples on the fly? Some systems, like HRM, run full backprop at test time, literally updating weights. But **BDH-CQ** takes an entirely different path: it keeps its weights completely frozen—zero gradient updates—and adapts entirely through a recurrent associative memory state.
  > 
  > We built this live interactive toy model so you can see that happen in real time. Watch what happens as I change the demonstration pattern or add another example: the four-by-four state matrix visibly evolves, the Frobenius norm recalculates, and the prediction readout sharpens—all inside forward-pass inference without touching a single weight."

---

## ⏱️ 1:45 – 2:00 | Wrap-up & Literature Grounding

- **What you're doing:** Scroll down to the bottom references section (`#references`), pointing to the citations (Engdahl et al., Bordes et al., Akyürek et al.).
- **What to say (Polished finish):**
  > "Everything in DataForge is grounded in recent 2024 to 2026 research, backed by clean evidence labeling and automated tests. It’s a transparent, interactive tool built to help anyone explore the real boundary between benchmark memorization and true generalization. Thanks for watching!"

---

## 💡 Quick Tips for Recording
- **Don't stress over a pause:** A half-second pause while you click a button sounds much more natural than talking nonstop.
- **Smile while speaking:** It gives your voice warmth and makes you sound genuinely interested in the demo.
- **Key words to stress naturally:** *familiarity*, *diagnostic signal*, *does not prove memorization*, *zero gradient updates*.
