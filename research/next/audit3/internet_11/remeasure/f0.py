import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
orb=cv2.ORB_create(6000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
def H_to(src_i,dst_i):
    k1,d1=orb.detectAndCompute(g[src_i],None); k2,d2=orb.detectAndCompute(g[dst_i],None)
    m=bf.match(d1,d2)
    s=np.float32([k1[x.queryIdx].pt for x in m]); d=np.float32([k2[x.trainIdx].pt for x in m])
    H,_=cv2.findHomography(s,d,cv2.RANSAC,1.5); return H
for i in (0,1,2,3,9,12,15):
    # background for frame i from frame 27 warped into frame i coords
    H=H_to(27,i)
    bgi=cv2.warpPerspective(fr[27],H,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    L=cv2.cvtColor(fr[i],cv2.COLOR_BGR2Lab).astype(np.float32); L0=cv2.cvtColor(bgi,cv2.COLOR_BGR2Lab).astype(np.float32)
    d=np.sqrt(((L-L0)**2).sum(axis=2)); d=cv2.GaussianBlur(d,(3,3),0)
    m=(d>25).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
    n,ll,st,cc=cv2.connectedComponentsWithStats(m); j=1+np.argmax(st[1:,4]); x,y,w,h,a=st[j]
    # vertical extent & center row via max-gradient on the column near the right part
    # right edge per row: rightmost crossing of 0.5*plateau, use rows below red line
    rights=[];lefts=[]
    for r in range(y+10,y+h-10):
        prof=d[r,:].astype(np.float64)
        inner=prof[max(x+w-150,0):x+w-90]
        plat=np.median(inner)
        if plat<30: continue
        thr=0.5*plat
        idx=np.nonzero(prof[:min(x+w+40,1919)]>thr)[0]
        if len(idx)==0: continue
        rr=idx[-1]; rx=rr+(prof[rr]-thr)/(prof[rr]-prof[rr+1])
        rights.append((r,rx))
        l=idx[0]
        if l>0: lefts.append((r,l-1+(thr-prof[l-1])/(prof[l]-prof[l-1])))
        else: lefts.append((r,np.nan))
    rights=np.array(rights); lefts=np.array(lefts)
    # center row = row of max right extent (smoothed)
    rs=np.convolve(rights[:,1],np.ones(9)/9,'same')
    k=np.argmax(rs[5:-5])+5
    mid=(lefts[:,1]+rights[:,1])/2
    print(i,'bbox',x,y,w,h,'max right edge %.1f at row %d'%(rs[k],rights[k,0]),' rows %d-%d'%(y,y+h),'left edge at that row %.1f'%np.nanmedian(lefts[max(k-4,0):k+5,1]),'median mid %.1f'%np.nanmedian(mid))
    # white line centre in frame i at rows y+h/2 .. use row 600 region
    for yy in (560,600,640):
        row=fr[i][yy-3:yy+4].astype(np.float32).mean(axis=0)
        wv=(row[:,0]-row[:,2])[1100:1300]; thr=(np.median(wv)+np.percentile(wv,97))/2
        xs=[q+(thr-wv[q])/(wv[q+1]-wv[q]) for q in range(len(wv)-1) if (wv[q]-thr)*(wv[q+1]-thr)<0]
        print('   white line y%d: %.1f-%.1f centre %.1f'%(yy,1100+xs[0],1100+xs[-1],1100+(xs[0]+xs[-1])/2))
