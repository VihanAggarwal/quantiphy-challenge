# simulation_0222 (S2MS, top-down living room, robot vacuum)
Camera: nadir perspective (walls visible), principal point ~ image centre. Vacuum disc = 120.3 px (subpixel edges, static at end) -> 3.641 mm/px at vacuum-rim height.
Camera height estimated in floor-px: H ~ 2850 (f ~2850 px, HFOV ~37 deg) from mirror top magnification k=1.20 (assuming mirror ~2.7x its width),
lampshade top-opening parallax (dome ~0.3 m), dock tower k=1.010, vase mouth parallax (range 1800-3600). Size = img_px * s_floor * (1 - h/H),
s_floor = 3.667 mm/px; heights assumed (bench 136 px, stand 163, lamp rim 263, vase widest 208, sofa arms 163 / back 218 floor-px).
Image extents: bench 287x115; TV stand 710->~1205 (right end hidden under lampshade, bounded 1195-1222) x 122; lampshade 148.5; vase 72.5;
mirror bottom width at floor 168; carpet circle fit D~477 (floor); sofa x 568.5->1451.5, y 578.5->1058.5 (front offset 38.5, back offset 518.5).
Motion: template-matching track (subpixel), backward-difference speed * 0.438/120.3 * 24; accel = d|v|/dt with light quadratic smoothing.
Confidence: speeds high; carpet/mirror/bench high-medium; stand length medium (hidden end); sofa/lamp medium (height assumption); acc@1s low (near speed peak, small value).
