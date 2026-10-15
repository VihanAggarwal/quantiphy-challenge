# internet_0030 speedboat
- Camera pans right slowly (background phase-correlation shift ~ -0.85 px/frame); boat track compensated by adding pan.
- Boat tracked by template matching (template from frame 15). Pan-compensated x: f15 652.4, f30 876.3, f41 1034.3 px.
- Boat length ~184 px (f15) to ~177 px (f41) hull, ~200 incl. stern flag; used 190 px = 3.2 m -> 0.01684 m/px.
- d(0.5-1.0)=223.9 px=3.77 m (conf medium); d(0.5-1.37)=381.9 px=6.43 m (medium); speeds 7.54, 7.39 m/s.
- Acceleration: world speed nearly constant (px speed drops ~4% while boat apparent size drops ~4%); answered 0.3 m/s^2 (low confidence).
