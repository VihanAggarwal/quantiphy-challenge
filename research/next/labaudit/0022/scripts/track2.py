import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
D='/home/user/quantiphy-challenge/research/next/labaudit/0022/'
out={}
for r in ['','s','x']:
    fr=np.load(S+f'fr0022{r}.npy').astype(np.float32)
    med=np.median(fr,axis=0)
    cv2.imwrite(D+f'median_{r or "o"}.png',med.astype(np.uint8))
    res=[]; prev=np.array([437.6,380.0])
    for i,im in enumerate(fr):
        d=np.abs(im-med).max(2)
        bright=im.min(2)  # white ball -> high min channel
        score=d*(bright>120)
        # search window around prev
        u0,v0=int(prev[0]),int(prev[1])
        win=score[max(0,v0-45):v0+60, max(0,u0-45):u0+45]
        m=(win>35).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        cands=[(k,st[k,4],cen[k]) for k in range(1,n) if st[k,4]>=20]
        if not cands:
            res.append(None); print(r,i,None); continue
        k,a,c=max(cands,key=lambda c:c[1])
        x,y,w,h=st[k,:4]
        c=c+np.array([max(0,u0-45),max(0,v0-45)])
        # intensity-weighted centroid of whitish pixels within box
        res.append([float(c[0]),float(c[1]),int(w),int(h),int(a)])
        prev=c
        print(r or 'o',i,np.round(c,1),w,h,a)
    out[r or 'o']=res
json.dump(out,open(S+'track_diff.json','w'))
