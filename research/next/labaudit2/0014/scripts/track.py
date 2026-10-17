import cv2, numpy as np, sys, json
sys.path.insert(0,'scripts')
from frames import load
out={}
for r in ['x','s','']:
    fr=load(r)
    bg=np.median(np.stack([f.astype(np.float32) for f in fr[28:49]]),0)
    res=[]
    prev=None
    for k in range(0,27):
        im=fr[k].astype(np.float32)
        d=np.abs(im-bg).sum(2)
        roi=np.zeros_like(d); roi[230:720,440:700]=1
        d=d*roi
        m=(d>40).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<=1: res.append(None); continue
        # choose largest component (near previous)
        cand=[i for i in range(1,n) if st[i,4]>60]
        if prev is not None:
            cand.sort(key=lambda i: np.hypot(*(cen[i]-prev))-0.02*st[i,4])
        else:
            cand.sort(key=lambda i:-st[i,4])
        i=cand[0]
        x,y,w,h,a=st[i]
        # weighted centroid using diff
        mm=(lab==i)
        ys,xs=np.nonzero(mm); ww=d[mm]
        wc=(float((xs*ww).sum()/ww.sum()), float((ys*ww).sum()/ww.sum()))
        prev=np.array(wc)
        res.append(dict(k=k,bbox=[int(x),int(y),int(w),int(h)],area=int(a),cen=[float(cen[i][0]),float(cen[i][1])],wcen=wc))
    out[r or 'o']=res
    print('render',r or 'o')
    for e in res:
        if e is None: print('none'); continue
        print(e['k'],e['bbox'],e['area'],np.round(e['cen'],1),np.round(e['wcen'],1))
json.dump(out,open('track_bgdiff.json','w'),indent=0)
