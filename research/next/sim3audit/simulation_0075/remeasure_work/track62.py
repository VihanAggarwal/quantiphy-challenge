from common import *
V=load('simulation_0062'); g=V.astype(np.float32).mean(3)
def track(ref, box, frames, xrange=None):
    x0,y0,x1,y1=box; T=g[ref,y0:y1,x0:x1]; out=[]
    for i in frames:
        S=g[i,y0-3:y1+3,:]
        r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
        _,mx,_,loc=cv2.minMaxLoc(r); x,y=loc
        dx=0
        if 0<x<r.shape[1]-1:
            a,b,c=r[y,x-1],r[y,x],r[y,x+1]; den=(a-2*b+c); dx=0.5*(a-c)/den if den!=0 else 0
        out.append((i,x+dx-x0,y-3,mx))
    return np.array(out)
van=track(60,(1290,470,1460,540),range(0,72))
for r in van: print('van %d %.2f %d %.3f'%tuple(r))
np.save('van62.npy',van)
