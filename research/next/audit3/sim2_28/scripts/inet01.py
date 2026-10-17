import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('internet_0001_segmented')
out=[]
prev=None
for i,f in enumerate(F):
    nb=(f.max(axis=2)>35).astype(np.uint8)
    nb[:30]=0; nb[690:]=0
    # remove lane markings: thin (height<12) components
    n,lab,st,cen=cv2.connectedComponentsWithStats(nb)
    cands=[(k,st[k],cen[k]) for k in range(1,n) if st[k][3]>30 and st[k][4]>1500 and 420<cen[k][1]<560]
    s=' '.join(f'[{st[0]},{st[0]+st[2]},{st[1]},{st[1]+st[3]},a{st[4]},c{c[0]:.1f}]' for k,st,c in cands)
    print(i,s)
