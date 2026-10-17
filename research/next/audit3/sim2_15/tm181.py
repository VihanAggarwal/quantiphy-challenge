from util import *
fr=frames('0181'); g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
def track(ref, box, rng, search=80):
    x0,y0,w,h=box; T=g[ref][y0:y0+h,x0:x0+w]
    pos={ref:(x0,y0)}; 
    for direction in [1,-1]:
        cx,cy=x0,y0; 
        for i in (range(ref+1,rng[1]+1) if direction==1 else range(ref-1,rng[0]-1,-1)):
            # predict
            prev=pos[i-direction]; pp=pos.get(i-2*direction,prev)
            px=2*prev[0]-pp[0]; py=2*prev[1]-pp[1]
            X0=max(0,int(px)-search); Y0=max(0,int(py)-search)
            S=g[i][Y0:Y0+h+2*search, X0:X0+w+2*search]
            r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
            # subpixel
            mx,my=ml
            dx=dy=0
            if 0<mx<r.shape[1]-1: a,b,c=r[my,mx-1],r[my,mx],r[my,mx+1]; dx=0.5*(a-c)/(a-2*b+c)
            if 0<my<r.shape[0]-1: a,b,c=r[my-1,mx],r[my,mx],r[my+1,mx]; dy=0.5*(a-c)/(a-2*b+c)
            pos[i]=(X0+mx+dx,Y0+my+dy); 
            print(i,'%.2f %.2f score %.3f'%(pos[i][0],pos[i][1],mv))
    return pos
print('fall: patch from frame0 face')
P=track(0,(420,260,180,120),(0,8))
k=sorted(P); y=np.array([P[i][1] for i in k]); t=np.array(k)
p=np.polyfit(t,y,2); print('fall a px/f2 %.3f -> px/s2 %.0f -> px/m %.1f'%(2*p[0],2*p[0]*576,2*p[0]*576/9.81))
print('slide: patch from frame 20 face')
P2=track(20,(640,520,150,100),(10,37))
k=sorted(P2); xy=np.array([P2[i] for i in k]); t=np.array(k)
np.save if False else None
import json; json.dump({str(i):P2[i] for i in k},open(W+'tm181.json','w'))
