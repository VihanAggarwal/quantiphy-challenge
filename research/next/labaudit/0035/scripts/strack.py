# background-subtraction ball tracking in s renders, seeded per frame by x-render centres
import cv2, numpy as np, sys, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
v=sys.argv[1]; xv=sys.argv[2]; thr=int(sys.argv[3]) if len(sys.argv)>3 else 30
fr=np.load(f'{S}/f0035{v}.npy').astype(np.int16)
bg=np.median(fr,axis=0)
seeds=json.load(open(f'{S}/tr_{xv}.json'))
out={'sb':{},'bb':{}}
for key in ['sb','bb']:
    for ks,d in seeds[key].items():
        k=int(ks); f=fr[k]
        diff=np.abs(f-bg).max(2)
        m=(diff>thr).astype(np.uint8)
        R=int(0.9*d['major'])
        x0,y0=int(d['cx'])-R,int(d['cy'])-R
        roi=np.zeros_like(m); roi[max(y0,0):y0+2*R,max(x0,0):x0+2*R]=1
        m=m*roi
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
        if n<2: continue
        dd=[np.hypot(cen[j][0]-d['cx'],cen[j][1]-d['cy']) if st[j][4]>300 else 1e9 for j in range(1,n)]
        j=1+int(np.argmin(dd))
        comp=(lab==j).astype(np.uint8)
        cs,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=max(cs,key=cv2.contourArea)
        (ex,ey),(ma,MA),ang=cv2.fitEllipse(c); M=cv2.moments(c)
        A=cv2.contourArea(c)
        out[key][k]=dict(cx=M['m10']/M['m00'],cy=M['m01']/M['m00'],minor=min(ma,MA),major=max(ma,MA),A=A,w=int(st[j][2]),h=int(st[j][3]))
json.dump(out,open(f'{S}/tr_{v}.json','w'))
for k in range(49):
    s=[]
    for key in ['sb','bb']:
        d=out[key].get(k); x=seeds[key].get(str(k))
        s.append('%s %6.1f %6.1f min%5.1f maj%5.1f deq%5.1f w%d h%d (x-render min %.1f)'%(key,d['cx'],d['cy'],d['minor'],d['major'],np.sqrt(4*d['A']/np.pi),d['w'],d['h'],x['minor']) if d else key+' -')
    print(k,' | '.join(s))
