import cv2, numpy as np, json, sys
sys.path.insert(0,'scripts')
from circfit import edge_circle
rend=sys.argv[1] if len(sys.argv)>1 else 'o'
res={}
# initial (static) frames: use left, upper-left, bottom-left, bottom arcs (right side is person/bin, top hands)
c=(612,508); r=62
for n in range(0,20):
    img=cv2.imread(f'frames/{rend}_{n:02d}.png')
    cx,cy,rr,pts=edge_circle(img,c,r,list(range(95,235,5)))
    res[n]=(cx,cy,rr,len(pts))
# moving frames
c=None
init={22:(588,528,66),24:(570,543,73)}
prev=None
for n in range(22,40):
    img=cv2.imread(f'frames/{rend}_{n:02d}.png')
    if prev is None: c0=init[22]
    else: c0=prev
    cx,cy,rr,pts=edge_circle(img,c0[:2],c0[2],list(range(-180,5,5)),band=(0.8,1.25))
    res[n]=(cx,cy,rr,len(pts)); prev=(cx+(cx-c0[0])*0.0,cy,rr)
for n,v in res.items(): print(n,'c=(%.1f,%.1f) r=%.1f npts=%d'%v)
json.dump({int(k):list(map(float,v)) for k,v in res.items()},open(f'yoga_{rend}.json','w'))
