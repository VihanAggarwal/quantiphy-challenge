# simulation_0307 - plane flying away (3D sim, static camera, 2560x1440 @24fps, 72 frames)

Questions: 1481 length (m), 1482 width (m), 1483 displacement 0.5-1.0 s (m). Prior: speed 22.16 m/s. Depth (origin): 102.6664 m at t=1, 121.8263 m at t=2.

## Motion
- Median-background segmentation plus about 100 KLT feature tracks (forward-backward checked) on the plane.
- Every track is a straight image line (rms 0.1-0.3 px). Each one fits a constant-velocity projective (Mobius) model with rms 0.1-0.4 px.
- All tracks converge on one focus of expansion, FOE ~(-755,-480). That means pure translation with no rotation.
- 1/rho to the FOE is linear in t, so acceleration is about 0 (|Az/Vz| < 0.5%/s).
- **Q1483:** constant velocity along a straight line, so the displacement is 22.16 x 0.5 = **11.08 m**. Confidence: high.

## Camera and convention
- Span direction: I detected the wingtip-fin apexes (a mirror pair) in every frame. The lines joining them meet at VP_S ~(8340,-491).
- VP_S and the FOE lie on the same image row, so camera roll is 0 and the flight is level.
- If the heading equals the velocity (span perpendicular to V), then f = 3590 px. Using the q-based 3D span direction instead gives 90 deg at f~3500.
- Range convention plus FOE: Vz from (d2-d1) is ~18.4-18.5, which gives f ~3460-3700 depending on where the origin projects. The Z convention would need f=4065, a 5 deg heading offset and an origin outside the body, so I rejected it.
- I used f ~3580 px (horizontal FOV ~39 deg).
- Q-based depth check: the per-track Mobius q gives Vz/Z0, so Z = Vz/q with Vz = 22.16·cos(angle(V, optical axis)) ≈ 18.5. This puts the plane's body centre about 5.5 m deeper than the d1 origin range. The origin seems to sit at the rear of the model (or there is a time offset). Sizes therefore use the self-consistent q-based scale, not d1.

## Sizes (3D reconstruction in a world frame: fwd = V, span = S, up = U)
- Wingtip fin apexes are 17.45 m apart (f-dependence: 17.9 at f=3400, 17.0 at f=3800). The check against the changing image separation over time is consistent.
- I added about 0.3-0.4 m for the wingtip rails and lower fins, giving **width ≈ 17.8 m** (span). Confidence: medium.
- The left boom runs tip to tip from fore +4.3/+3.7 to -5.5/-5.9, so 9.6-9.85 m horizontally. It is the longest fore-aft element: the canopy and the nose-side probe stay within it, and the nozzles/ventral fins end around -4.2 to -4.8.
- **Length ≈ 10.0 m** (nose-to-tail, fore-aft). Confidence: medium-low.
- Caveats:
  - The booms are inclined about 8.8 deg nose-up.
  - If the dataset's "length" means the larger horizontal dimension, then length and width swap (17.8 vs 10.0).
  - The world AABB alignment is assumed to match the body axes.
