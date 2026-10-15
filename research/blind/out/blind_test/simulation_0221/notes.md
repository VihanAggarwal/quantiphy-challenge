# simulation_0221 (S2MC, top-down room, 1920x1080, 80 frames @24fps)
Scale: vacuum (robot) disk = 120-121 px (bbox of diff mask, frames 41-79) -> 0.438/120.5 = 0.003635 m/px at vacuum top; floor-equivalent 0.003659 m/px.
Perspective: near-orthographic top view. TV stand front face shows ~8 px band at r~255 px -> h/Hc ~0.035 -> Hc ~14 m (stand ~0.5 m). Raised object tops
de-magnified by k=1/(1-h/Hc) with guessed heights (bench 0.45, stand 0.5, lamp shade rim ~0.85, vase ~0.65, sofa ~0.4-0.7).
Pixel extents: bench 287.5x115.5; TV stand 711..~1194 (right end hidden under lamp, from symmetry of glass shelf/legs) x 112 (top);
lampshade 148; vase 72-73; mirror bottom edge 166 px (floor); carpet vertical diameter ~480; sofa 885x478 px.
Motion: background = frame79 with frame0 pasted over x570-880 (removes resting vacuum + its shadow); positive-brightness diff mask, bbox left/top edge + 60 px.
Backward-difference speeds; acceleration from linear fit of speed over +-3-4 frames. Speed: accelerates ~2.1 m/s^2 to ~1.76 m/s plateau (~0.9-1.2 s), dips to 1.3 (1.7 s), peaks 2.0 (2.1 s), stops ~2.9 s.
Confidence: speeds high; acc@0.5 medium; acc@1 low (near zero, plateau edge); acc@2 medium; sizes medium (TV stand length, lampshade, vase, sofa height corrections lower).
