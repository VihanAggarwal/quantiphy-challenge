import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
v=sys.argv[1]
c=cv2.VideoCapture(D+v+'.mp4'); M=[]
while True:
    ok,f=c.read()
    if not ok: break
    M.append((cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)[800:940,400:1000]<60).astype(np.float32))
def sh(a,b):
    A=np.fft.rfft2(a); B=np.fft.rfft2(b); cc=np.fft.irfft2(np.conj(A)*B,s=a.shape)
    iy,ix=np.unravel_index(np.argmax(cc),cc.shape); p=cc[iy,ix]; l=cc[iy,ix-1]; r=cc[iy,(ix+1)%cc.shape[1]]
    dx=ix+0.5*(l-r)/(l-2*p+r); return dx-cc.shape[1] if dx>cc.shape[1]/2 else dx
for lag in [18,19,37]:
    s=[sh(M[i],M[i+lag])/lag for i in range(0,len(M)-lag)]
    print(v,'lag',lag,' '.join('%.2f'%x for x in s))
