import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0088')
sky=np.median(np.stack(F[::3]),axis=0)
def extent(prof,thr):
    idx=np.nonzero(prof>thr)[0]
    if len(idx)==0: return None
    a,b=idx[0],idx[-1]
    # subpixel crossing
    l=a-1+(thr-prof[a-1])/(prof[a]-prof[a-1]); r=b+(prof[b]-thr)/(prof[b]-prof[b+1])
    return l,r
crow=[];eag=[]
for i in range(2,26):
    d=np.abs(F[i].astype(float)-sky).sum(2)
    # crow: column profile = max over rows 530-575 in region; eagle similarly
    m=(d>60).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8)))
    for k in range(1,n):
        if st[k,4]<200: continue
        x,y,w,h=st[k,:4]
        sub=d[540:566, max(x-10,0):x+w+10]
        prof=sub.max(0)
        pk=np.percentile(prof,95)
        e=extent(prof,pk/2)
        if e is None: continue
        L=e[1]-e[0]
        full = x>5 and x+w<1915
        if not full: continue
        (crow if w<110 else eag).append((i,L,x+max(-10,-x)+e[0],x+max(-10,-x)+e[1],cen[k][0]))
for c in crow: print('crow',c[0],round(c[1],1),round(c[2],1),round(c[3],1),round(c[4],1))
for c in eag: print('eagle',c[0],round(c[1],1),round(c[2],1),round(c[3],1),round(c[4],1))
c=np.array(crow);e=np.array(eag)
pc=np.polyfit(c[:,0],(c[:,2]+c[:,3])/2,1); pe=np.polyfit(e[:,0],(e[:,2]+e[:,3])/2,1)
print('crow speed px/f',pc[0],'eagle',pe[0])
s=17.98/(abs(pe[0])*24)
print('scale',s,'crow L med px',np.median(c[:,1]),'m',np.median(c[:,1])*s,'eagle L',np.median(e[:,1]),np.median(e[:,1])*s,'crow v',abs(pc[0])*24*s)
