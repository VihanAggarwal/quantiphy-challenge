import json, numpy as np
d=np.array([np.cos(np.radians(44.224)),np.sin(np.radians(44.224))])
rows=json.load(open('diam2_simulation_0254.json')); R={int(r[0]):r for r in rows}
fr=np.arange(19,47); t=fr/24
xy=np.array([(R[i][5],R[i][6]) for i in fr]); s=xy@d
eq=np.array([R[i][1] for i in fr])
DC=23.9; sc=1064.6
p3=np.polyfit(t,s,3)
tt=np.arange(20,47)/24
vb_px=(np.polyval(p3,tt)-np.polyval(p3,tt-1/24))*24
smid=(np.polyval(p3,tt)+np.polyval(p3,tt-1/24))/2
pl=np.polyfit(s,eq,1)
for label,ratio in (('measured blue-eq shrink (VP~25k)',lambda ss: np.polyval(pl,ss)/np.polyval(pl,sc)),
                    ('VP 19000',lambda ss:(19000-ss)/(19000-sc)),('VP 21700',lambda ss:(21700-ss)/(21700-sc)),('VP 24000',lambda ss:(24000-ss)/(24000-sc))):
    sig=0.9918*(DC/0.17)*ratio(smid)**2
    V=vb_px/sig
    A=np.polyfit(tt-1/48,V,1); Q=np.polyfit(tt-1/48,V,2)
    print(f'{label:34s} lin: a={A[0]:.3f} V0 at t={-A[1]/A[0]:+.3f} rms={(V-np.polyval(A,tt-1/48)).std():.3f} | lin-extrap vb(0.5)={np.polyval(A,0.5-1/48):.3f} vb(1)={np.polyval(A,1-1/48):.3f} | quad a(0.5)={np.polyval(np.polyder(Q),0.5-1/48):.3f} a(1)={np.polyval(np.polyder(Q),1-1/48):.3f} vb(0.5)={np.polyval(Q,0.5-1/48):.3f}')
