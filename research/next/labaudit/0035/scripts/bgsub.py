import cv2, numpy as np, sys, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
def run(v, seeds, thr=28, maxjump=60, rad=55):
    fr=np.load(f'{S}/f0035{v}.npy').astype(np.int16)
    bg=np.median(fr,axis=0)
    out={}
    for key,(k0,k1,seed) in seeds.items():
        prev=np.array(seed,float); out[key]={}
        for k in range(k0,k1):
            d=np.abs(fr[k]-bg).max(axis=2)
            m=(d>thr).astype(np.uint8)
            # restrict to ROI around prev
            x0,y0=int(max(prev[0]-rad-40,0)),int(max(prev[1]-rad-40,0))
            roi=np.zeros_like(m); roi[y0:int(prev[1]+rad+40),x0:int(prev[0]+rad+40)]=1
            m=m*roi
            m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
            m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
            n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
            best=None
            for j in range(1,n):
                if st[j][4]<500: continue
                dd=np.hypot(*(cen[j]-prev))
                if best is None or dd<best[0]: best=(dd,j)
            if best is None or best[0]>maxjump: continue
            j=best[1]; comp=(lab==j).astype(np.uint8)
            cs,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            c=max(cs,key=cv2.contourArea)
            filled=np.zeros_like(comp); cv2.drawContours(filled,[c],-1,1,-1)
            (ex,ey),(ma,MA),ang=cv2.fitEllipse(c)
            A=filled.sum(); M=cv2.moments(filled)
            cx,cy=M['m10']/M['m00'],M['m01']/M['m00']
            out[key][k]=dict(cx=cx,cy=cy,A=float(A),minor=float(min(ma,MA)),major=float(max(ma,MA)),w=int(st[j][2]),h=int(st[j][3]))
            prev=np.array([cx,cy])
    json.dump(out,open(f'{S}/tr_{v}.json','w'))
    return out
if __name__=='__main__':
    v=sys.argv[1]
    seeds=json.loads(sys.argv[2])
    out=run(v,{k:tuple(x[:2])+(tuple(x[2]),) for k,x in seeds.items()})
    for k in range(49):
        s=[]
        for key in out:
            d=out[key].get(k)
            s.append('%s %6.1f %6.1f min%5.1f maj%5.1f deq%5.1f'%(key,d['cx'],d['cy'],d['minor'],d['major'],np.sqrt(4*d['A']/np.pi)) if d else key+' -')
        print(k,' | '.join(s))
