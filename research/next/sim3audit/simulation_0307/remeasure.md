# simulation_0307 - independent re-measurement of qid 1481 (plane length)

I did not read anything else in this folder. My scripts and frame crops are in `indep_b/`. I read only the original agent notes for 0303, 0305, 0307 and 0284-0287.

## Answer
- **1481 length = 14.4 m.** Confidence: medium-high.
- The current answer, 10.0 m, is wrong.
  - It runs from the pod noses to the pod tails only.
  - It misses the central tail section: the tail cone, the canted tail planes and the ventral fin.
  - That tail section ends about 5 m behind the pod tails.

## Key facts established
- 0303 (V3SX), 0305 (V3SS) and 0307 (V3SC) are the same render with different backgrounds.
  - The plane pixels, KLT tracks and FOE are identical.
  - Frame 0 duplicates frame 1, and the timing is uniform from frame 1 onward. I checked per-frame time residuals: all are below 0.07 frame.
- The motion is pure translation. FOE is (-765, -483) px, and the 1/rho-linear model fits every track.
- Per-point depth comes from a plane-sweep over 70 frames. I swept the patch scale about the FOE, giving Z(i) = vzf * (1/q + i).
  - I did this on 0303 (silhouette against sky) and on 0305 (texture). The two clips agree to within 0.1-0.3% in q.
- Focal length:
  - Mirror pairs (fin tops, pod noses, pod tails) perpendicular to V give f = 3566-3636.
  - Ranges plus speed plus FOE give Vz = d2·cos(theta2) - d1·cos(theta1) = 18.49 m/s, so cos(alpha) = 0.834, so f = 3589.
  - Adopted f = 3590 (the Blender 50 mm default would be 3556). Roll is 0 and flight is level (dUp of mirror pairs is about 0).
  - The Euclidean range convention is consistent. A Z-depth convention would need f of about 4090, which contradicts the symmetry.
- Body frame (fore = V). In N=24 units relative to the fin-top midpoint:
  - pod noses at fore +5.37 (L and R agree);
  - pod tails at -4.5;
  - wingtip fin tops at 0.0 (span ±8.7);
  - canopy at +2.8.
  - The ventral fin trailing edge is on the centreline (span -0.2) at fore -9.55, and -9.6 to -9.85 near the tail-cone end.
  - In frame 1 that fin projects right under the right pod's tail. Parallax over the clip separates them: by frame 36/71 the fin sits between the nozzle and the right pod. This is what fooled the earlier 10 m measurement.
- Fore-aft extent: 14.93-14.98 in N=24 units, or 14.33-14.38 in N=25 units. It is insensitive to f (±0.06 for f 3550-3640) and to the FOE.

## Routes
1. **Motion parallax plus speed prior.** Length is 14.93 m if the render is 24 fps and 14.33-14.38 m if it is 25 fps.
2. **Mirror-symmetry geometry plus depth_info anchor.** This uses no q for the geometry. The scale is set so that the AABB centre is at the stated range d1. Result: 14.2-14.35 m.
   - Length / fin-top distance is 0.861, against 0.857 from route 1.
3. **fps / origin check.** If the origin is the AABB centre, d1 and d2 are both matched (rms 0.01-0.06 m) with an implied N of 25.3-25.7.
   - Under N=24 the origin would have to sit about 5 m behind the AABB centre, near the tail fin (rms 0.2 m). So N=25 is favoured.
   - The dataset fps field also says 25 for 0303 and for all four 2D siblings 0284-0287.
4. **Same plane in the 2D siblings, my own template tracks.** Each point is scaled at its own depth with X = v·(x - c)/s.
   - Top view 0284: pod noses (34.45 px/frame) to tail-cone tip (34.76 px/frame) = 14.40 m at 25 fps.
   - Side view 0285: near pod nose (43.79) to tail-cone tip (41.37) = 14.28 m at 25 fps.
   - These agree with route 1 at the same frame rate. The 2D clips also show that "length" in this family means fore-aft (pod noses to tail), and that width means span.

## Residual risk
- The main risk is the frame-rate ambiguity. If the scene is really 24 fps, the truth is about 14.9-15.0, and 14.4 is still within 4%.
- A world AABB that is not aligned with the body axes would make the length larger.
