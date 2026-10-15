# simulation_0082 (S2MX, 24 fps, 72 frames, 1920x1080)

Scene: a nadir (top-down) camera over a uniform grey ground plane, so the video is planar. Two identical-looking Tesla Cybertruck models, yellow (top, y~400) and black/white (bottom, y~540), drive left at constant speed. Frames 0 and 1 are identical, and motion starts after frame 1.

## Method
- Background is a flat grey (158) with soft shadows. Each car's front and rear edges were found per frame (rows through the car body) as the sub-pixel half-level crossing of the colour distance from the local background. Mirror-tip top and bottom extents came from column scans started in the gap between the cars (scripts work/both.py, work/mirror2.py).
- Perspective check: the cars' pixel speed is uniform across the frame (BW 15.89 px/frame on the right and 15.87 on the left), so the ground plane is fronto-parallel. The apparent car length has a V-shape against image x: about 302 px when the car is centred under the camera and about 311 px at the right edge, because the front and rear faces show when the car is off-axis. I therefore take the scale from the centred (minimum) length, where the silhouette ends are the AABB-extreme points.
- Scale: yellow centred length is about 303.3 px, which equals 5.67 m, giving 0.018695 m/px at the height of the extreme points. Speeds and distances use the motion of those same rigid-body points, so the result does not depend on the origin height.
- BW and yellow compared at the same image positions: BW is 0.9965 x yellow, so 5.65 m. Both cars appear to be the same model.
- Widths are mirror tip to mirror tip (the AABB includes the mirrors): yellow 131.7 px and BW 131.5 px, which gives 2.46 m (the real Cybertruck with mirrors is 2.41 m). The body alone, without mirrors, is about 105 px, or about 1.97 m.
- Velocities from linear fits of the centres (residuals 0.3 px): yellow 11.335 px/frame, giving 5.09 m/s; BW 15.856 px/frame, giving 7.11 m/s.
- Distance between centres: dy is 139.5 px (mirror-midpoint and body-midpoint estimates are 139.9 and 139.0). dx at frame 1 is 1.55 px, plus 4.521 px/frame. At t=1.0 (frame 24), dx = 105.3 px (measured 104.5), giving a distance of 174.8 px = 3.27 m. At t=2.0 (frame 48), dx = 214.1 px, giving 255.5 px = 4.78 m.

## Answers and confidence
- 88 yellow width: 2.46 m. Medium confidence; if the ground truth excludes the mirrors it would be about 2.0.
- 89 BW length: 5.65 m. High confidence.
- 90 BW width: 2.46 m. Medium confidence; same caveat as 88.
- 91 distance at 1.0 s: 3.27 m. Medium-high confidence.
- 92 distance at 2.0 s: 4.78 m. Medium-high confidence.
- 93 yellow speed: 5.09 m/s. High confidence.
- 94 BW speed: 7.11 m/s. High confidence.
