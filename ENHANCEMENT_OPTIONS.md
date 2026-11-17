# Joy of Convolution: enhancement options

*For the course professor. Prepared 2026-11-17.*

The first release will be a near-exact copy of Steve Crutchfield's *Joy of Convolution* applets
(continuous-time and discrete-time, Johns Hopkins University). It will run in any modern browser
with nothing to install. **Nothing below is being built yet.** Each option would be an opt-in
control, and the original view stays the default. Please mark the ones worth adding, or say
none are needed.

## How the original works (for reference)
Students choose or draw x(t) and h(t): presets are *pulse*, *double pulse* and *decay*, or they
draw with the mouse. They click a value of t, and h(v) appears with the flipped and shifted
x(t − v) on top of it. Dragging t slides x along. Below that, the product h(v)·x(t − v) is
plotted, and y(t) is traced out, but only at the values of t the student has visited. The axes
have no numbers, only ±1 marks.

## At a glance
Effort: **S** = about a day, **M** = a few days, **L** = a week or more.

| # | Option | What students gain | Effort |
|---|---|---|---|
| 1 | Numbered time axis | Read off widths, delays and where y(t) starts and stops | S |
| 2 | Shade the integrand's signed area | See y(t) *as* the area: positive and negative parts in two colors | S |
| 3 | Live t and y(t) readout | Check hand calculations against exact numbers | S |
| 4 | Play button that sweeps t | Watch the flip-and-slide as a smooth animation; good on a projector | S |
| 5 | Show all of y(t) at once | Skip the tracing when the shape, not the process, is the point | S |
| 6 | More preset signals | Cover the standard textbook cases without hand drawing | M |
| 7 | Adjustable presets | Change width, delay, decay rate or height and see y(t) respond | M |
| 8 | Predict, then reveal | Sketch y(t) first, then compare with the true result | M |
| 9 | Flip h instead of x | Show that x∗h = h∗x | S |
| 10 | Shareable links | A link opens the sim with chosen signals already loaded (homework, exams) | M |
| 11 | Interactive quiz | The original 5-question quiz with instant feedback, not a PDF | M |
| 12 | Projector / full-screen layout | Readable from the back of a lecture hall | M |
| 13 | CT and DT side by side | Connect the integral and the sum, sample by sample | L |
| 14 | Phone and tablet layout | Use on a phone. Laptops are the current target | M |

## The options in more detail

### Seeing the math
1. **Numbered time axis.** The original marks only the origin and ±1, so "the pulse is π/2 wide"
   can't be read off the screen. Adding numbers (in the original's units, or rescaled to 0–1–2 s)
   lets students check width-of-y = width-of-x + width-of-h, and similar rules.
2. **Shade the integrand's signed area.** Fill the area under h(v)·x(t − v): one color above
   zero, another below. y(t) is that net area. This is probably the strongest single addition
   for understanding.
3. **Live readout.** Show "t = 1.20, y(t) = 0.83" next to the plot. Useful for checking
   hand-worked problems.

### Exploring
4. **Play button.** Sweeps t from left to right at an adjustable speed, with pause and step.
   The original needs a steady mouse drag.
5. **Show all of y(t).** A checkbox that draws the whole output at once. The original's
   reveal-as-you-go stays the default, because the tracing is part of the lesson.
6. **More presets:** step, ramp, triangle, a narrow pulse (an impulse stand-in), a sinusoid,
   exponential growth. The quiz already asks about step and ramp inputs, which students currently
   have to draw.
7. **Adjustable presets:** sliders for width, delay, decay rate and amplitude, so "what happens
   to y(t) if the pulse gets twice as wide?" takes one drag.
9. **Flip h instead of x.** A toggle for which signal is flipped and slid. The same y(t) appears
   either way.

### Active learning and assessment
8. **Predict, then reveal.** The student sketches their predicted y(t) with the mouse. Then the
   true y(t) is drawn over it in a different color.
11. **Interactive quiz.** Turn the original multiple-choice quiz into a page with instant
   feedback and a short explanation for each answer. **Needs an answer key**: the original PDF
   doesn't have one. More questions could be added.
10. **Shareable links.** The instructor sets up signals and copies a link. Students open it and
   get exactly that setup. Handy for homework ("open this link and explain why y(t) is
   negative at t = 1").

### Classroom and devices
12. **Projector layout.** Bigger lines and type, filling the screen. Our other course simulation
   (the feedback phase-shift sim) has one.
13. **CT and DT side by side.** One page with both versions, so the convolution sum can be seen
   as the sampled version of the integral.
14. **Phone/tablet layout.** Touch already works. This would re-flow the page for narrow
   screens.

## Questions for you
- Which options, if any, should be added after the faithful copy? A top three is enough to start.
- For a numbered axis: keep the original's units (each plot spans about 2π), or rescale to round
  numbers like seconds?
- Do you have, or want us to draft, an answer key for the two original quizzes?
- Should the narration transcripts ("Welcome" and "Exercises") be shown on the page by default,
  or tucked behind a "Show transcript" link?

*The original applets are the work of Steven Crutchfield (CT 1996, DT 1997; DT updated by Michael
Ross, 2001), in the Johns Hopkins Signals, Systems and Control demonstrations project directed by
Wilson J. Rugh, with narration by Cherie Weinert and support from the National Science
Foundation.*
