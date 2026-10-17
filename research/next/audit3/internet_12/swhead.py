import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0037.mp4'
cap=cv2.VideoCapture(p); out=[]
i=0
while True:
    ok,im=cap.read()
    if not ok: break
    roi=im[750:1150].astype(np.int16)
    b,g,r=roi[...,0],roi[...,1],roi[...,2]
    m=((np.abs(r-g)<10)&(np.abs(g-b)<10)&(g>70)&(g<150)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); out.append((i,cen[k,0],cen[k,1]+750,st[k,4],st[k,2],st[k,3]))
    else: out.append((i,np.nan,np.nan,0,0,0))
    i+=1
O=np.array(out)
np.savetxt('sw_head.txt',O,fmt='%.1f')
for r in O[::6]: print('%3d x %.0f y %.0f area %d w %d h %d'%tuple(r))
def at(t):
    f=t*24; return np.interp(f,O[:,0],O[:,1])
# local linear fit around targets
def fit(fc,hw=4):
    sel=(O[:,0]>=fc-hw)&(O[:,0]<=fc+hw)&(O[:,3]>500)
    c=np.polyfit(O[sel,0],O[sel,1],1); return np.polyval(c,fc)
for hw in [0,3,6]:
    if hw==0: a,b,c=at(0),at(2.07),at(5.2)
    else: a,b,c=fit(0,hw),fit(49.68,hw),fit(124.8,hw)
    s=0.00243
    print('hw',hw,'x0 %.0f x1 %.0f x2 %.0f'%(a,b,c),'v01 %.3f v12 %.3f v02 %.3f'%((b-a)*s/2.07,(c-b)*s/3.13,(c-a)*s/5.2))
