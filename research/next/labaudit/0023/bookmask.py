import cv2, numpy as np
def cover_mask(fr):
    im=cv2.imread(f'frames/{fr}.png'); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
    m=((hsv[...,0]>=82)&(hsv[...,0]<=108)&(hsv[...,1]>=22)&(hsv[...,2]>=140)).astype(np.uint8)
    m[:300]=0; m[560:]=0; m[:, :400]=0; m[:, 800:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: return m*0
    k=1+np.argmax(st[1:,4]); return (lab==k).astype(np.uint8)
if __name__=='__main__':
    for pre in ['o','x']:
        print(pre)
        for i in range(0,49):
            m=cover_mask(f'{pre}{i:02d}'); ys,xs=np.nonzero(m)
            if len(xs)==0: print(i,'none'); continue
            print(i, 'area',len(xs),'x',xs.min(),xs.max(),'y',ys.min(),ys.max(),'cen',round(xs.mean(),1),round(ys.mean(),1))
