import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
out={}
for r in ['','s','x']:
    fr=np.load(S+f'fr0022{r}.npy')
    res=[]
    prev=None
    for i,im in enumerate(fr):
        hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
        m=((hsv[...,2]>185)&(hsv[...,1]<70)).astype(np.uint8)
        m[640:,1000:]=0
        if r!='x':
            m[:, 700:]=0; m[:300,:]=0
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        cands=[(k,st[k,4],cen[k]) for k in range(1,n) if 15<=st[k,4]<=600]
        if prev is not None:
            cands=[c for c in cands if np.hypot(*(c[2]-prev))<40]
        if not cands:
            res.append(None); continue
        k,a,c=max(cands,key=lambda c:c[1])
        x,y,w,h=st[k,:4]
        res.append([float(c[0]),float(c[1]),int(w),int(h),int(a)])
        prev=c
    out[r or 'o']=res
    for i,rr in enumerate(res):
        print(r or 'o',i,rr)
json.dump(out,open(S+'track_white.json','w'))
