import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
vid=sys.argv[1]; sthr=int(sys.argv[2]) if len(sys.argv)>2 else 40
F=frames(vid,n=49)
np.set_printoptions(suppress=True,precision=2,linewidth=160)
allrec=[]
for k in range(49):
    hsv=cv2.cvtColor(F[k],cv2.COLOR_BGR2HSV)
    m=(hsv[...,1]>sthr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=sorted([(st[i,4],i) for i in range(1,n) if st[i,4]>200],reverse=True)[:3]
    recs=[]
    for a,i in comps:
        x,y,w,h,area=st[i]
        recs.append((x,y,w,h,area,cen[i][0],cen[i][1]))
    # sort by area desc: expect white horse, brown horse, rabbit
    allrec.append(recs)
    if k in (0,24,48):
        print(k,[tuple(np.round(r,1)) for r in recs])
        if k==24: cv2.imwrite(f'{vid}_mask24.png',cv2.resize(m*255,None,fx=0.5,fy=0.5))
import pickle; pickle.dump(allrec,open(f'{vid}_recs.pkl','wb'))
