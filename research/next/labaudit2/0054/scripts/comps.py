from common import *
import sys
def comps(v,k,minA=20,maxA=4000):
    im=frames(v)[k].astype(np.int32)
    if v.endswith('x') and v.startswith('a'):
        bg=np.array([0,255,0]); d=np.abs(im-bg).sum(2); m=(d>120).astype(np.uint8)
    else:
        m=(im.sum(2)>60).astype(np.uint8)
    m[690:,1100:]=0  # watermark
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    out=[]
    for i in range(1,n):
        A=st[i,4]
        if A<minA or A>maxA: continue
        ys,xs=np.nonzero(lab==i)
        col=im[ys,xs].mean(0)  # BGR
        out.append(dict(i=i,x=cen[i][0],y=cen[i][1],w=st[i,2],h=st[i,3],A=A,B=col[0],G=col[1],R=col[2],x0=st[i,0],y0=st[i,1]))
    return out,lab
if __name__=='__main__':
    v=sys.argv[1]; ks=range(int(sys.argv[2]),int(sys.argv[3]))
    for k in ks:
        out,_=comps(v,k)
        for o in out:
            print(v,k,cap(k),'(%.1f,%.1f) %dx%d A=%d BGR=(%d,%d,%d)'%(o['x'],o['y'],o['w'],o['h'],o['A'],o['B'],o['G'],o['R']))
