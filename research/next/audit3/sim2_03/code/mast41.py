import cv2, numpy as np
exec(open('/home/user/quantiphy-challenge/research/next/audit3/sim2_03/code/cam41.py').read().split("print('--- beam")[0].replace('print(','(lambda *a,**k: None)('))
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0041.mp4')
F={}
k=0
while True:
    ok,fr=c.read()
    if not ok: break
    if k in (6,12,18,24,30,36,42,48,54): F[k]=fr.astype(int)
    k+=1
for k,fr in F.items():
    dx=(k-36)*-5.61; dy=(k-36)*-1.60
    # mast column: around x=290+dx; find brightest column (white mast) near y=850+dy
    yc=int(round(860+dy)); xc=int(round(291+dx))
    g=fr[:,:,1]
    # top: scan upward in columns xc-4..xc+4 for max brightness profile
    cols=range(xc-6,xc+7)
    prof=np.max(g[int(770+dy)-20:int(800+dy),xc-6:xc+7],axis=1).astype(float)
    y0=int(770+dy)-20
    bg=np.median(prof[:8]); pk=prof.max(); thr=(bg+pk)/2
    i=np.where(prof>thr)[0][0]
    top=y0+i-1+(thr-prof[i-1])/(prof[i]-prof[i-1])
    # foot: in the mast column (brightest G at y=870+dy), scan down until G drops (red roof)
    yy=int(round(870+dy)); xm=xc-6+int(np.argmax(g[yy,xc-6:xc+7]))
    col=g[yy:yy+30,xm].astype(float)
    j=np.where(col<100)[0][0]
    foot=yy+j-1+(col[j-1]-100)/(col[j-1]-col[j])
    # model: back-project foot at roof height ~3.8 m (approx above water), solve mast height
    P=back(np.array([xm,foot]),3.8,Hc)
    m=brentq(lambda mm: proj(P+np.array([0,0,mm]),Hc)[1]-top, 0.1, 20)
    print('frame %2d mast col %d top %.1f foot %.1f  dpx %.1f  -> mast above roof %.2f m'%(k,xm,top,foot,foot-top,m))
