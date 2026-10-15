# simulation_0045 – notes

Scene: a fixed camera looks down a street. A cyclist (blue city bike with a rear rack) rides away along the road. A walker goes
away along the right-hand sidewalk. A phone booth stands at the far end, and there are stoops of a stone house (near) and a green
clapboard house (far) on the right. Prior: bike speed 4.87 m/s (assumed constant).

## Camera
- Street VP (curbs + cornices, RANSAC LSD): (560, 199.3). Facade lines gave (566, 201) and ground lines (558, 198), so the road is level, the horizon is at row ~199.3 and roll is ~0 (vertical VP x ~959).
- Focal length:
  - Near manhole ellipse, exact circle-on-plane fit for inner and outer rims: f = 1946 / 1952. This barely depends on cy.
  - Vertical VP with the principal point at the image centre: median of the long verticals gives f ~1900.
  - Far manhole, first order: ~2050 (noisy).
  - Used f = 1925 px, cy = 383, pitch 5.45 deg.
- Scale: hand-read rear-wheel contact points on 13 frames (12..96) were back-projected to the road plane and fitted to a straight line at constant speed, with speed = 4.87 m/s. This gives camera height H = 2.22 m. Heading is parallel to the curbs (track points to the street VP).
- Check against depth_info (bike): the rear-contact ranges are 11.84 and 16.62 m at t = 1 and 2 s. The bike origin is 12.12 and 16.90 m, i.e. a constant +0.28 m, so the origin sits ~0.3 m ahead of the rear contact. The range rates agree (4.778 vs 4.779).
- Human depth_info (17.17 and 18.38) does not match the visible walker. His feet are on the sidewalk at range ~11 m and he passes in front of the fence. So the human origin is offset by ~6 m, but its range rate (1.21 m/s) agrees with the visible walker's motion. Only the bike depth was used for scale.
- Curb / sidewalk height above the road: c ~0.13 m, from radial (VP) intensity profiles across the curb face.

## Answers (f = 1925, c = 0.13)
- 1174, walker speed: footfall (heel) positions on the sidewalk plane for 6 consecutive planted feet. Step period is 17 frames (lowest-point plateaus; head-bob minima). Fit gives 1.22–1.24 m/s, answer **1.23**. Confidence: medium-high. Main uncertainty: period ±0.25 frame (±1.5%).
- 1175, walker height: head top over the planted foot at mid-stance in 5 strides gives 1.74–1.77 (mean 1.76). Adding a small allowance for walking posture gives **1.77**. Confidence: medium-high. Scales ~1/f (±2%).
- 1176, phone-booth height: base at row 399.7 and cap top at row 114, distance ~20 m, giving 2.97 m. A grey roof object reaches row 103.5 (3.07 m) and is probably not part of the booth. Answer **3.0**. Confidence: medium.
- 1177, left pillar of near door to right pillar of far door: the stoop pillars give 3.4 m centre to centre (near stoop's left stone pillar s ≈ 9.5, far stoop's right post s ≈ 12.9 along the street). The door-flanking pilasters, with facade planes from the railing ends (lat ≈ 5.4 / 5.2), give 3.3–4.0 (~3.6). Answer **3.5**. Confidence: low-medium (ambiguous object).
- 1178, bike height (handlebar to ground): left-hand/grip centre over the front part of the wheelbase on 4 frames gives 0.96–1.00. Adding the bar top gives **0.99**. Confidence: medium.
- 1179, bike length: front/rear contact separation on 6 frames gives a wheelbase of 0.90–1.15 (mean ~1.03). Adding the wheel diameter gives **1.74**. Confidence: low-medium.
- 1180, wheel diameter: rear hub (dark axle spot) above the contact gives R ≈ 0.36. The chain/rack-stay bar gives R ≈ 0.325. Answer **0.69**. Confidence: low-medium.
- 1181, first step of the near house's stoop: bottom riser between VP-converging edges, 30 px at ~9.4 m, giving 0.145–0.156. Answer **0.15**. Confidence: medium.

Scripts are in work/: cam.py (camera model), lm.py, manhole2.py, bikescale.py, walker scripts, and others.
