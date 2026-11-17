# Joy of Convolution Sim

Tier 1 teaching utility: a browser port of Steven Crutchfield's JHU Java applets *The Joy of
Convolution* (continuous time, 1996) and its discrete-time version (Crutchfield 1997, updated by
Michael Ross 2001), for a Seattle Pacific University course. Sibling and style model:
`../Feedback Phase Shift Sim` (single-file HTML, GitHub Pages, README as the student landing page).

## Read first
- [PLAN.md](PLAN.md): decisions, phases, the permission gate, credits list.
- [RESEARCH.md](RESEARCH.md): what the original is, the asset list, and applet behavior and units
  from reading `Convolve.java`.
- [DOWNLOAD_LIST.md](DOWNLOAD_LIST.md): exact URLs of the originals to save into `reference/`.
- [ENHANCEMENT_OPTIONS.md](ENHANCEMENT_OPTIONS.md): options for the professor. None approved yet.
- [BACKLOG.md](BACKLOG.md): enhancement checklist and the other JHU applets.

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
  (raw Whisper output with timestamps, not yet cleaned up or checked by Jon).

## Status
- 2026-11-17: Phase 0 done except one item. CT captures complete (geometry in RESEARCH.md).
  DT captures were taken **without the 10 button GIFs** (DOWNLOAD_LIST.md §5): once Jon saves
  them, re-run DtProbe (the button-row layout depends on icon size) and update the DT geometry
  in RESEARCH.md. Transcripts: raw. Next: Phase 1, CT port (PLAN.md). The JDK is still needed
  for that (DT re-capture, comparisons).
