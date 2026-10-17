from util import *
import sys
v=sys.argv[1]
fr=frames(v)
bg=None
if 'segmented' in v:
    getm=lambda f:(f.astype(int).min(axis=2)<225)
else:
    # background: median of first and last frames combination
    allf=[f for i,f in fr]
    bg=allf[0].astype(float) if "0262" in v else np.median(np.stack([allf[0],allf[-1],allf[25]]),axis=0)
    getm=lambda f:(np.abs(f.astype(int)-bg).max(axis=2)>25)
rows=[]
for i,f in fr:
    m=getm(f).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    if st[k,4]<300: continue
    rows.append((i,cen[k][0],cen[k][1],st[k,1],st[k,1]+st[k,3],st[k,2],st[k,3],st[k,4]))
a=np.array(rows)
np.set_printoptions(suppress=True,linewidth=150,precision=2)
print(a)
