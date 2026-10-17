import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f36/'
out={}
for v in ['captured_0036','captured_0036s','captured_0036x']:
    F=[cv2.imread(S+f'{v}/f{k:02d}.png') for k in range(49)]
    bg=np.median(np.stack(F[41:49]),axis=0).astype(np.float32)
    res={}
    prev=(415,423)
    for k in range(49):
        im=F[k].astype(np.float32)
        d=np.abs(im-bg).max(axis=2)
        g=im.mean(2)
        hsv=cv2.cvtColor(F[k],cv2.COLOR_BGR2HSV)
        # brightness-based ball mask: bright, low sat
        white=(hsv[...,2]>140)&(hsv[...,1]<70)
        m=((d>30)&white).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        best=None
        for i in range(1,n):
            x,y,w,h,a=st[i]
            if a<60: continue
            if y>650 and x>1000: continue
            dist=np.hypot(cen[i][0]-prev[0],cen[i][1]-prev[1])
            if dist>120: continue
            if best is None or a>best[0]: best=(a,i)
        if best is None: continue
        i=best[1]; x,y,w,h,a=st[i]
        prev=tuple(cen[i])
        res[k]=dict(cx=float(cen[i][0]),cy=float(cen[i][1]),x0=int(x),y0=int(y),w=int(w),h=int(h),a=int(a))
    out[v]=res
    for k in sorted(res):
        r=res[k]; print(v[-2:],k,'c=(%.1f,%.1f) bb x%d-%d y%d-%d w%d h%d a%d'%(r['cx'],r['cy'],r['x0'],r['x0']+r['w'],r['y0'],r['y0']+r['h'],r['w'],r['h'],r['a']))
json.dump(out,open('scripts/trk_bg.json','w'))
