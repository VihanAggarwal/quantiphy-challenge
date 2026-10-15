# simulation_0055 — measurement notes

Scene: fixed, level camera (vertical edges exactly vertical, so pitch is 0 and the horizon is at cy=539.5), 1080x1080 at 30 fps, 78 frames.
The camera looks straight across a street. In view: an orange car that enters from the left at frame 22 and brakes, a person walking right to left
on the near sidewalk, a fire hydrant (u~941), a streetlight (u~815), and raised curbs.
Depth convention: Euclidean range. The car's range changes 16.06 -> 11.67 m while its image rows and size stay constant, so the values cannot be Z-depth.
Static-object ranges fit the bounding-box centre better than the base.

## Scale / focal length
- Car wheel-arch gap centres were tracked (orange mask). The fit is quadratic with residual sd 0.4 px and pixel acceleration -448.7 px/s^2. With the prior of 2.86 m/s^2 this gives s_W = 156.9 px/m at the depth of the wheel features.
- Ranges d0, d1 plus the prior-based displacement D = 7.43 m give car X positions Xc1 = -4.3..-4.5 m and depth of the car centre Zc = 10.68..10.76 m.
- f from four routes:
  - (a) car: s_W*(Zc - half-width), and the front/rear silhouette tangent-depth symmetry. Gives 1525-1549.
  - (b) tyre bottom row ~877.5 (hub 827 + radius 50.5; hidden by the curb) gives h_r = 2.16 m. Combined with the far-curb ratio and the static f*H_s = 3060, this gives ~1563.
  - (c) the person's two ranges, assuming constant depth, give ~1570 +-60.
  - (d) the hydrant/streetlight pair gives ~1505 +-50.
  - Adopted f = 1540 px (HFOV ~38.6 deg). Answers that scale with 1/f carry about +-2% from this.
- Camera height above the near sidewalk H_s = 1.986 m. Camera height above the road h_r = 2.17 m (average of the tyre-based and curb-based values).

## Answers (f=1540)
| qid | quantity | value | method | confidence |
|---|---|---|---|---|
| 1220 | hydrant height | 1.026 m | Z_h=8.79 from range (bbox centre). Top apex at 707.7, base near edge at 897.0, base radius 41 px. Perspective-corrected | medium-high |
| 1221 | streetlight height | 4.366 m | Z_s=8.76. Finial top at 120.8, base near edge at 896.5 | medium-high |
| 1222 | car length | 4.99 m | Silhouette end tangents vs wheel track, using the prior scale with per-end depth ratios. Does not depend on f (range 4.97-5.01) | medium-high |
| 1223 | car height | 1.433 m | h_r (2.159 from the tyre, 2.184 from the curb) minus the roof crown (row 644.6 at Zc+0.2) | medium |
| 1224 | curb height | 0.191 m | Far-curb face 15.9 px gives 0.197. Near curb from h_r - H_s gives 0.185 | medium |
| 1225 | person speed 1-2 s | 0.535 m/s | Torso centroid moved 104.3 px between frames 30 and 60, at Z_p=7.78 (0.00505 m/px), giving 0.527. Raised ~1.5% for pelvis bob (0.527-0.55) | medium |
| 1226 | person height | 1.809 m | H_s - (head top 574.5 - cy)*Z_p/f. Head top varies 572.4-579.4 over the gait | medium-high |
