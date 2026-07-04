---
name: Three.js single-file game structure
description: How game3d.html (Подвал Безумия) is organized and constraints to respect when editing it
---

## Structure
The entire 3D game lives in one inline `<script type="module">` block inside `game/game3d.html` — no bundler, no separate JS files. All systems (movement, collisions, monster AI, jumpscare, inventory, HUD) are plain top-level functions/consts sharing module scope.

## Verifying edits
Since there's no build step or bundler, syntax errors only surface at runtime in the browser. After multi-part edits, extract the module script and run `node --check` on it to catch syntax errors before restarting the workflow — this is much faster than round-tripping through the browser console.

**Why:** a batch of ~15 sequential `edit` calls across collisions/monster-AI/jumpscare/hands touched many interdependent sections; `node --check` caught issues immediately without needing a live browser session.

## Screenshot tool limitation
The `screenshot` tool's headless sandbox cannot create a WebGL context ("Could not create a WebGL context... BindToCurrentSequence failed"). This is an environment limitation of the screenshot sandbox itself, not a bug in the game — don't chase it as a real error. Rely on `node --check` + browser console log review instead of screenshots for this project.

## Key systems added (for future consistency)
- Collision: `wallColliders` array of `{x,z,hx,hz}` AABBs registered via `solidBox()`; player is a circle of radius `PLAYER_R` resolved via `resolveCollisions()` called per-axis in `handleMovement`.
- Monster AI: walks continuously via `monsterPos` vector at `MONSTER_SPEED` between room centers (graph-based via `ROOMS[].exits`), waits at rooms via `monsterWaitTimer`, triggers `encounter()` on proximity rather than teleporting.
- Jumpscare/respawn: `jumpscareActive`/`jumpscarePhase` drive a fly-at-camera animation, then fade via `#faint-overlay`, then `respawnPlayer()` resets to 'вход' and a `reviving`/`#wake-blur` blur-decay animation plays — inventory/quest state (`gs.inventory`, `gs.unlocked`, etc.) is untouched by respawn.
- First-person hands: `handsGroup` attached to `camera`; left arm always holds a flashlight mesh, right arm holds `gs.heldItem` via `setHeldItem(name)`, wired to inventory slot clicks (click to equip/unequip, dblclick to use).
- Monster chase/vision: `monsterState` ('patrol'|'chase'|'hidden') driven by a distance+cone-angle+`hasLineOfSight()` (AABB raymarch vs `wallColliders`) check; chase raises speed multiplier and can randomly hide/reappear near the player as a scare beat, separate from the proximity-triggered `encounter()` jumpscare.

## Synthesizing a "spoken" monster line without audio assets
Used the browser's built-in `SpeechSynthesisUtterance` (not Web Audio oscillators) to make the monster shout a Russian phrase, with very low `pitch` (~0.15) and slowed `rate` (~0.78) for a distorted/demonic effect, layered under a short Web-Audio screech.
**Why:** there are no voice audio assets in this project and recording/generating one wasn't in scope; the platform speech API is the only zero-asset way to get actual spoken words instead of generic noise bursts.
**How to apply:** pick a matching-language voice via `speechSynthesis.getVoices()` (populate on `onvoiceschanged` since voices load async), then set extreme `pitch`/`rate` values on the utterance for a horror tone — works well combined with a synthesized noise/screech for impact.
