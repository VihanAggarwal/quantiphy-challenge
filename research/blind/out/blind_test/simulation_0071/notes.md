# simulation_0071 (S2MS, top-down nadir view of an intersection, 2160x1080, 72 frames @24 fps)

Scale: prior car length 5.44 m. Car silhouette measured by luminance half-max edges (thr 180-190) on axis-aligned
frames (0-3 vertical, 66-71 horizontal): length 217.4 px (216.9-217.9), max width 79.0 px (78.0-79.6; widest at rear
wheel arches, typical body 77 px). Scale = 5.44/217.4 = 0.02502 m/px. Chroma-only mask overestimates (bleed), not used for sizes.
Perspective: lamp-pole parallax ~6% of radial distance -> camera very high (H >> 10x object heights); height effects < 1%.
Frames 0 and 1 are identical (duplicate start frame); motion otherwise uniform.

- Q45 width: 5.44 * 79.0/217.4 = 1.98 m (range 1.97-1.99). Car is axis aligned at start and end, so AABB width = car width. Confidence: medium-high.
- Q44 car speed @2.5 s (frame 60): bg-diff+colour mask, centroid / hull centroid / rect centre tracks; quadratic fits over
  frames 50-70 give 6.78-6.86 px/frame (use 6.81) -> 6.81*24*0.02502 = 4.09 m/s. Yaw rate at f60 ~0.12 rad/s, so origin
  offset along car axis changes |v| negligibly. Confidence: high.
- Q46 pedestrian speed @1.0 s (frame 24): white-shirt torso centroid (bg diff + lum>205), linear fits over 12-36 frame windows
  and 24-frame chords: 2.04-2.06 px/frame (whole-clip mean 2.05) -> 2.058*24*0.02502 = 1.24 m/s. Confidence: high-medium.
