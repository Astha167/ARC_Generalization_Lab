# ARC Generalization Lab — Simple & Natural Demo Script (~1:45)

> **Speaker Note:** Talk naturally, like you're showing a cool project to a friend on your laptop. Don't rush. Pause for half a second after each click.
> **Live Demo URL:** `https://frontend-navy-gamma-81.vercel.app/`

---

## ⏱️ 0:00 – 0:25 | The Big Question

- **What you're doing:** Open [ARC Generalization Lab](https://frontend-navy-gamma-81.vercel.app/). Move your mouse over the title, then click **`⚡ Start 60-Second Guided Journey`**.
- **What to say:**
  > "Hey everyone! Welcome to the ARC Generalization Lab.
  > 
  > Today, we're asking a simple question: when AI models score high on visual reasoning benchmarks like ARC, are they actually reasoning... or have they just seen the puzzles before on the internet?
  > 
  > That's what we built this lab to test. Let’s jump into our 60-second guided journey."

---

## ⏱️ 0:25 – 0:45 | Step 1 & 2: How ARC Works & The Common Trap

- **What you're doing:** 
  1. In Step 1, click **`🤖 Run Heuristic Solver`**, then click **`👁️ Reveal Reference Output`**.
  2. Click **`Proceed to Step 2`**.
  3. Under Step 2, click the **`NO`** button.
- **What to say:**
  > "In Step 1, we see how ARC works: you look at a couple of grid examples, figure out the pattern, and solve the puzzle. Here, our solver predicts the answer, and we can compare it with the ground truth.
  > 
  > But in Step 2, here's the catch: if a model gets this right, does that prove general intelligence?
  > 
  > We click **No**—because these puzzles have been public for years. A high score might just be memorization."

---

## ⏱️ 0:45 – 1:15 | Step 3 & 4: The Live Test & Why Nuance Matters

- **What you're doing:** 
  1. Click **`Proceed to Step 3`**, then click **`▶ Run Diagnostic Comparison`**. 
  2. Point at the two scores and the performance gap.
  3. Click **`Proceed to Step 4`**, then click **Option C**.
- **What to say:**
  > "So in Step 3, we run a real test. We take the exact same solver and test it on public puzzles versus freshly generated puzzles that were never on the internet.
  > 
  > Notice the drop in performance—that's our diagnostic gap!
  > 
  > But here's the key lesson in Step 4: **a gap does NOT automatically prove the AI cheated or memorized.** The fresh puzzles might just be harder, or the generator might have small differences. It’s a diagnostic clue, not instant proof."

---

## ⏱️ 1:15 – 1:45 | Step 5: Learning Without Retraining (BDH-CQ)

- **What you're doing:** 
  1. Click **`Proceed to Step 5`**, then click **`🔬 Inspect & Manipulate BDH-CQ Recurrent State ↓`**.
  2. In the sandbox:
     - Pick a different **Pattern** from the dropdown.
     - Drag the **Retention Rate** slider slightly.
     - Point at the **$4 \times 4$ heatmap** changing live.
- **What to say:**
  > "Finally, how can models learn new rules on the fly without retraining?
  > 
  > Most approaches update their neural weights with gradient descent. But **BDH-CQ** takes an exciting path: it keeps all weights completely frozen, and adapts entirely through a fast recurrent memory.
  > 
  > In this interactive sandbox, you can see it live. As I change the pattern or adjust the memory slider, the state matrix updates instantly—learning the rule in real time without retraining."

---

## ⏱️ 1:45 – 1:55 | Wrap-Up

- **What you're doing:** Scroll back up to the top navbar.
- **What to say:**
  > "That's our project: an interactive, honest lab testing how AI really reasons outside its training data. Try the live link below. Thanks for watching!"
