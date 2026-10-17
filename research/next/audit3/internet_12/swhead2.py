import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0037.mp4'
R=np.loadtxt('sw_track.txt')
cap=cv2.VideoCapture(p); out=[]
i=0
while True:
    ok,im=cap.read()
    if not ok: break
    hx=int(R[i,3]); x0=max(hx-50,0); x1=hx+350
    roi=im[800:1150,x0:x1].astype(np.int16)
    b,g,r=roi[...,0],roi[...,1],roi[...,2]
    m=((np.abs(r-g)<12)&(np.abs(g-b)<12)&(g>60)&(g<160)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); out.append((i,cen[k,0]+x0,cen[k,1]+800,st[k,4],st[k,2],st[k,3]))
    else: out.append((i,np.nan,np.nan,0,0,0))
    i+=1
O=np.array(out)
np.savetxt('sw_head.txt',O,fmt='%.1f')
for r in O[::4]: print('%3d x %.0f y %.0f area %d w %d h %d'%tuple(r))
good=O[:,3]>600
def fit(fc,hw):
    sel=(O[:,0]>=fc-hw)&(O[:,0]<=fc+hw)&good
    c=np.polyfit(O[sel,0],O[sel,1],1); return np.polyval(c,fc)
s=0.00243
for hw in [2,4,6]:
    a,b,c=fit(0,hw),fit(49.68,hw),fit(124.8,hw)
    print('hw',hw,'x0 %.0f x1 %.0f x2 %.0f'%(a,b,c),'v01 %.3f v12 %.3f v02 %.3f'%((b-a)*s/2.07,(c-b)*s/3.13,(c-a)*s/5.2))
