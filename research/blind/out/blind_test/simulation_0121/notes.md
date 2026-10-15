# simulation_0121 - Newton's cradle (2D sim, 1920x1080, 80 frames @30 fps)

Questions: speed of the left (first) ball at 0.5 s (frame 15) and at 1.0 s (frame 30). Prior: ball diameter = 2 m.

## Observations
- Fixed camera, fronto-parallel view of the cradle. Video frame 1 is a glitch frame (balls dropped); ignored.
- Ball 1 is released at about frame 1, swings down a ~40 deg arc, and hits ball 2 between frames 27 and 28.
  After that it bounces back slowly (small pendulum swing: turns at frame ~54, back by frame 79).

## Tracking
- Background = median of late frames, with an early-frame patch where the ball rests later. Silhouette circle fit
  (sil.py), then a limb-edge tracker (limbtrack.py): sub-pixel half-max edge crossings on 720 rays,
  rejecting rays without clean background (arc occlusion, neighbouring balls), then a robust circle/ellipse fit.
- A damped pendulum ODE (pivot, L, theta0, release time, omega, damping) fits the limb track for frames 2-27
  with rms 0.12-0.15 px. Its chord 14->15 is 16.09 px (dx 14.16, dy 7.64). Direct limb chords: 16.00 / 16.12.
  The undamped model gives 16.02.
- After the collision (frames 28-40), the limb track moves 0.91-0.93 px/frame. A sinusoid fit to frames 29-79
  gives 0.90 px/frame at 29->30, and annulus ECC gives 0.91-0.97.

## Scale
- The ball images are ellipses: perspective stretches them along the radial direction, plus about 3% extra
  vertical stretch, either from the pixel aspect or from the ball shape along the string.
- Horizontal tangential diameter:
  - ball 3 (near the image centre column) is 160.6-161.4 px wide;
  - ball 1 at rest is 162.2 px wide, about 160.5-161 px after the perspective correction;
  - ellipse minor axes are 161-164 px.
- Used D = 161 px for 2 m, i.e. 0.01242 m/px.

## Answers (backward difference x 30 fps)
- 262 (t=0.5 s): 16.05 px/frame x 30 x 2/161 = 5.98 m/s (range about 5.94-6.02). Confidence: good (about +-3%).
- 263 (t=1.0 s): 0.91 px/frame x 30 x 2/161 = 0.339 m/s (range about 0.33-0.36). Confidence: moderate.
  The ball barely moves after the collision, so the true value depends on how much it rebounded.
