# sim3audit: simulation_0017 family (0016 nadir, 0017 perspective, 0017_segmented)

Scripts are in `scripts/`; frames and crops are in `frames/` (PNG only, about 29 MB).

Orientation: `simulation_0017.mp4` is stored rotated 90 deg CW. `simulation_0017_segmented.mp4` is stored upright and has the same geometry (pixel-identical layout). `simulation_0016` is a nadir view padded to 1920x1080.

## Same object/quantity across clips

| object / qty | 0016 (nadir, k_floor 99 px/m) | 0017 / 0017_seg (perspective, Hc~0.965, f~888) | verdict |
|---|---|---|---|
| pedestal width | 1.469 (1498) | 1.47 (1084, 1652) | consistent across two independent calibrations |
| bench length | 2.249 (1500) | 2.24 (1087, 1655) | consistent |
| bench width | 0.718 (1499) | cushion depth ~0.68 from 0017 cushion v 157.5/212.5 | consistent (cushions sit inside the board) |
| bench seat height | shadow ~0.52 | 0.50 (1086, 1654) | consistent |
| pedestal height | shadow ~0.65-0.78 (ambiguous: the slab shadow dominates either way) | 0.60 (1085, 1653) dark block only | keep (see below) |
| sculpture height | n/a | 1.95 hedge of 2.00 / 1.68 (1088, 1656) | keep |
| person height | n/a | 1.87 (1083, 1651); agent re-measured 1.864 | keep |
| panel height | n/a | 1.98 (1089, 1658) | keep; re-measured 1.97-1.99 |
| **panel width** | n/a | **0.37 (1657, pre-agent pipeline)** | **WRONG -> 1.55** |

## 1657: panel width (0.37 -> 1.55)

The 0017 agent answered only qids 1083-1089. 1657 is asked only on the segmented clip, so it kept the pre-agent pipeline value. That pipeline, and its three Claude runs (0.51 / 0.355 / 0.37, with heights 0.71 / 0.52 / 0.52), scaled the panel with `distance_the_freestanding_art_display_panel = 4.223 m`. Their width/height ratio of about 0.7 shows they measured the face width.

The depth of 4.223 m cannot belong to the visible panels:
- At frames 35-45 the person (Euclidean 4.75-4.9 m, so Z of about 4.7) walks IN FRONT of the left panel and occludes it (`frames/occl_f040.png`). A Euclidean distance of 4.223 would force Z <= 4.223, which would put the panel in front of the person.
- The panel base touches the floor at y~612.5 (v=72.5 below the horizon), against y=703.5 for the pedestal front face. That puts the panel at Z ~ 11.8 m. The ratio to the pedestal does not depend on f or Hc.
- The segmented clip keeps exactly these two flanking panels; the panels hidden behind the sculpture are removed. So these two are the question objects.
- Inside the same clip, 1658 (height 1.98, agent measurement at the correct depth) and 1657 = 0.37 imply an aspect of 0.19. The observed aspect is 0.75-0.80 (base 114-118 px against 148 px height).

Re-measurement (`scripts/panel_width.py`, using the right panel, which the pedestal does not occlude):
- The base X-extent is 114 px (segmentation mask) to 118 px (gridded zoom of the original, x 664-783). The frame alone is 88-91 px.
- Width = Hc * px / v_bottom with v_bottom = 72.5. f cancels.
  - Route 1, Hc = 0.964 from static depth_info (bench and pedestal, agent): 1.52-1.57.
  - Route 2, Hc = 0.970 from the person's planted foot (person depth plus kinematic f, agent): 1.53-1.58.
  - Route 3, Hc = 0.974 from the 0017 receding floor seams. These are spaced 1.358 in X/Hc and line up with 0016's 1.323 m tile rows. This route uses no 0017 depth_info: 1.53-1.585.
  - Family-ratio route: 1.98 (panel height) * 118/148 = 1.58.
- Adopted width = 1.55, the AABB including the stepped base. The frame alone would be ~1.2.

Risk: if "width" meant panel thickness (unlikely for a display panel; every earlier run read it as the face width), 1.55 would be wrong. The panels look rotated slightly toward the centre line (the base front edge slants 4 px), and the AABB X-extent above already accounts for that.

## Rows kept (with reasons)

- 1085/1653, pedestal height 0.60, and 1088/1656, sculpture height 1.95. Both hinge on whether the light tapered slab belongs to the pedestal (0.92 / 1.68) or to the sculpture (0.60 / 2.00). Physical evidence cannot separate the two:
  - The 0016 shadow of ~0.68 is dominated by the slab either way.
  - The segmented clip keeps both block and slab.
  - The depth pair 5.963 / 5.962 fits "slab in sculpture" under Euclid-to-bbox-centre (predicted gap 3 mm, against 33 mm for "slab in pedestal"). However, it fits either reading under optical-axis Z, or with a 3 cm XY offset of the sculpture.
  - No two routes agree on a change, and "square base" fits the dark block. Kept.
- 1083/1651 person 1.87: the agent re-measured 1.864; kept.
- 1089/1658 panel height 1.98: re-measured 1.968-1.988 over the three Hc routes; kept.
- 1084/1652, 1086/1654, 1087/1655, 1498-1500: consistent across 0016 and 0017; kept.
