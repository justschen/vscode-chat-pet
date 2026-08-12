---
name: update-pet-previews
description: Use when VS Code chat pet sprites, sprite timings, eye geometry, or interactions change and the vscode-chat-pet README previews need to be regenerated from a checkout, branch, or pull request.
---

# Update Pet Previews

Regenerate the side-by-side Stable and Insiders README previews from the canonical VS Code pet sources without modifying the source sprites.

## Source of truth

- Sprite sheets: `src/vs/workbench/contrib/chat/browser/widget/media/chatPet/`
- State mapping and timings: `src/vs/workbench/contrib/chat/browser/widget/chatPetWidget.ts`
- Preview generator: `scripts/regenerate_pet_previews.py`
- Generated APNGs: `readme-assets/`

Keep previews as animated PNGs. GitHub wraps `.gif` files in an animated-image player that can render blank in some browser profiles; APNGs render directly and preserve pixel-perfect frames and timing.

## Setup

From the `vscode-chat-pet` repository:

```sh
python3 -m pip install -r requirements.txt
```

The default VS Code checkout is the sibling folder `../vscode`. Override it with `--vscode-root`.

## Update from a VS Code pull request

Fetch the PR as a read-only ref. Do not check it out or modify the VS Code worktree:

```sh
git -C ../vscode fetch origin pull/<PR_NUMBER>/head:refs/remotes/origin/pr-<PR_NUMBER>
```

Regenerate only affected previews:

```sh
python3 scripts/regenerate_pet_previews.py \
  --vscode-root ../vscode \
  --ref refs/remotes/origin/pr-<PR_NUMBER> \
  --only sleep-wake fall-respawn-v2
```

Names may be provided with or without `.png`.

## Update from the current VS Code worktree

Regenerate every animated preview:

```sh
python3 scripts/regenerate_pet_previews.py --vscode-root ../vscode
```

Or regenerate selected previews:

```sh
python3 scripts/regenerate_pet_previews.py \
  --vscode-root ../vscode \
  --only cursor-gaze dizzy
```

The generator:

1. Reads sprite bytes from the worktree or selected Git ref.
2. Reads frame durations and wide-sprite widths from `chatPetWidget.ts`.
3. Applies the runtime tall-eye, blink, drag, and movement treatments.
4. Produces looping APNGs for Stable and Insiders.
5. Validates every image referenced by the README.

## Adding a new state

When a new runtime state appears:

1. Add its sprite entry to `SPRITES` in the generator.
2. Add a renderer that explains how the state is triggered, not only the isolated sprite.
3. Add it to `ANIMATIONS`.
4. Add a concise README row with descriptive alt text.
5. Regenerate and visually review both colorways.

Use the exact runtime frame timing and source dimensions. Wide sprites are centered as a complete envelope while their body remains anchored within the source frame.

## Review

After generation:

```sh
git status --short
git diff --stat
```

Open every changed APNG and check:

- Stable remains blue and Insiders remains green.
- Source art is pixel-sharp with no smoothing.
- Eye dimensions, blink, gaze, and facing match the runtime CSS.
- Wide sprites do not recenter the body unexpectedly.
- Movement communicates the trigger and result.
- Platform occlusion hides pixels below the platform.
- Frame timing and loops are intact.

Never modify or commit files in the VS Code checkout. Do not commit `.DS_Store` or temporary contact sheets.

## Publish

Commit only the README, generator/skill changes, and referenced assets. Preserve configured commit signing and hooks. Push `main`, then verify the public README has:

- No broken or zero-sized images.
- No `.gif` links or GitHub animated-image wrappers.
- All expected rows and alt text.
