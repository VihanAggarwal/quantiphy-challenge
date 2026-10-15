# simulation_0239 notes
Top-down static camera; house roof (gable main block, ridge along image y; higher cross gable ridge along image x); two horses walking +x below the house.
Back horse = brown (upper, behind); front horse = white (lower, ahead).
Scale: brown horse template track 64.4 px/s (0-2 s fit; local 61-64) -> 0.874/64.3 = 0.01359 m/px at horse level.
- 794 brown length ~147 px -> 2.0 m (medium confidence)
- 798 white length ~156-174 px (tail/muzzle ambiguity) -> 2.2 m (medium-low)
- 797 white speed at 1 s: template fit 111-117 px/s (gait oscillation) -> ~1.55 m/s (medium)
- House: roof extents x 617-1426 (cross-gable barge peaks), y 20-745 (main gable peaks). Perspective from gable peaks vs eaves:
  D_peak/D_eave = 0.856 (main), 0.906 (cross) -> eave-scale extents X=733, Y=621 px. Eave-vs-horse depth ratio assumed ~0.9
  (roof pitch 30-45 deg, f 1500-2700 px). X=9.0 m (length, along horse motion / larger), Y=7.6 m (width). Uncorrected would be 10.9/9.8. Low-medium confidence.
