import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
F=frames('simulation_0240',1060,1920)[:49:6]
bg=np.median(F,axis=0).astype(np.float32)
g=cv2.cvtColor(bg.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)
Y0=1060
res=[]
for y in range(1070,1900,40):
    band=g[y-Y0-10:y-Y0+10, 40:1040]
    band=band-band.mean(axis=1,keepdims=True)
    # horizontal autocorrelation
    ac=np.zeros(200)
    for r in band:
        f=np.fft.rfft(r*np.hanning(len(r)),n=2048)
        a=np.fft.irfft(np.abs(f)**2)[:200]
        ac+=a/a[0]
    ac/=len(band)
    # width where autocorrelation drops to 0.5
    i=np.argmax(ac<0.5); w=i-1+(ac[i-1]-0.5)/(ac[i-1]-ac[i])
    # spectral centroid
    P=np.zeros(1025)
    for r in band:
        P+=np.abs(np.fft.rfft(r*np.hanning(len(r)),n=2048))**2
    fr=np.arange(1025)/2048
    sel=(fr>0.004)&(fr<0.25)
    cen=(P[sel]*fr[sel]).sum()/P[sel].sum()
    res.append((y,w,1/cen))
res=np.array(res)
np.set_printoptions(suppress=True,precision=2,linewidth=150)
print(res)
for j,nm in [(1,'ac-halfwidth'),(2,'1/centroid')]:
    for lo,hi in [(1070,1500),(1070,1900),(1200,1900)]:
        s=(res[:,0]>=lo)&(res[:,0]<=hi)
        p=np.polyfit(res[s,0],res[s,j],1)
        print(nm,lo,hi,'slope',p[0],'zero-crossing y_h =',-p[1]/p[0])
