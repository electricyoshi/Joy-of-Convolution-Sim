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
  `#selftest-out`; `#shot=<scenario>:<a-e>` shows only the applet at 1x after that step.
  `window.JOC` exposes the applet, `runScenario`, `dump` for tests and screenshots.
- First paint is synchronous (`fit()` at the end of the script): headless Chrome may run no
  animation frames before `--dump-dom`. Later repaints are coalesced with rAF.

## Tests and checks
- `py -m unittest discover -s tests -v` (stdlib; browser tests skip without Chrome/Edge).
  `tests/ct_model.py` is an independent Python transcription of the Java math.
  `test_model.py`: analytic checks (triangle, closed-form pulse*decay) + model == original's
  JSON (skipped without `reference/`). `test_html_portable.py`: static portability and
  credits; headless load with no error and 13 canvases painted; real PointerEvents at z != 1;
  `#selftest` == model == original.
- `py tools/compare_ct.py` (Pillow): screenshots every `#shot` at 1x and writes
  original | port | diff sheets to `reference/captures/compare/ct/`. Currently < 1 % of pixels
  differ (text antialiasing, steep pulse edges, the redrawn equation).
- README screenshot `docs/ct-port.png`: a scratch copy of the page with a script appended that
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
- Phase 0 done except the 10 DT button GIFs (DOWNLOAD_LIST.md §5): once Jon saves them, re-run
  DtProbe (the button-row layout depends on icon size) and update the DT geometry in RESEARCH.md.
- **Phase 1 (CT) first port done 2026-11-17**: arrays identical to the original in all 5
  scenarios, tests green. Waiting for Jon's CHECKLIST.md run on Windows and Mac, and his check of
  the transcripts against the audio (the page's text was cleaned up from Whisper
  `*_pass2.txt`, which fixed pass 1's invented sentences in ct_exercises).
- Next: Phase 2, DT port (from `reference/dt/javap/`). The JDK is still needed for that.
