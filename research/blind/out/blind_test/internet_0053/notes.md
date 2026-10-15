# internet_0053 notes
Static camera, 1920x1080, 81 frames @30fps. Rider on e-scooter moves L->R.
Speed scale: rear wheel x 405 (f0) -> 1857 (f80): 1452 px / 2.667 s = 544 px/s (template tracking f0-50 ~569 px/s, f50-70 ~513 px/s; slight decel).
s0 = 4.46/544 = 0.00820 m/px at rider ground (avg wheel-contact y~713).
Perspective: low camera, horizon est. y~595 (far court fence base y~612 through gate, near fence base ~690).
Scale at object depth = s0 * (713-595)/(y_ground-595).
Measurements (px, ground y): person 317 (f0, ground 718) / 305 (f40, 712) -> 2.49/2.52;
lamp 125..703 = 578 -> 5.18; scooter h 210/197 -> 1.65/1.63; scooter length 206/195 -> 1.62/1.61;
sign 574..~683, 110 tall x 66 wide -> 1.21 / 0.73; hydrant 557..683 =126 -> 1.39 (hedged 1.33);
bench 1342..1656 (314) x 550..699 (149) -> 2.92 / 1.39; bin 574..697 =123 -> 1.17.
Note: implied scale is ~1.55x real-world (person 2.5 m); followed prior as the scale per instructions.
Confidence: scooter/person medium-high (same depth as prior); fixed objects medium (perspective correction 1.14-1.40x, horizon uncertain); hydrant/sign lowest.
