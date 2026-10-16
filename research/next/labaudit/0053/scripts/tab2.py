import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
from geo import *
import json
d=json.load(open('xcomps.json'))
def tab(n,prefix='x'):
    im=cv2.imread(f'frames/{prefix}_{n:02d}.png').astype(int)
    b=[x for x in d[str(n)] if x['a']>4000 and not abs(x['cx']-986)<6][0]
    x0,y0,w,h=b['x'],b['y'],b['w'],b['h']
    ya=y0+int(0.72*h); sub=im[ya:y0+h+3,x0:x0+int(0.6*w)]
    white=(sub.min(2)>150)&((sub.max(2)-sub.min(2))<70)
    m=white.astype(np.uint8); k,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if k<2: return None
    i=max(range(1,k),key=lambda j:st[j][4])
    return np.array([x0+cen[i][0], ya+cen[i][1]]), st[i][4], st[i][:4]
H=1.689; dn=DOWN_ROLL
T={}
for n in list(range(6,14))+list(range(30,38)):
    r=tab(n)
    if r is None: print(n,'none'); continue
    T[n]=r[0]; print(n,np.round(r[0],1),'area',r[1],'box',r[2])
for z in (0.0,0.03):
    for a,b in [(10,34),(9,33),(11,35),(8,32)]:
        if a in T and b in T:
            print('z',z,'tab disp n%d->n%d %.3f'%(a,b,np.linalg.norm(floor_pt(*T[b],H,dn,z)-floor_pt(*T[a],H,dn,z))),' ranges %.3f %.3f'%(np.linalg.norm(floor_pt(*T[a],H,dn,z)),np.linalg.norm(floor_pt(*T[b],H,dn,z))))
