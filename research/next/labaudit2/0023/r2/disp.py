import numpy as np, json
from geo import *
T=json.load(open(D+'cover_track.json'))
H=0.0146
TT={h:json.load(open(D+'table_track_h%.3f.json'%h)) for h in [0.170]}
for route in ['stated','ruler']:
    M=board_model(route); p0=M['B']+M['n']*H
    for pre in ['x','o']:
        c24=(T[pre][24]['cx'],T[pre][24]['cy']); c29=(T[pre][29]['cx'],T[pre][29]['cy'])
        g24=hit_plane(p0,M['n'],*c24); g29=hit_plane(p0,M['n'],*c29)
        r25=1.02+(np.linalg.norm(g24)-np.linalg.norm(g29))
        P25=bp(*c24,r25)
        for h in [0.169,0.171]:
            # rest: visible centre click (566.5,494.5) at stated 0.851 ; geometric top-face centre = mid of back edge (y~480.1) and front edge (y~496.4) at x 566.5, height H
            P40=bp(566.5,494.5,0.851)
            back=table_pt(566.5,480.1,h-H); front=table_pt(566.5,496.4,h-H); G40=(back+front)/2
            # geometric visible-centre click point (surface hit on the cover at y 494.5)
            V40=table_pt(566.5,494.5,h-H)
            dl=np.linalg.norm(P40-P25)*100; dg=np.linalg.norm(G40-g24)*100; dv=np.linalg.norm(V40-g24)*100
            dgl=np.linalg.norm(G40-P25)*100
            print(f'{route:6s} {pre} h={h}: r25(label)={r25:.4f} geo r24={np.linalg.norm(g24):.4f} | label-style (stated 0.851 at rest) {dl:.1f} | geometric top-face centre->centre {dg:.1f} | geo slope -> geo visible-centre click {dv:.1f} | rest centre range geo {np.linalg.norm(G40):.4f}, visible click geo {np.linalg.norm(V40):.4f}')
