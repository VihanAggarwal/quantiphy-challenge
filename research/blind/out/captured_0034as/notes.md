# captured_0034as — notes

Lab (segmented, SAM2-demo) video, 1280x720, 49 frames, container 24 fps. Static camera (soccer ball / bag
template drift < 0.3 px). Two tennis balls are held at the table edges, pushed, roll toward the centre,
collide around frame 37 and bounce back; soccer ball and pencil bag static.

## Time base (important)
Both balls show a ~2x displacement step between frames 35->36 (L 23->41 px, R 22->46 px), i.e. a dropped
frame: the clip is a 25 fps original resampled to 24 fps (ffmpeg fps filter, timeline preserved; drops near
output frames ~12 and ~36). So output frame 29 = original frame 30 = t 1.20 s (depth-label frame), output 30 =
1.24 s, 31 = 1.28 s, 32 = 1.32 s, 33 = 1.36 s. Lab GT forward difference at 25 fps -> v(1.2) = P(f30)-P(f29) x 25;
v(1.3) = mean of steps f31->32 and f32->33, x 25.

## Scale
Ball sizes (halo extents, gradient ellipse fits, visual) vs labels: L 72.5-74 px at 0.706 m, R 63-64.5 px at
0.776 m -> f ~ 745 (L alone 760-769, R alone 713-736); lab nominal 711; surface-depth semantics would give ~781.
Used f = 745 (geometric middle of the hypotheses) with depth labels as range to centre.

## Depth along the track
Table surface is not planar (balls descend toward the middle: R keeps constant size while moving to the image
centre yet barely rises), so depth comes from ball size ratios, not a ground plane. L ball shrinks ~1.4 %/frame
(f29->f35: 76.3->69.2 px halo, ellipse b 36.8->33.4, template scale 0.905) -> range +1.0 cm/frame;
R ball size constant (range ~0.776). End: L ~0.84 m, R ~0.80 m; R at rest ~0.81 m, L at rest ~0.706 m.

## Velocities (template-matched pixel steps)
L: 28->29 37.7, 29->30 32.1, 30->31 26.0, 31->32 24.5, 32->33 24.0 px (sliding->rolling deceleration).
R: ~25.4 px/frame at 1.2 s, ~24.4 at 1.3 s.
- 2714 L v(1.2) = 71 cm/s (3D incl. radial ~25 cm/s; f=711 -> 73, f=781 -> 69)   confidence medium
- 2715 R v(1.2) = 62 cm/s                                                       medium
- 2719 L v(1.3) = 60.3 cm/s                                                     medium
- 2720 R v(1.3) = 60.6 cm/s                                                     medium

## Sizes
- 2718 soccer ball: minor-axis 142 px at 0.894 m -> 17.0 (centre) / 17.9 (surface / f=711) -> 17.5 cm   medium
- 2717 pencil bag length: 131 px (543.5-675) at ~1.04-1.08 m -> 18.3-19.8 -> 18.8 cm                       medium-low
- 2716 pencil bag height: ~47 px (425.5-473) -> 6.5-7.0 -> 6.7 cm                                          medium-low

## Total distance (3D path rest -> contact (f37) -> end (f48))
- 2721 L: rest->contact ~27.3-27.6 cm + rebound ~8.3 cm = ~36 (excluding 1 cm pull-back before push);
  shaded to 35.3 for sparse-click GT                                                                      low-medium
- 2722 R: rest->contact ~38.6 cm + rebound ~4.5 cm = ~43; shaded to 42.6                                 low-medium
