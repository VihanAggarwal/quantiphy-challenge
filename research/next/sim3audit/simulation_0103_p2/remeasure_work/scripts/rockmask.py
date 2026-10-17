from vio import *
import cv2
def rock_mask(v,k,thr=250,keep='largest'):
    f=frame(v,k).astype(int)
    m=(f.min(axis=2)<thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    i=1+np.argmax(st[1:,4])
    r=(lab==i).astype(np.uint8)
    # fill holes
    cs,_=cv2.findContours(r,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    out=np.zeros_like(r); cv2.drawContours(out,cs,-1,1,-1)
    return out, max(cs,key=cv2.contourArea)[:,0,:]
if __name__=='__main__':
    import sys
    v=sys.argv[1]; k=int(sys.argv[2])
    m,c=rock_mask(v,k)
    ys,xs=np.nonzero(m)
    print(v,k,'x',xs.min(),xs.max(),'y',ys.min(),ys.max(),'area',m.sum())
    H,Wd=m.shape
    print('edge touches: left',m[:,0].sum(),'right',m[:,-1].sum(),'top',m[0].sum(),'bottom',m[-1].sum())
    # rightmost/leftmost points
    i=np.argmax(c[:,0]); j=np.argmin(c[:,0]); t=np.argmin(c[:,1]); b=np.argmax(c[:,1])
    print('rightmost',c[i],'leftmost',c[j],'top',c[t],'bottom',c[b])
    np.save(W+'rockcontour_%s_%d.npy'%(v,k),c)
    cv2.imwrite(W+'rockmask_%s_%d.png'%(v,k),m*255)
