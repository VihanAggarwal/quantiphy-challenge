# simulation_0134 — toaster pops toast (S2MC, 24 fps, 60 frames, 1080x1920)

## Scene / camera
- Fixed, level camera (cabinet gap lines exactly vertical -> zero pitch/roll; horizon taken at cy=960).
- Toaster on counter, front face toward camera; one slice of toast in the FRONT slot (toast occludes the whole
  slot-plate top band at rest; the plate's front lip stays in front of it).
- Plate side-edge width ratio (213.5/203.5=1.049) matches its vertical ratio (162.7/154.9=1.050) -> supports horizon ~960.

## Scale (prior: toaster height 0.166 m)
- Feet bottom (front) y=1398.2; plate front-top edge at toast depth (toast occlusion line) y=1122.75; plate back edge 1114.9.
- Naive 2D extent 1398.2-1114.9=283 px would include perspective of the receding top. Used front-plane height:
  s_feet*H = 275.45 - 162.75*delta, delta=(Z_toast-Z_feet)/Z ~0.012 (front-rounding of body ~1.5-2.5 cm, Z~2 m).
- s_feet ~1648 px/m (toaster front), s_toast ~1620 px/m (toast origin). Uncertainty ~ +-3% (delta in 0..0.035).

## Toast track (template matching on frame-42 toast, rotation search -> 0 deg, sub-pixel; cross-checked by top-edge gradient)
- image y offset vs frame 42: f0-39 208.62, f40 72.75, f41 24.01, f42 0, f43 -7.86, f44 25.05, f45 102.42, f46 191.73,
  f47 176.18, f50+ 191.71 (keyframed hop, not ballistic: 2nd diffs 87,25,16,41,44 px/f^2).
- Peak at frame 43: 216.48 px above start.
- t=1.75 s -> frame index 42. Backward speeds v41=48.74, v42=24.01 px/frame -> |dv|=24.73 px/f^2 = 14244 px/s^2.

## Answers
- 320 toast length (world X extent = horizontal width 195 px): 0.1204 m. Medium confidence: if "length" means the
  longest side (vertical 239 px) the answer would be ~0.148 m.
- 321 toaster length (foot-to-foot 462 px at front depth): 0.2804 m. Good confidence (+-3%).
- 322 peak vertical displacement: 216.48 px -> 0.1336 m. Good confidence (+-3%).
- 323 acceleration at 1.75 s: 8.79 m/s^2. Medium: depends on frame/time convention (index 41 would give ~31 m/s^2).
