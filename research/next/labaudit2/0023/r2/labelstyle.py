import numpy as np, json
from geo import *
T=json.load(open(D+'cover_track.json'))
H=0.0146
out={}
print('--- v(1.2): c30->c31 = v29->v30, stated r(c30)=1.02')
for route in ['stated','ruler']:
    M=board_model(route); p0=M['B']+M['n']*H
    for pre in ['x','o']:
        for cdef in ['cen','bbox']:
            ux=lambda k: (T[pre][k]['cx'],T[pre][k]['cy']) if cdef=='cen' else (T[pre][k]['bx'],T[pre][k]['by'])
            g29=hit_plane(p0,M['n'],*ux(29)); g30=hit_plane(p0,M['n'],*ux(30))
            r29=np.linalg.norm(g29); r30=np.linalg.norm(g30)
            P30=bp(*ux(29),1.02); P31=bp(*ux(30),1.02+(r30-r29))
            vl=np.linalg.norm(P31-P30)*2500; vg=np.linalg.norm(g30-g29)*2500
            # scaled-geometry variant: rescale whole geometry so that range at c30 = 1.02
            vs=vg*1.02/r29
            print(f'{route:6s} {pre} {cdef:4s} geo r29 {r29:.4f} r30 {r30:.4f} | label-style (stated anchor) {vl:.1f}  geometric {vg:.1f}  geometric rescaled to 1.02 {vs:.1f}')
print('--- v(1.4): c35->c36 = v34->v35, stated r(c35)=0.857; visible-centre clicks')
for h in [0.169,0.171]:
    for pre,c34,c35 in [('o',(572,487),(570,490.5)),('x',(571,486.5),(570,490.5))]:
        # geometric range of the clicked surface: clicks fall on the cover top face (height H) near its front edge
        g34=table_pt(*c34,h-H); g35=table_pt(*c35,h-H)
        # book-fixed point: use the bottom-line motion (dZ) for the displacement of the clicked material point
        r34=np.linalg.norm(g34); r35=np.linalg.norm(g35)
        P35=bp(*c34,0.857)
        for name,r36 in [('plane-anchored',0.857+(r35-r34)),('interp 1.4-1.6',0.857+(0.851-0.857)/5)]:
            P36=bp(*c35,r36); print(f'h={h} {pre} {name:15s} r36={r36:.4f}  v={np.linalg.norm(P36-P35)*2500:.1f}   (geo click ranges {r34:.4f}->{r35:.4f}, geo step {np.linalg.norm(g35-g34)*2500:.1f})')
