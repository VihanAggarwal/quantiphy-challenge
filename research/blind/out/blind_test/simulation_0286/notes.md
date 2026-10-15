# simulation_0286 (V2SC, top-down view, plane flying -x over tanks)
- Template matching (nose+wing template from frame 0): constant pixel speed 34.40 px/frame (fit frames 2-56, residual std 1.1 px); frames 0-1 duplicates. 859.9 px/s.
- Scale from prior 22.16 m/s -> 0.025771 m/px (plane's own depth, so consistent for its size).
- Length (x extent, wing-pod nose ~1925 to tail fin ~2480 px, motion blur trimmed) ~553 px -> 14.25 m. Medium confidence (blur, dark plane on dark ground).
- Width (wingspan incl. dark wingtip caps, which move with the plane, y 372-1090) ~718 px -> 18.50 m. Medium-high confidence.
- Displacement 0.5-1.0 s: constant speed -> 0.5*22.16 = 11.08 m. High confidence.
