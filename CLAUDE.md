# Joy of Convolution Sim

Tier 1 teaching utility: a browser port of Steven Crutchfield's JHU Java applets *The Joy of
Convolution* (continuous time, 1996) and its discrete-time version (Crutchfield 1997, updated by
Michael Ross 2001), for a Seattle Pacific University course. Sibling and style model:
`../Feedback Phase Shift Sim` (single-file HTML, GitHub Pages, README as the student landing page).

## Read first
- [PLAN.md](PLAN.md): decisions, phases, the permission gate, credits list.
- [RESEARCH.md](RESEARCH.md): what the original is, the asset list, and applet behavior and units
  from reading `Convolve.java`.
- [QUIRKS.md](QUIRKS.md): original quirks kept on purpose, and the port's deliberate deviations.
  **Add to it whenever a deviation is made.** [CHECKLIST.md](CHECKLIST.md): Jon's hands-on test.
- [DOWNLOAD_LIST.md](DOWNLOAD_LIST.md): exact URLs of the originals to save into `reference/`.
- [ENHANCEMENT_OPTIONS.md](ENHANCEMENT_OPTIONS.md): options for the professor. None approved yet.
- [BACKLOG.md](BACKLOG.md): enhancement checklist and the other JHU applets.

## The CT page (`joy_of_convolution.html`)
- Single file, no libraries, runs from `file://`. Classes transcribe `Convolve.java` with the same
  names; **Java int semantics are kept exactly** (`idiv`, `toInt` = truncation), which is why
  the arrays match the original bit for bit. Don't "improve" the arithmetic to floats.
- Panel bounds are hard-coded from `reference/captures/ct/geometry.txt` (`LAYOUT`), not a
  GridBag re-implementation. One canvas per AWT component; the whole applet scales by `z`
  (`fit()`), and each canvas is redrawn at `z * devicePixelRatio`.
- `Graphics` is a tiny java.awt.Graphics stand-in; `drawLine` strokes pixel centres with square
  caps and batches same-colour lines (thousands per drag event).
- `ConvPanel` draws signals directly instead of the original's two offscreen images: whenever
  `fSigChanged` is false those images equal the current signals, so it's equivalent.
- The equation image in the y panel is redrawn as canvas text (`drawEquation`); no JHU
  images, audio or PDFs are referenced (a static test enforces that).
- `window.onerror` lives in its own `<script>` before the main one, so a parse error in the
  main script still shows the red `#err` bar.
- Hash modes: `#selftest` runs the CtProbe scenarios in a hidden second applet and writes JSON to
  `#selftest-out`; `#shot=<scenario>:<a-e>` shows only the applet at 1x after that step (an
  unknown name throws, so the red bar shows). `window.JOC` exposes the applet, `runScenario`,
  `dump` for tests and screenshots.
- `SCENARIOS`: s1-s5 are preset pairs + a rightward t sweep (steps a-e); s7-s9 are
  `[name, actions]` lists (`['preset', 'x', name]`, `['down'|'drag', 'x'|'h'|'conv', x, y]`)
  for leftward/outside drags, drawing on h, the cleared state, single clicks. **Each list exists
  three times** (page, `tests/*_model.py`, `tools/*Probe.java`); a static test checks they agree.
  Design rule: a scenario's end state must show what it tests (s7 once ended with a full sweep
  that hid whether the leftward drag revealed anything; mutation testing caught it).
- One pointer at a time (`pointer`, `mayPress`): a second finger is ignored; releases are
  watched on `window`; a move with `buttons === 0` or any new mouse press ends a lost drag.
- First paint is synchronous (`fit()` at the end of the script): headless Chrome may run no
  animation frames before `--dump-dom`. Later repaints are coalesced with rAF.

## The DT page (`joy_of_convolution_dt.html`)
- Same shell as the CT page (Graphics stand-in, `fit()`, hash modes, `window.JOC`, synchronous
  first paint). Classes transcribe the **bytecode** (`reference/dt/javap/`), original names kept.
  Values are doubles; Java `Math.round` = JS `Math.round`, `(int)` = `Math.trunc` (`jround`,
  `d2i`). Equality with the original is exact, so keep operation order as in the bytecode.
- `MyMouseListener` in the JAR is unused (the panels use `MyMouseGraphListener`); not ported.
- The y panel's `'//definition'` label triggers drawing the equation (the original loads an
  image named there); `drawDefinition` redraws it as text. Preset icons are our own schematic
  stem plots (`ICONS`, `paintIcon`); their canvases are only the 29 x 21 icon, inside a bordered
  `<button>` whose hover colour is the signal colour (SignalClickListener).
- Whole-applet repaint per event (cheap); `DTConvolve.repaint` coalesces with rAF.
- Scenarios d6-d8 are action lists like CT's s7-s9 (panel `'dual'` instead of `'conv'`); the
  pointer handling is the CT page's.

## Tests and checks
- `py -m unittest discover -s tests -v` (stdlib; browser tests skip without Chrome/Edge).
  `tests/ct_model.py` is an independent Python transcription of the Java math.
  `test_model.py`: analytic checks (triangle, closed-form pulse*decay) + model == original's
  JSON (skipped without `reference/`). `test_html_portable.py`: static portability and
  credits; headless load with no error and 13 canvases painted; real PointerEvents at z != 1;
  `#selftest` == model == original (all 8 scenarios); no JHU file tracked by git; the scenario
  lists agree in page/model/probe. It also holds the shared browser helpers (`run_probe`
  appends a script to a temp copy of a page; `POINTER_JS` `fire()` sends PointerEvents with
  real `buttons`). `test_dt.py`: the same for DT (`tests/dt_model.py`, a Python transcription
  of the bytecode; y[n] == direct convolution sum; autoscale quirks). `test_ui.py`, both pages:
  keyboard presets, one pointer at a time, lost releases, rAF repaint + readout (probes queue
  rAF themselves; headless may run no frame), `layout()`, the `#shot` guard, and drawing:
  pixels where the model puts each sample have the signal's colour (works without `reference/`).
- Mutation check used in the 2026-11-17 review: inject a bug into a page, run the suite, restore
  (8 of 8 caught). Repeat it when adding tests: a test that never fails proves nothing.
- `py tools/compare.py ct|dt` (Pillow): screenshots every `#shot` at 1x and writes
  original | port | diff sheets to `reference/captures/compare/<ct|dt>/`. Currently < 1 % (CT)
  and ~1.7 % (DT) of pixels differ: text antialiasing, steep edges, redrawn equation/icons.
- README demo GIFs `docs/{ct,dt}-demo.gif`: `py tools/make_demo.py` (headless Chrome renders each
  frame of a t/n sweep from a temp page copy; Pillow assembles them).
- Older screenshot `docs/ct-port.png` (no longer in the README): a scratch copy of the page with a script appended that
  runs `JOC.runScenario(JOC.applet, JOC.SCENARIOS[2], 'c')`, drags to x = 300, then
  `JOC.applet.layout(1.15, 1)`; headless Chrome at 1280x1500, cropped to the white applet box.

## Hard rules
- **Credit Crutchfield / JHU / Rugh prominently** on every page and in the README. It's their work.
  Name people in plain text. **Never @-mention anyone on GitHub** (no announcements yet).
- **Original JHU material is "all rights reserved".** It stays in `reference/` (gitignored).
  Never commit or publish it.
- **Public dev repo is approved** (Jon, 2026-11-17): `electricyoshi/Joy-of-Convolution-Sim` is
  public, for development and collaboration with the professor. **Students and announcements
  stay gated** on written permission from the original authors (PLAN.md, BACKLOG.md). Keep the
  README marked work-in-progress with full credits; no student-facing links until permission.
- **Faithful first:** no enhancements until the professor picks from ENHANCEMENT_OPTIONS.md.
  Keep the original's quirks and list them; don't fix them silently.
- pages.jh.edu is behind Cloudflare: scripted fetches (curl/WebFetch) get 403, and spoofing a
  browser user-agent is not allowed. Read it through Claude-in-Chrome, or have Jon save files.

## Local tools (nothing on PATH; use full paths)
- **JDK 8** (Temurin 8.0.512.9, installed files-only 2026-11-17 for `appletviewer` + `javap`):
  `C:\Program Files\Eclipse Adoptium\jdk-8.0.512.9-hotspot\bin\`. **Uninstall when the
  reference work is done:** `winget uninstall EclipseAdoptium.Temurin.8.JDK`. Remind Jon if
  it's still installed at the end of a session where that work finished.
- **faster-whisper** 1.2.1 (CUDA, `large-v3` cached):
  `C:\Users\Jon\AppData\Local\Programs\Python\Python313\python.exe`. `py` defaults to 3.14,
  which doesn't have it.
- Headless Chrome: `C:\Program Files\Google\Chrome\Application\chrome.exe`; Edge is also
  installed. No Node or Deno.

## Ground-truth tools (`tools/`, our code; outputs go to gitignored `reference/captures/`)
- `CtProbe.java` / `DtProbe.java` run the **original applets' own classes** under JDK 8 and
  script user actions (presets, freehand drawing, t/n sweeps). They write `geometry.txt` (exact
  GridBag bounds), 1x PNGs, and per-scenario JSON of the internal arrays. **The JSON is the
  oracle for the port's parity tests.** Not appletviewer: an in-process harness is deterministic.
  CT drives the AWT 1.0 handlers directly (`mouseDown(null,x,y)`); DT dispatches Swing MouseEvents.
  ```
  J="/c/Program Files/Eclipse Adoptium/jdk-8.0.512.9-hotspot/bin"
  "$J/javac.exe" -nowarn -cp reference/ct -d tools/build tools/CtProbe.java
  "$J/java.exe" -cp "tools/build;reference/ct" CtProbe reference/ct reference/captures/ct
  "$J/javac.exe" -nowarn -cp reference/dt/classes -d tools/build tools/DtProbe.java
  "$J/java.exe" -cp "tools/build;reference/dt/classes" DtProbe reference/dt reference/captures/dt
  ```
  `reference/dt/classes/` = the unpacked `DTConvolve.jar`; `reference/dt/javap/` = full disassembly.
- `transcribe.py` (system Python 3.13) → `reference/transcripts/{ct,dt}_{welcome,exercises}.txt`
  (raw Whisper output with timestamps). `--pass2` (no conditioning on previous text, VAD on)
  writes `*_pass2.txt`; it fixed pass 1's looping/invented sentences. Use pass 2 as the base.

## Status
- 2026-11-17: git repo created and pushed (public, `electricyoshi/Joy-of-Convolution-Sim`, main).
- Phase 0 done. The 10 DT button GIFs were fetched 2026-11-17 through Claude-in-Chrome (in-page
  `fetch`, base64 back, written to `reference/dt/`); DtProbe re-run; RESEARCH.md DT geometry updated.
- **Phase 1 (CT) first port done 2026-11-17**: arrays identical to the original in all 5
  scenarios, tests green. Waiting for Jon's CHECKLIST.md run on Windows and Mac, and his check of
  the transcripts against the audio (the page's text was cleaned up from Whisper
  `*_pass2.txt`, which fixed pass 1's invented sentences in ct_exercises).
- **Phase 2 (DT) first port done 2026-11-17**: values identical to the original (every double,
  axes, n, reset) in all 5 DtProbe scenarios. DtProbe now also records the autoscaled axes and
  `reset`; `definition.gif` was fetched (Claude-in-Chrome) so its captures show the y equation.
- **Review 2026-11-17** (REVIEW.md): no arithmetic defects; the oracle grew to 8 scenarios per
  page (leftward/outside drags, h drawing, cleared state, clicks), all identical; fixed
  multi-touch splicing, a lost release leaving a drag stuck, and silent bad `#shot` names.
  Suite: 56 tests.
- 2026-11-18: Jon ran CHECKLIST.md, no issues. GitHub Pages enabled (legacy, `main` /):
  https://electricyoshi.github.io/Joy-of-Convolution-Sim/ . Shared with the signals professor only;
  still no student links until permission. README now leads with the run links + demo GIFs.
- Waiting on Jon: transcripts vs audio (punted; needs `reference/` copied to the new PC).
- Next: Phase 4 accessibility polish, then Phase 5 after permission. The JDK is only needed
  for re-capturing; **uninstall it once Jon has signed off the ports**
  (`winget uninstall EclipseAdoptium.Temurin.8.JDK`).
