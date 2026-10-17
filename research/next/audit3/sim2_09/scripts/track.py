from load import *
import sys
S=0.438/120.2
def track(v):
    fr=load(v)
    N=len(fr)
    bg=fr[79].copy()
    bg[400:600,550:750]=fr[0][400:600,550:750]
    # Route A: positive-brightness diff mask centroid & bbox
    A=[];B=[]
    tmpl=fr[0][423-75:423+75,1666-75:1666+70] if v=='x' else None
    # template from 0222-like end frame: take vacuum from last frame
    cy,cx=(500,650) if True else None
    T=fr[79][cy-66:cy+66,cx-66:cx+66]
    for i in range(N):
        d=fr[i]-bg
        m=(d>40).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n>1:
            k=np.argmax(st[1:,4])+1
            x,y,w,h,a=st[k]
            A.append((cen[k][0],cen[k][1],x,y,w,h,a))
        else: A.append((np.nan,)*7)
        r=cv2.matchTemplate(fr[i],T,cv2.TM_CCOEFF_NORMED)
        _,mv,_,ml=cv2.minMaxLoc(r)
        x,y=ml
        dx=dy=0
        if 0<x<r.shape[1]-1:
            l,c,rr=r[y,x-1],r[y,x],r[y,x+1]; dx=0.5*(l-rr)/(l-2*c+rr)
        if 0<y<r.shape[0]-1:
            l,c,rr=r[y-1,x],r[y,x],r[y+1,x]; dy=0.5*(l-rr)/(l-2*c+rr)
        B.append((x+dx+66,y+dy+66,mv))
    return np.array(A),np.array(B)
if __name__=='__main__':
    for v in ['simulation_0221','simulation_0222']:
        A,B=track(v)
        np.save(f'{v}_A.npy',A); np.save(f'{v}_B.npy',B)
        for i in range(0,80,4): print(v,i,np.round(A[i],1),np.round(B[i],2))
