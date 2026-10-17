import cv2, numpy as np
bg=cv2.imread('research/next/audit3/internet_11/remeasure/png/bg47_ref15.png')
g=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY).astype(np.float32)
for (y0,y1) in [(0,200),(200,420),(560,760),(780,1060)]:
    band=g[y0:y1]
    # seams: dark thin lines; use negative of second derivative in x (ridge detector)
    dxx=cv2.Sobel(band,cv2.CV_32F,2,0,ksize=5)
    prof=np.clip(dxx,0,None).mean(axis=0)  # dark line -> positive second derivative
    prof=prof-np.convolve(prof,np.ones(61)/61,'same')
    x0,x1=300,1150
    p=prof[x0:x1]
    F=np.abs(np.fft.rfft(p*np.hanning(len(p))))
    fr=np.fft.rfftfreq(len(p))
    k=np.argmax(F[5:])+5
    # refine with autocorrelation
    ac=np.correlate(p,p,'full')[len(p)-1:]
    ac/=ac[0]
    pk=[i for i in range(20,200) if ac[i]>ac[i-1] and ac[i]>=ac[i+1]]
    print(y0,y1,'fft period %.1f'%(1/fr[k]),'ac peaks',[(i,round(ac[i],2)) for i in pk[:6]])
