import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/scripts')
from seg import masks,S
def track(v, soc_seed, frames_soc):
    fr=np.load(f'{S}/f0035{v}.npy')
    res={'bb':{},'sb':{}}
    prev=soc_seed
    for i,f in enumerate(fr):
        green,orange=masks(f)
        k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        o=cv2.morphologyEx(orange.astype(np.uint8),cv2.MORPH_OPEN,k)
        o=cv2.morphologyEx(o,cv2.MORPH_CLOSE,k)
        n,lab,st,cen=cv2.connectedComponentsWithStats(o,8)
        if n>1:
            j=1+np.argmax(st[1:,4])
            cs,_=cv2.findContours((lab==j).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            c=max(cs,key=cv2.contourArea)
            (ex,ey),(ma,MA),ang=cv2.fitEllipse(c)
            res['bb'][i]=dict(cx=float(cen[j][0]),cy=float(cen[j][1]),A=int(st[j][4]),minor=float(min(ma,MA)),major=float(max(ma,MA)),w=int(st[j][2]),h=int(st[j][3]))
        if i in frames_soc:
            m=(~green)&(~orange)
            m[680:,1020:]=False
            m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
            n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
            best=None
            for j in range(1,n):
                if 800<st[j][4]<6000:
                    d=np.hypot(cen[j][0]-prev[0],cen[j][1]-prev[1])
                    if best is None or d<best[0]: best=(d,j)
            if best and best[0]<80:
                j=best[1]
                # fill holes
                comp=(lab==j).astype(np.uint8)
                cs,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
                c=max(cs,key=cv2.contourArea)
                (ex,ey),(ma,MA),ang=cv2.fitEllipse(c)
                A=cv2.contourArea(c)
                res['sb'][i]=dict(cx=float(cen[j][0]),cy=float(cen[j][1]),A=float(A),minor=float(min(ma,MA)),major=float(max(ma,MA)),w=int(st[j][2]),h=int(st[j][3]))
                prev=cen[j]
    json.dump(res,open(f'{S}/tr_{v}.json','w'))
    return res
if __name__=='__main__':
    v=sys.argv[1]; sx,sy=float(sys.argv[2]),float(sys.argv[3]); a,b=int(sys.argv[4]),int(sys.argv[5])
    r=track(v,(sx,sy),range(a,b))
    for i in range(49):
        bb=r['bb'].get(i); sb=r['sb'].get(i)
        s1='bb %6.1f %6.1f min%5.1f maj%5.1f'%(bb['cx'],bb['cy'],bb['minor'],bb['major']) if bb else 'bb -'
        s2='sb %6.1f %6.1f min%5.1f maj%5.1f deq%5.1f'%(sb['cx'],sb['cy'],sb['minor'],sb['major'],np.sqrt(4*sb['A']/np.pi)) if sb else 'sb -'
        print(i,s1,'|',s2)
