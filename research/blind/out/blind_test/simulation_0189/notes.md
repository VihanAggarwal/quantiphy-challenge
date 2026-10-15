# simulation_0189 — catering truck lifting its body, cardboard box on roof (V2MS, 120 fps, 1920x1080)

## Scene / camera
- Static, level camera (all verticals exactly vertical); principal point at image centre confirmed: the far-side rear
  stabilizer pad (553,957) lies on the line from (960,540) to the near pad (488,1024) (predicted v=957.3).
  Depth ratio near/far pad = 0.862.
- Box: moves straight up at constant pixel speed (linear fit, residual 0.05 px): 19.21 px/s -> s_b = 0.094/19.21
  = 0.004894 m/px at the box near face.
- Truck body: rises with constant acceleration (y = -3.49 t^2 - 9.07 t px), so it is NOT moving with the box; the box
  floats slightly above the roof in frames 70-270 (dark underside gap, up to ~3.5 px) and later sinks into it.
- Box near face is deeper than the roof near edge: at t=0 the box bottom is hidden ~4.3 px behind the roof edge
  (face height 190.7 px vs visible 186.45 px; max gap 3.5 px at relative shift 7.8 px). If the box rests on the roof
  at t=0: Zt/Zb = 1 - 4.3/171.55 = 0.975 -> s_t = 0.004771 m/px at the truck near side.

## Measurements (px, frame 0)
- Box near-face width 407.1 (edges 529.3 / 936.4); face height 190.7; open flap rises 19.2 px above the top edge.
- Truck: rear lamp x=124, mirror tip x=1840 (cab front 1812). Mirror ~0.2 m proud of the side -> corrected span 1709.8 px.
- Truck top at t=0: front lift post / platform rail top y=306.5; ground (tyre bottom) y=1025 -> 718.5 px.
- Tyre near-sidewall diameter ~161 px (bottom 1024.8, top ~864; rim centre 1584,942).

## Answers
- 456 box length = 407.1*s_b = 1.992 m (confidence high)
- 457 box height: face only 0.933 m, including the raised flap (AABB) 1.027 m -> hedged 0.99 m (medium)
- 458 truck length = 1709.8*s_t = 8.16 m (medium-high; +/-2% from depth ratio)
- 459 truck height at t=0 = 718.5*s_t = 3.43 m (medium-high)
- 460 tyre diameter = 161*s_t = 0.77 m (medium; edge of dark tyre against dark wheel arch is +/-3 px)
