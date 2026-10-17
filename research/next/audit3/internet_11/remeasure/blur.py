import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
# raw frames; background from frame where ball absent at that location: use frame 27 (ball gone) aligned via ORB similarity
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
orb=cv2.ORB_create(6000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
def align(src_i,dst_i):
    k1,d1=orb.detectAndCompute(g[src_i],None); k2,d2=orb.detectAndCompute(g[dst_i],None)
    m=bf.match(d1,d2)
    s=np.float32([k1[x.queryIdx].pt for x in m]); d=np.float32([k2[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(s,d,cv2.RANSAC,1.5); return H
def lin(img): 
    x=img.astype(np.float32)/255.
    return np.where(x<=0.04045,x/12.92,((x+0.055)/1.055)**2.4)
for i in (11,12,15,18):
    H=align(27,i)
    bgi=cv2.warpPerspective(fr[27],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    I=lin(fr[i]); B=lin(bgi)
    t=np.loadtxt('research/next/audit3/internet_11/remeasure/track47d.txt'); 
    # approximate raw center: aligned pos (ref15) ~ raw (camera x shift tiny)
    xc=dict((int(a),b) for a,b in zip(t[:,0],t[:,1]))[i]
    # find center row: vertical extent via difference at column xc
    dd=np.abs(I-B).sum(axis=2)
    col=dd[:,int(xc)-3:int(xc)+4].mean(axis=1)
    rows=np.nonzero(col>0.5*np.median(col[np.argsort(col)[-150:]]))[0]
    top,bot=rows.min(),rows.max()
    cy=(top+bot)//2
    print('frame',i,'xc',round(xc,1),'top',top,'bot',bot,'ext',bot-top+1)
    for r in (cy+15, cy+30, cy+45):
        F=I[r,int(xc)-30:int(xc)+30].mean(axis=0)  # ball interior colour approx
        prof=[]
        for x in range(int(xc)-200,int(xc)+200):
            b=B[r,x]; v=F-b; a=np.dot(I[r,x]-b,v)/max(np.dot(v,v),1e-6)
            prof.append(a)
        prof=np.array(prof); prof=np.convolve(prof,np.ones(3)/3,'same')
        xs=np.arange(int(xc)-200,int(xc)+200)
        def cross(level,side):
            if side=='L':
                idx=np.nonzero(prof[:200]<level)[0]; k=idx[-1] if len(idx) else 0
            else:
                idx=np.nonzero(prof[200:]<level)[0]; k=200+idx[0]-1 if len(idx) else 399
            return xs[k]
        L10,L50,L90=cross(0.1,'L'),cross(0.5,'L'),cross(0.9,'L')
        R10,R50,R90=cross(0.1,'R'),cross(0.5,'R'),cross(0.9,'R')
        h=r-cy
        print('  row h=%d  L10-90 %d  R90-10 %d   halfw50 %.1f  mid50 %.1f  expected c(h)~sqrt(114.5^2-h^2)=%.1f'%(h,L90-L10,R10-R90,(R50-L50)/2,(R50+L50)/2,np.sqrt(max(114.5**2-h*h,0))))
