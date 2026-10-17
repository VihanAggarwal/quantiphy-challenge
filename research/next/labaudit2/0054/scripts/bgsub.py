from common import *
import sys
def bg(v):
    L=frames(v); return np.median(np.stack(L[::2]),0).astype(np.int16)
def comps(v,k,B,box,thr=45,minA=40):
    im=frames(v)[k].astype(np.int16); x0,y0,x1,y1=box
    d=np.abs(im-B).sum(2); m=(d>thr).astype(np.uint8); mm=np.zeros_like(m); mm[y0:y1,x0:x1]=m[y0:y1,x0:x1]
    mm=cv2.morphologyEx(mm,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(mm)
    out=[]
    for i in range(1,n):
        if st[i,4]<minA: continue
        ys,xs=np.nonzero(lab==i); col=im[ys,xs].mean(0)
        hsv=cv2.cvtColor(im[ys,xs].astype(np.uint8)[None],cv2.COLOR_BGR2HSV)[0].mean(0)
        out.append((cen[i][0],cen[i][1],st[i,2],st[i,3],st[i,4],col,hsv))
    return out
if __name__=='__main__':
    v=sys.argv[1]; box=tuple(map(int,sys.argv[2].split(','))); B=bg(v)
    for k in range(int(sys.argv[3]),int(sys.argv[4])):
        for c in comps(v,k,B,box):
            print(v,k,cap(k),'(%.1f,%.1f) %dx%d A=%d BGR=(%d,%d,%d) HSV=(%d,%d,%d)'%(c[0],c[1],c[2],c[3],c[4],*c[5],*c[6]))
