# simulation_0169 (S2SS, astronaut drifting upward past moon)
- Scale: astronaut height at frame 0 = 89.5 px (head 477 to feet 566, verified on 4x crop) -> 2.2/89.5 = 0.02458 m/px.
- Track: threshold >60 blob in ROI x1240-1500, y90-700 (track.py); centroid and bbox centre agree within 1%.
- Motion: ease-in/ease-out, mostly vertical. Speed peaks ~3.05 m/s around 1.5-1.9 s.
- Speed = backward diff, with local quadratic fits (+-5 frames) and 5-frame moving average; accel = slope of speed magnitude.
- Answers: v(0.5)=1.56, a=2.45; v(1)=2.58, a=1.3; v(2)=2.94, a=1.0 (decel); v(3)=0.99, a=2.95 (decel).
- Confidence: speeds high (~5%); accelerations medium (10-25%). Height shrinks to 83 px late (rotation), scale held fixed.
