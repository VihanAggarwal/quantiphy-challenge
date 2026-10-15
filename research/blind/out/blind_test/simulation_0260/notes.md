# simulation_0260 notes
Scene: fixed camera, back wall, table with cup/phone/pen/plant/phone/bag; mug drops from above frame (released ~t=0) onto table back edge (lands ~frame 16).
Scale: template-matched mug track frames 5-15, quadratic fit a = 6.97 px/frame^2 = 6276 px/s^2 -> 9.8/6276 = 1.5615e-3 m/px at mug depth. Vertex at frame -0.03 => release at t=0.
Perspective: camera has strong horizontal lens shift; vanishing point of depth lines ~(1440-1470, 722-735) from table legs (left legs 520 vs 679, right legs overlap), table top front/back edges (896/866) and window sill lines. Scale per object = s_mug*(y_mug-yh)/(y_obj-yh), yh~728.
Speeds: backward diff of fitted parabola: t=0.2 -> 1.81 m/s, t=0.4 -> 3.77 m/s (g*(n-0.5)/30 analytic: 1.80/3.76). Confidence high.
Sizes (px -> m): mug h 54px ->0.085 (high); red cup h 63px ->0.097 (high); plant h 61, w 47px ->0.094/0.073 (med-high);
phone x-extent 52px ->0.080 (med); bag 224px ->0.342 (med); table front edge 1020px at front-edge depth (ratio 0.83) ->1.34 (med);
AC front face 132-567 = 435px, grille 567-637 is side face, AC front at ~0.92 of wall depth -> 0.634 (low-med; assumes AC back against wall).
