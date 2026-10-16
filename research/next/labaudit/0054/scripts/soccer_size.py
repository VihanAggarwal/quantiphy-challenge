"""Soccer ball diameter, routes:
 S1 (camera a, frame 0): soccer (65 px wide, centre ~(158.5,598)) beside the basketball (70.5 px, centre (241.5,574.5)),
    both resting on the floor; ranges from floor-plane intersection at the centre height (H 0.95 m, pitch 1-3.8 deg),
    basketball 23.2 cm as the reference -> ratio route (scale-free except via the floor geometry).
 S2 (camera b, frame 48 = 2.0 s): stated range 3.254 m, disc 44-47 px at (834,371)."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
def ray(u, v):
    d = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return d / np.linalg.norm(d)
def on_plane(u, v, H, pitch, hgt):
    p = np.radians(pitch); n = np.array([0, np.cos(p), np.sin(p)])  # gravity (down) in camera coords
    d = ray(u, v); t = (H - hgt) / (n @ d); return t  # range along unit ray
def size_D(u, v, dpx, rng):
    th = np.arctan(np.hypot(u - CX, v - CY) / F); b = dpx / 2
    s = b * np.cos(th) / np.sqrt(F ** 2 + b ** 2); return 2 * rng * s
for H in (0.9, 0.95, 1.0):
    for pitch in (1.0, 2.5, 3.8):
        rb = on_plane(241.5, 574.5, H, pitch, 0.116)
        # iterate soccer radius
        Rs = 0.10
        for _ in range(10):
            rs = on_plane(158.5, 598.0, H, pitch, Rs)
            Ds = 0.232 * (size_D(158.5, 598, 65, rs) / size_D(241.5, 574.5, 70.5, rb)); Rs = Ds / 2
        print('H %.2f pitch %.1f: r_bb %.3f r_soc %.3f  soccer D %.1f cm | bb size-check D(bb)=%.1f cm at floor range' % (H, pitch, rb, rs, Ds * 100, size_D(241.5, 574.5, 70.5, rb) * 100))
for dpx in (44, 45.5, 47):
    print('S2 b f48: %.1f px -> D %.1f cm (range 3.254 as centre range), %.1f cm (3.254+0.10)' % (dpx, size_D(834.2, 370.8, dpx, 3.254) * 100, size_D(834.2, 370.8, dpx, 3.354) * 100))
