# Ball tracks for take a or b. Foreground = pixels where the original render equals both the x and s renders
# (the SAM cut-out is pasted on a green/white background in x and a gradient in s, so background pixels differ).
import sys
from common import *
take=sys.argv[1]
O=frames(take); X=frames(take+'x'); Sr=frames(take+'s')
T=28
def fgmask(k):
    o=O[k].astype(int); x=X[k].astype(int); s=Sr[k].astype(int)
    m=(np.abs(o-x).max(2)<T)&(np.abs(o-s).max(2)<T)
    m=m.astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    return m
def orange(k):
    hsv=cv2.cvtColor(O[k],cv2.COLOR_BGR2HSV)
    h,s,v=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
    return ((h>=2)&(h<=22)&(s>100)&(v>50)).astype(np.uint8)
def desc(comp):
    cs,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea)
    M=cv2.moments(comp,True)
    A=M['m00']
    (ex,ey),(a1,a2),ang=cv2.fitEllipse(c)
    (mx,my),mr=cv2.minEnclosingCircle(c)
    hull=cv2.convexHull(c); Ah=cv2.contourArea(hull)
    return dict(cx=M['m10']/A,cy=M['m01']/A,A=float(A),deq=float(np.sqrt(4*A/np.pi)),dhull=float(np.sqrt(4*Ah/np.pi)),
                minor=float(min(a1,a2)),major=float(max(a1,a2)),ang=float(ang),ex=ex,ey=ey,mec=2*mr)
seeds={'a':{'sb':(318,108)*np.array([4,4])/2,'bb':None},'b':{}}
res={'bb':{},'sb':{}}
cands={}; bcands={}
prev_sb=None
sbseed={'a':(352,296),'b':(437,686)}[take]   # soccer ball start pixel (rest)
prev_sb=np.array(sbseed,float)
for k in range(len(O)):
    fg=fgmask(k)
    # basketball: orange blobs inside foreground (candidates)
    ob=orange(k)&fg
    ob=cv2.morphologyEx(ob,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    n,lab,st,cen=cv2.connectedComponentsWithStats(ob,8)
    bcands[k]=[]
    for j in range(1,n):
        if st[j,4]>400 and st[j,2]<170 and st[j,3]<170:
            comp=(lab==j).astype(np.uint8)
            cs,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            comp2=np.zeros_like(comp); cv2.drawContours(comp2,cs,-1,1,-1)
            d=desc(comp2); d['fill']=d['A']/(np.pi/4*d['minor']*d['major'])
            if d['fill']>0.75 and d['major']<1.8*d['minor']: bcands[k].append(d)
    # soccer: candidate round non-orange foreground blobs
    m=fg&(1-cv2.dilate(ob,np.ones((5,5),np.uint8)))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    cands[k]=[]
    for j in range(1,n):
        if 500<st[j,4]<12000 and st[j,2]<160 and st[j,3]<160:
            comp=(lab==j).astype(np.uint8)
            cs,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            comp2=np.zeros_like(comp); cv2.drawContours(comp2,cs,-1,1,-1)
            d=desc(comp2)
            d['fill']=d['A']/(np.pi/4*d['minor']*d['major'])
            if d['fill']>0.8 and d['major']<1.6*d['minor']: cands[k].append(d)
def link(C,key,anc,ax_,ay_):
    for rng_ in [range(anc,len(O)),range(anc,-1,-1)]:
        p=np.array([ax_,ay_]); lim=40
        for k in rng_:
            best=None
            for d in C[k]:
                dd=np.hypot(d['cx']-p[0],d['cy']-p[1])
                if dd<lim and (best is None or dd<best[0]): best=(dd,d)
            if best:
                res[key][k]=best[1]; p=np.array([best[1]['cx'],best[1]['cy']]); lim=60
            else: lim+=40
a=sys.argv[2:]
link(cands,'sb',int(a[0]),float(a[1]),float(a[2]))
link(bcands,'bb',int(a[3]),float(a[4]),float(a[5]))
json.dump(res,open(f'{OUT}/tr_{take}.json','w'),indent=0)
for k in range(len(O)):
    s=[]
    for key in ['sb','bb']:
        d=res[key].get(k)
        s.append(f"{key} {d['cx']:7.1f} {d['cy']:6.1f} deq{d['deq']:5.1f} min{d['minor']:5.1f} maj{d['major']:5.1f} hull{d['dhull']:5.1f}" if d else key+' -')
    print(k,cap(k),' | '.join(s))
