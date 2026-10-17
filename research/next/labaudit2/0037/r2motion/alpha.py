import cv2,numpy as np,json
from track import load
tr=json.load(open('tracks.json'))
res={}
for sfx,key in [('','a'),('s','s'),('x','x')]:
    fr=load(sfx)
    med=np.median(np.stack(fr[::2]),axis=0).astype(np.float32)
    ref=tr['s']
    res[key]={}
    for i in range(21,49):
        r=ref[i]; cx,cy=int(r['cx']),int(r['cy'])
        x0,y0=cx-50,cy-50
        F=fr[i][y0:y0+101,x0:x0+101].astype(np.float32); B=med[y0:y0+101,x0:x0+101]
        # background for this frame: use median but ball might be in median? median over 25 frames, ball moves -> fine
        W=np.array([238,238,238],np.float32)  # assumed ball colour (bright)
        den=(W-B); den=np.where(np.abs(den)<25,np.nan,den)
        al=np.nanmedian((F-B)/den,axis=2)
        al=np.nan_to_num(al,nan=0.0)
        al=np.clip(al,0,1.2)
        # keep connected region around ball: threshold 0.15, component nearest center
        m=(al>0.15).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: continue
        d=[np.hypot(cen[k][0]-50,cen[k][1]-50) if st[k,4]>30 else 1e9 for k in range(1,n)]
        k=1+int(np.argmin(d))
        mk=cv2.dilate((lab==k).astype(np.uint8),np.ones((5,5),np.uint8)).astype(bool)
        w=al*mk
        ys,xs=np.mgrid[0:101,0:101]
        mx=(w*xs).sum()/w.sum(); my=(w*ys).sum()/w.sum()
        res[key][i]=(x0+mx,y0+my,float(w.sum()))
json.dump(res,open('alpha.json','w'),indent=1)
for i in range(21,49):
    s='%2d'%i
    for key in 'asx':
        if i in res[key]: s+='  %s:(%6.1f,%6.1f) A=%6.0f'%(key,*res[key][i])
    t=tr['s'][i]; s+='  trk_s:(%6.1f,%6.1f)'%(t['cx'],t['cy'])
    print(s)
