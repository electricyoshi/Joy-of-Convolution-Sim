# Original files to save into `reference/`

Every link below was checked on 2026-11-17 (HTTP 200, size shown). The site blocks scripted
downloads, so save them from Chrome. Keep the **exact filenames**. `reference/` is gitignored:
these files are "all rights reserved" by JHU and are for local reference only.

**How to save each kind:** `.class`, `.jar` and `.rm` usually download as soon as you open them.
For `.html` and `.java`, open the link and press Ctrl+S (for HTML choose "Webpage, HTML only").
MP3s and PDFs open in a player or viewer: use its download button, or right-click the link →
"Save link as…".

## 1. Continuous-time → `reference\ct\` (required)
| # | Link | Size |
|---|---|---|
| 1 | https://pages.jh.edu/signals/convolve/index.html | 3.8 KB |
| 2 | https://pages.jh.edu/signals/convolve/Convolve.java | 20.9 KB |
| 3 | https://pages.jh.edu/signals/convolve/Convolve.class | 1.9 KB |
| 4 | https://pages.jh.edu/signals/convolve/ConvPanel.class | 5.0 KB |
| 5 | https://pages.jh.edu/signals/convolve/ConvSigPanel.class | 2.7 KB |
| 6 | https://pages.jh.edu/signals/convolve/ConvSignal.class | 1.9 KB |
| 7 | https://pages.jh.edu/signals/convolve/ControllableSignal.class | 0.9 KB |
| 8 | https://pages.jh.edu/signals/convolve/MouseSigPanel.class | 1.8 KB |
| 9 | https://pages.jh.edu/signals/convolve/SigButton.class | 1.5 KB |
| 10 | https://pages.jh.edu/signals/convolve/SigControls.class | 1.4 KB |
| 11 | https://pages.jh.edu/signals/convolve/SigPanel.class | 2.5 KB |
| 12 | https://pages.jh.edu/signals/convolve/Signal.class | 3.0 KB |
| 13 | https://pages.jh.edu/signals/convolve/TransparentFilter.class | 0.5 KB |
| 14 | https://pages.jh.edu/signals/convolve/conv.gif | 0.5 KB |
| 15 | https://pages.jh.edu/signals/convolve/conv.jpg | 2.5 KB |
| 16 | https://pages.jh.edu/signals/convolve/welcome.mp3 | 1.77 MB |
| 17 | https://pages.jh.edu/signals/convolve/exercises.mp3 | 2.99 MB |
| 18 | https://pages.jh.edu/signals/convolve/Quizconvolution.pdf | 28.9 KB |

## 2. Discrete-time (2001 version, the one the page runs) → `reference\dt\` (required)
No Java source is posted for this one. `DTConvolve.jar` holds only compiled classes; the JDK
disassembles those.
| # | Link | Size |
|---|---|---|
| 19 | https://pages.jh.edu/signals/discreteconv2/index.html | (page) |
| 20 | https://pages.jh.edu/signals/discreteconv2/DTConvolve.jar | 20.8 KB |
| 21 | https://pages.jh.edu/signals/discreteconv2/conv.gif | 0.5 KB |
| 22 | https://pages.jh.edu/signals/discreteconv2/welcome.mp3 | 1.83 MB |
| 23 | https://pages.jh.edu/signals/discreteconv2/exercises.mp3 | 2.81 MB |
| 24 | https://pages.jh.edu/signals/discreteconv2/Quizdtconvolution.pdf | 28.0 KB |

## 3. Shared → `reference\shared\` (required)
| # | Link | Size |
|---|---|---|
| 25 | https://pages.jh.edu/signals/index.html | 16.5 KB |
| 26 | https://pages.jh.edu/signals/images/demo6.gif | 2.0 KB |
| 27 | https://pages.jh.edu/signals/images/return_arrow.gif | 0.1 KB |

## 4. Optional: Crutchfield's 1997 original DT applet → `reference\dt-1997\`
Michael Ross's 2001 update replaced this one. It's useful for credits and history, and to see
what Ross changed. Its narration is in RealAudio (`.rm`), which ffmpeg can usually convert.
| # | Link | Size |
|---|---|---|
| 28 | https://pages.jh.edu/signals/discreteconv/index.html | 2.4 KB |
| 29 | https://pages.jh.edu/signals/discreteconv/Convolve.class | 2.1 KB |
| 30 | https://pages.jh.edu/signals/discreteconv/ConvPanel.class | 5.8 KB |
| 31 | https://pages.jh.edu/signals/discreteconv/ConvSigPanel.class | 2.8 KB |
| 32 | https://pages.jh.edu/signals/discreteconv/ConvSignal.class | 1.5 KB |
| 33 | https://pages.jh.edu/signals/discreteconv/ControllableSignal.class | 1.0 KB |
| 34 | https://pages.jh.edu/signals/discreteconv/MouseSigPanel.class | 2.1 KB |
| 35 | https://pages.jh.edu/signals/discreteconv/SigButton.class | 1.8 KB |
| 36 | https://pages.jh.edu/signals/discreteconv/SigControls.class | 1.5 KB |
| 37 | https://pages.jh.edu/signals/discreteconv/SigPanel.class | 2.7 KB |
| 38 | https://pages.jh.edu/signals/discreteconv/Signal.class | 4.0 KB |
| 39 | https://pages.jh.edu/signals/discreteconv/TransparentFilter.class | 0.5 KB |
| 40 | https://pages.jh.edu/signals/discreteconv/conv.gif | 0.5 KB |
| 41 | https://pages.jh.edu/signals/discreteconv/rafile.gif | 0.6 KB |
| 42 | https://pages.jh.edu/signals/discreteconv/welcome.rm | 228 KB |
| 43 | https://pages.jh.edu/signals/discreteconv/exercises.rm | 352 KB |

Not needed: the pages also load `dcs_signals.js` and `dcs_tag2.js` (old analytics scripts,
now 404), and the narration links point to the old `www.jhu.edu/signals/...` host; the
`pages.jh.edu` links above are the same files.

## Status
2026-11-17: all 27 required files saved and checked (sizes match the server, file types valid,
JAR opens cleanly, `Convolve.java` complete at 1548 lines). The three HTML pages were saved as
"Webpage, Complete" under their page titles (`The Joy of Convolution.html`, etc.) with `_files/`
folders; that's fine for reference. `Convolve.java` was saved as `.java.txt` and renamed.
The optional 1997 DT files (section 4) were not saved.

## 5. Missed the first time: DT button images → `reference\dt\` (required)
Found in the `javap` disassembly: the DT applet loads its preset-button faces from its own folder.
All 10 checked 2026-11-17 (HTTP 200, about 0.1 KB each). Missing them → blank buttons in appletviewer.
| # | Link |
|---|---|
| 44 | https://pages.jh.edu/signals/discreteconv2/x_rightpulse.gif |
| 45 | https://pages.jh.edu/signals/discreteconv2/x_squarewave.gif |
| 46 | https://pages.jh.edu/signals/discreteconv2/x_exponential.gif |
| 47 | https://pages.jh.edu/signals/discreteconv2/x_impulse.gif |
| 48 | https://pages.jh.edu/signals/discreteconv2/x_clear.gif |
| 49 | https://pages.jh.edu/signals/discreteconv2/h_rightpulse.gif |
| 50 | https://pages.jh.edu/signals/discreteconv2/h_squarewave.gif |
| 51 | https://pages.jh.edu/signals/discreteconv2/h_exponential.gif |
| 52 | https://pages.jh.edu/signals/discreteconv2/h_impulse.gif |
| 53 | https://pages.jh.edu/signals/discreteconv2/h_clear.gif |
