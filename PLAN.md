# Porting plan: The Joy of Convolution → modern browser (HTML5)

Status: **Phase 1 first port done** (2026-11-17; see CLAUDE.md "Status"). Background facts: [RESEARCH.md](RESEARCH.md). Later work: [BACKLOG.md](BACKLOG.md).

## Goal
Bring Steven Crutchfield's *Joy of Convolution* applets (Johns Hopkins University, 1996/1997,
part of Wilson J. Rugh's Signals, Systems and Control demonstrations) back to life for a
Seattle Pacific University course. The originals are **Java applets**; no current browser can
run them. The port is plain HTML + JavaScript + `<canvas>`, which runs in any current browser
with nothing to install and nothing for campus IT to approve.

This is their work. We are only updating it for modern browsers. Credit goes at the top of
every page, in the README, and in an About/credits section (see "Credits").

## Decisions (Jon, 2026-11-17)
| Topic | Decision |
|---|---|
| Scope | **Both** the continuous-time (CT) and discrete-time (DT) versions. Other JHU applets → BACKLOG. |
| Fidelity | **Near-perfect copy** of the original first. No additions yet. Enhancement options go in a separate doc for the course professor. |
| Narration audio | **Transcribe into text** on the page. |
| Hosting | **GitHub Pages**, same student experience as `../Feedback Phase Shift Sim`: open the GitHub URL → README with screenshots and examples → "Run it in your browser" link. |
| Devices | Windows and Mac laptops (current Chrome, Edge, Firefox, Safari). Tablets and phones: nice to have, not optimized. |
| Accessibility | SPU is private; WCAG 2.1 AA is best effort, not a hard requirement. |
| Credits | Name everyone credited on the original site. |
| Permission | Not requested yet. Jon and the collaborating professor will contact Crutchfield / Rugh / JHU before students use it. |
| Repo | **Public GitHub repo approved for development** (`electricyoshi/Joy-of-Convolution-Sim`), shared with the collaborating professor (Jon, 2026-11-17; supersedes the earlier local-only rule). Public exposure in the interim is accepted; student sharing and announcements still wait for permission. |
| Process tier | Tier 1 (single-file pages, no dependencies), plus the sibling sim's test pattern. |

## Permission (gate before students use it)
The JHU index says: "Copyright 1995-2003, Johns Hopkins University and Wilson J. Rugh, all rights
reserved… Copying or duplicating the images or code is prohibited." A faithful port translates
their code, and the transcripts and quiz reproduce their text, so all of it is a derivative work.
- Original files stay in `reference/` (gitignored) and are never committed or published.
- **Development happens in a public repo now** (Jon, 2026-11-17). That interim public exposure is
  accepted. The gate is on **students**: no student-facing links, no announcements, no course
  advertising until written permission is granted (BACKLOG.md).
- Choose the LICENSE after permission (it may have to be "used with permission", not MIT).
- If permission is refused: SPU-only use, distributed to enrolled students through the course
  LMS (GitHub Pages cannot restrict viewers). Decide then.

## Deliverables
```
joy_of_convolution.html      CT page: the whole original page, with the applet as a canvas
joy_of_convolution_dt.html   DT page, same treatment (done, first port)
index.html                   tiny Pages landing page linking both (the README is the GitHub landing page)
README.md                    credits first, screenshots, "Run it" links, things to try, offline copy
docs/*.png                   README screenshots
tests/                       py -m unittest discover -s tests -v
CLAUDE.md, PLAN.md, RESEARCH.md, BACKLOG.md
```
Each HTML file is one self-contained file: no libraries, no CDN, no network access, and it runs
from `file://` (offline copy, like the sibling sim). The **whole original page** is reproduced,
not just the applet: intro text, the convolution integral/sum (native **MathML** instead of the
GIF; screen-readable, no library), "Welcome!" and "Exercises" as transcript sections in place of
the MP3 links, the applet, the quiz, and credits.

## Phases

### Phase 0: Reference capture (done 2026-11-17; see CLAUDE.md "Ground-truth tools")
1. **Original files → `reference/`: Jon saves them from Chrome** using the exact links in
   [DOWNLOAD_LIST.md](DOWNLOAD_LIST.md) (27 required, 16 optional). Cloudflare blocks scripted
   downloads, and spoofing a browser is not allowed.
2. **Ground truth for "near-perfect": run the originals in `appletviewer`.** Temurin JDK 8
   (8.0.512.9) was installed 2026-11-17 with winget, **files only** (`ADDLOCAL=FeatureMain`): no
   PATH entry, no JAVA_HOME, no `.jar` association, no browser plugin. Call it by full path:
   `C:\Program Files\Eclipse Adoptium\jdk-8.0.512.9-hotspot\bin\appletviewer.exe` (and `javap.exe`).
   Screenshot each applet to get the exact GridBag panel sizes, which can't be read from the
   source alone. **Uninstall when the project's reference work is done**
   (`winget uninstall EclipseAdoptium.Temurin.8.JDK`; Jon prefers not to keep Java installed).
3. **DT source.** Checked: `DTConvolve.jar` has no `.java`, only 10 classes in package
   `DTConvolve` (DTConvolve, DualGraphPanel, GraphPanel, InputGraphPanel, MyMouseGraphListener,
   MyMouseListener, MySimpleMouseListener, OutputGraphPanel, Signal, SignalClickListener). Use
   `javap -c -p` to transcribe. No source is posted for the 1997 DT original either.
4. **Transcripts with the existing faster-whisper:** system Python 3.13
   (`C:\Users\Jon\AppData\Local\Programs\Python\Python313\python.exe`, **not** `py`, which
   defaults to 3.14), faster-whisper 1.2.1, CUDA (1 GPU), model `large-v3` already cached in the
   Hugging Face cache. Four MP3s (CT and DT, a welcome and an exercises clip each, about 10 min
   total). Claude cleans up the math wording, then Jon listens once and checks the transcript
   against the audio.

### Phase 1: CT port, faithful (first port done 2026-11-17; hands-on check pending)
- **Geometry:** the same 480×600 applet layout, with panel rectangles measured from the
  appletviewer screenshot. Drawn on canvases at that logical size, sharp on high-DPI screens, with
  the whole applet scaled to a readable size on a 1080p laptop (the sibling sim's "stage" idea).
  The unscaled original is about 5 cm wide on a modern laptop.
- **Model = the Java, transcribed class by class** (`Signal`, `ConvSignal`, `SigPanel`,
  `MouseSigPanel`, `SigButton`, `SigControls`, `ConvPanel`, `ConvSigPanel`), keeping names so
  the code can be diffed against the original. Same sample grid (one sample per original pixel),
  presets, Riemann sum, `dx = 2π/W` and scale factors.
- **Behavior to reproduce:** main x/h panels start empty; buttons are thumbnails of their signal;
  click/drag drawing with linear interpolation, first and last samples locked; click on the
  conv panel sets t, dragging moves it; flipped x slides over a fixed h; integrand panel;
  y(t) is revealed only at visited t, with a dot at the current point; editing x or h clears the
  lower panels; the equation in the y panel; colors (blue x, red h, green "decay" button);
  no time-axis numbers (the original has none).
- **Input:** Pointer Events, so mouse, pen and touch all work without extra code.
- **Known deliberate deviations** are logged in [QUIRKS.md](QUIRKS.md). Changed from this plan:
  the port keeps the original's **int truncation exactly** (not floats), which made bit-exact
  tests against the original's arrays possible. Fonts are the browser's Arial.
- Anything in the original that looks like a bug: **keep it** and list it for Jon and the course professor.
  Don't fix it silently.

### Phase 2: DT port (first port done 2026-11-17; hands-on check pending)
Same approach, transcribed from the `javap` output (no source survives) and checked against
DtProbe's values and captures. Quirks and deviations: [QUIRKS.md](QUIRKS.md).

### Phase 3: Verification (`py -m unittest discover -s tests -v`, stdlib only)
- `test_model.py`: a Python transcription of the Java math (int arithmetic, exactly as written)
  plus analytic checks: pulse∗pulse is a triangle of known peak and width; pulse∗decay has a
  closed form; double pulse; the DT equivalents are exact sums.
- `test_html_portable.py`: one self-contained file, no network, no syntax newer than Safari 14.
  Headless Chrome/Edge loads it from `file://` and the `#err` bar must be empty.
  **JS-vs-Java parity without Node** (Node isn't installed): the page's `#selftest` mode runs
  the JS model on every preset pair, writes JSON into the DOM, and `--dump-dom` hands it to
  Python for comparison against the reference transcription.
- Visual: headless screenshots of the port next to the appletviewer screenshots, same preset
  and t; Jon eyeballs them.
- Jon and the course professor hands-on checklist on a Windows and a Mac laptop (written at the end of Phase 1).

### Phase 4: Accessibility, best effort (no change to how it looks)
`lang`, headings, real `<button>`s for the presets (canvas thumbnails inside), keyboard focus
on the conv panel with ←/→ to step t, an `aria-live` text readout of t and y(t) for screen
readers (visually hidden, so the faithful look is unchanged), MathML equations, transcripts
(the text alternative for the audio), and a contrast check of the original colors on white.

### Phase 5: Publish (after permission)
README in the sibling's style (credits block at the top, screenshots, "Run it in your browser",
things to try (taken from the transcribed Exercises), offline ZIP instructions, tests), a LICENSE
per the permission terms, a public repo, then Pages enabled with legacy build from `main` /.
Students get the README URL.

## Credits (on every page header + full list in About)
Header line, e.g.: *"The Joy of Convolution" by Steven Crutchfield, Johns Hopkins University
(1996). Restored for modern browsers, 2026.* The full list, from the JHU site:
- CT applet: **Steven Crutchfield**, Fall 1996
- DT applet: original **Steven Crutchfield**, Summer 1997; update **Michael Ross**, Fall 2001
- Project director: **Wilson J. Rugh**, JHU Signals, Systems, and Control demonstrations, 1994–2003
- Narration: **Cherie Weinert**
- Site page design: Mark Nesky (1998)
- Support: National Science Foundation; Kenan Fund, Center for Educational Resources and
  E.J. Schaefer Chair at Johns Hopkins
- Premier Engineering Courseware of 2001
- Original site: https://pages.jh.edu/signals/ (link)
- Port: electricyoshi, for a Seattle Pacific University course (wording TBD)

## Open items for Jon
- Done: files saved (2026-11-17), including the 10 DT button GIFs (fetched via Claude-in-Chrome).
- Check the cleaned-up narration transcripts on both pages against the audio (tidied 2026-11-17).
- Done: repo created and pushed 2026-11-17 (public dev repo, as approved).
- Run [CHECKLIST.md](CHECKLIST.md) on a Windows and a Mac laptop (both pages).
