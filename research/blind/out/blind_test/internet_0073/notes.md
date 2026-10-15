# internet_0073 - conveyor belt, prior belt speed 0.3 m/s
Method: template tracking (cv2) of red package and middle cardboard box over all 138 frames, corrected for slight camera pan
(tracked static yellow-striped belt frame, -3.6 px/s). Belt pixel speed 58.0 px/s at dataset fps 30 (raw uncorrected 54.3).
Scale = 0.3/58 = 0.00517 m/px. Belt is roughly fronto-parallel; all objects at similar depth.
Extents from 4x zoomed crops at t=0: red pkg 93x47 px; middle box 106x37 px; blue bag x 725-873 (c 799);
yellow bag x 912-1087 (c 1000); red pkg x 369-462 (c 415.5).
Distances taken centre-to-centre (edge gaps would be: blue-yellow 39 px=0.20 m, red-blue 263 px=1.36 m) -- main ambiguity, low confidence.
Displacement 2.0-3.5 s = belt speed x 1.5 s = 0.45 m (measured ~0.40-0.42, camera rotation noise).
Confidence: sizes medium; displacement high; distances low (convention).
