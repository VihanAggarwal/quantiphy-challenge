# simulation_0068 notes

Scene: top-down Blender view of a 4-way intersection, 2160x1080, 24 fps, 72 frames. White van drives straight north
(up) from rest with constant acceleration (prior: 4 m/s^2). Yellow/peach sedan turns right from the south arm and
drives east at a constant speed.

## Scale
- Clean background = frame 71 with the van/sedan areas patched from frame 0. Masks = |frame - bg| > 25.
- Van tracks: silhouette centroid gives a quadratic with A = 161.9 px/s^2 (rms 0.5 px). Sub-pixel edge tracks:
  hood leading edge A = 162.5 px/s^2, rear roof edge A = 165.4 px/s^2 (frames 2-43). Starts from rest around frame 1.
- The difference between the two edges, the change in silhouette length with position, the visible van side and
  rear faces, and the lamp-post radial lines (top/base radius ratio 1.06, consistent at all radii, so the nadir is at the image
  centre) all point to a pinhole camera looking straight down from roughly 50-80 m. So the scale depends on height:
  about 40.65 px/m at hood height (about 1.2 m, = 162.5/4), about 39.8 px/m at the ground and about 41.1 px/m at mirror height.
- The perspective corrections on the answers are 1-2%, below the 5% tolerance.

## Answers
- Q33 yellow speed at 2.5 s: centroid speed is constant at 162.5 px/s from frame 40 to 71 (backward diffs and
  quadratic fits); the heading is almost straight east at frame 60. With 40.6 px/m at the centroid height this is 4.00 m/s.
  Confidence high.
- Q34 yellow length: 217.5-218 px on luma edges and 220-222 px on chroma/thr25 edges. This holds at frame 0 (heading N) and
  frames 60-71 (heading E). About 219.5 px / 40.35 px/m = 5.44 m. Confidence medium-high.
- Q35 yellow width: 80.5-82 px on luma and 82-84 px on chroma. The mirrors are flush, adding about 1 px. About 81.5 px, giving 2.02 m. Confidence medium-high.
- Q36 white van width: mirror to mirror is 97.5-99 px (2.37-2.44 m at mirror-height scale). The body alone is about 1.93-2.13 m
  (the right side wall is visible from parallax). The answer, 2.32, is hedged a little toward the body width because it is
  unknown whether the ground-truth bbox includes the mirrors (it probably does). Confidence medium.
- Q37 white van length: bumper to bumper near the nadir is 240-243 px (bbox at frames 50-54 is 239-240, hood edge plus a
  bumper of about 7 px is about 243). At about 40.1-40.65 px/m this is 5.9-6.06 m, so the answer is 6.0. Confidence medium-high.

Scripts: track.py, track2.py, bg.py, edges.py, edgefit.py, yspeed.py, widths.py, ychroma.py, vanlen.py, prof*.py
