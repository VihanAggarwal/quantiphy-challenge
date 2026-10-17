import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
orb=cv2.ORB_create(6000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
REF=15
kr,dr=orb.detectAndCompute(g[REF],None)
al=[]
for i in range(30):
    k,d=orb.detectAndCompute(g[i],None); m=bf.match(d,dr)
    src=np.float32([k[x.queryIdx].pt for x in m]); dst=np.float32([kr[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(src,dst,cv2.RANSAC,1.5)
    al.append(cv2.warpPerspective(fr[i],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE))
bgs=np.median(np.stack(al[8:]),axis=0).astype(np.uint8)
lab0=cv2.cvtColor(bgs,cv2.COLOR_BGR2Lab).astype(np.float32)
# red line rows in ref15: top edge ~ 480-0.0275*(x-300), bottom ~ top+45
def redtop(x): return 479.7-0.0275*(x-300)
prev=None
res=[]
for i in range(0,24):
    L=cv2.cvtColor(al[i],cv2.COLOR_BGR2Lab).astype(np.float32)
    d=np.sqrt(((L-lab0)**2).sum(axis=2)); d=cv2.GaussianBlur(d,(3,3),0)
    m=(d>25).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
    n,ll,st,cc=cv2.connectedComponentsWithStats(m); j=1+np.argmax(st[1:,4]); x,y,w,h,a=st[j]
    xc0=x+w/2
    rt=redtop(xc0); rb=rt+46
    rowsA=[r for r in range(y+12, int(rt)-6)]          # above red line
    rowsB=[r for r in range(int(rb)+6, y+h-12)]         # below red line
    mids=[];halfw=[];band=[]
    for r in rowsA+rowsB:
        prof=d[r, max(0,x-40):min(1920,x+w+40)].astype(np.float64); off=max(0,x-40)
        inner=prof[int(xc0-off-40):int(xc0-off+40)]
        if len(inner)<10: continue
        plat=np.median(inner)
        if plat<30: continue
        thr=0.5*plat
        above=prof>thr
        idx=np.nonzero(above)[0]
        if len(idx)<5: continue
        l=idx[0]; rr=idx[-1]
        if l==0 or rr==len(prof)-1:
            continue
        lx=l-1+(thr-prof[l-1])/(prof[l]-prof[l-1]); rx=rr+(prof[rr]-thr)/(prof[rr]-prof[rr+1])
        mids.append(off+(lx+rx)/2); halfw.append((rx-lx)/2); band.append(0 if r in rowsA else 1)
    mids=np.array(mids); nA=len([r for r in rowsA]); 
    split=sum(1 for _ in rowsA)

    # also vertical extent at center column
    res.append((i,np.median(mids) if len(mids) else np.nan, np.mean(mids) if len(mids) else np.nan, len(mids), np.std(mids) if len(mids) else 0))
    band=np.array(band); hw=np.array(halfw)
    print('%2d mid med %.1f mean %.1f n %d sd %.1f'%res[-1], ' A %.1f (n%d) B %.1f (n%d) halfwA %.1f halfwB %.1f'%(np.median(mids[band==0]) if (band==0).any() else np.nan,(band==0).sum(),np.median(mids[band==1]) if (band==1).any() else np.nan,(band==1).sum(), np.max(hw[band==0]) if (band==0).any() else np.nan, np.max(hw[band==1]) if (band==1).any() else np.nan))
np.savetxt('research/next/audit3/internet_11/remeasure/track47d.txt',np.array(res),fmt='%.3f')
