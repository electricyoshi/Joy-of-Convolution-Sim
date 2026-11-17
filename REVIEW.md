# Code review: 2026-11-17

Scope: both pages, the two Python reference models, the two Java probes, the tests and `tools/`.

**Verdict:** the arithmetic is right. I re-checked the transcription against `Convolve.java` and
the DT bytecode at every point the scripted tests didn't already pin down, and found no defect.
The real gap was in *what the tests compared with the original*. The other findings are event
handling (touch) and tooling robustness. Everything below is fixed and committed except the last
section.

## Findings (fixed), most severe first

1. **The original was only checked on the "happy path"** (medium). The ground truth (the
   original applets run by CtProbe/DtProbe) covered five preset pairs with a *rightward* t/n
   sweep inside the panel. Never compared with the original: leftward drags, drags outside the
   panels (clamping, off-scale values, ends of the arrays), drawing on h, sketching over a
   preset, the cleared state after a change, single clicks, and DT axis growth from off-panel
   drawing. Added three action-list scenarios per page (CT s7–s9, DT d6–d8). The port, both
   Python models and the original agree exactly in all of them. The original 10 captures were
   re-generated and are byte-identical.
2. **Two fingers on a touch screen spliced into one drag** (medium, touch devices). Each panel
   had its own "pressed" flag, so a second finger restarted the stroke and both fingers' moves
   interleaved; on the conv panel t jumped between fingers. The original had one mouse, so now
   one pointer at a time drives the applet; other fingers are ignored until it lifts.
3. **A missed release could leave a drag stuck "on"** (low). If pointer capture failed (old
   Safari) and the button was released outside the canvas, plain mouse movement kept drawing.
   Now a move with no button down ends the drag, releases are watched on the whole window, and
   a new mouse press is always accepted, so the applet can't lock up.
4. **A mistyped `#shot=` name silently screenshotted the wrong state** (low, tooling). It ran
   every scenario instead, so `tools/compare.py` could compare the wrong picture with no error.
   It now throws, and the red error bar shows the bad name.
5. **One of my own new scenarios hid what it was testing** (low, tests). s7's first draft ended
   with a full left-to-right sweep, which reveals all of y(t) and masks whether the leftward
   drag revealed anything. Mutation testing caught it (below); s7/d6 now leave a deliberate gap.
   The design rule is in CLAUDE.md.
6. Trivial: comments named `tools/compare_ct.py` (it's `tools/compare.py`). The DT model shared
   one previous mouse position between the x and h panels, where the original has one per
   panel (no visible difference, since every drag starts with a press).

## New tests (34 → 56)

| What | Where | Needs `reference/`? |
|---|---|---|
| Page == model == original in all 8 scenarios per page | `test_html_portable`, `test_dt`, `test_model` | original only |
| Scenario lists identical in page, model and probe | `test_html_portable` | no |
| No JHU file tracked by git (hard rule) | `test_html_portable` | no |
| Error bar before main script on both pages; index links resolve | `test_html_portable` | no |
| Keyboard presets; one pointer at a time; lost release can't freeze the applet; only the conv / dual panel sets t / n | `test_ui` | no |
| Click → one coalesced repaint → screen-reader readout; cleared after a change | `test_ui` | no |
| `layout(z, dpr)` sizes every canvas and leaves the state alone; bad `#shot` → red bar | `test_ui` | no |
| Drawing: pixels where the model puts each sample have the signal's colour; hidden y samples aren't drawn; cleared panels have no signal colours | `test_ui` | no |

**Do the tests catch real bugs?** I injected 8 plausible bugs one at a time (second finger
accepted, flipped x drawn at the wrong offset, y drawn where not revealed, leftward drag reveals
nothing, keyboard activation lost, DT axis sign flipped, DT drag-left swap dropped, DT lower
panels drawn while reset). The suite caught all 8. Before the s7/d6 fix it caught 7.

## Not fixed (cosmetic, or can't be verified without hardware)

- **Moving the window to a monitor with a different scaling** may not fire `resize` in every
  browser, so the applet would stay at the old resolution (slightly soft) until the next resize.
  Unverified: needs two monitors. Worth a look in Phase 4 if Jon sees it.
- **DT preset button borders** keep their hover colour after a tap on a touch screen (CSS
  `:hover` sticks on touch). Cosmetic; the original had no touch support.

## How to validate (Jon)

- `py -m unittest discover -s tests -v`: 56 tests, all OK (about 25 s with Chrome installed).
- CHECKLIST.md has one new item: on a touch screen, a second finger is ignored while the first
  one drags.
