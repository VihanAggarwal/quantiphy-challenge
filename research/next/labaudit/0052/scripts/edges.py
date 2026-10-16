import cv2, numpy as np, sys
sys.path.insert(0,'scripts')
F=711.;CX=640.;CY=360.
def rays(p,f=F):
    p=np.asarray(p,float); d=np.c_[(p[:,0]-CX)/f,(p[:,1]-CY)/f,np.ones(len(p))]; return d/np.linalg.norm(d,axis=1)[:,None]
def ang(p,q,f=F):
    r=rays([p,q],f); return np.arccos(np.clip(r[0]@r[1],-1,1))
def edge_row(img,y,xa,xb,band=2):
    g=cv2.GaussianBlur(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32),(3,3),0)
    prof=g[y-band:y+band+1].mean(0)
    d=np.abs(np.gradient(prof))
    xs=np.arange(xa,xb); i=xs[np.argmax(d[xa:xb])]
    # subpixel parabola
    a,b,c=d[i-1],d[i],d[i+1]; off=0.5*(a-c)/(a-2*b+c) if (a-2*b+c)!=0 else 0
    return i+off
def edge_col(img,x,ya,yb,band=2):
    g=cv2.GaussianBlur(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32),(3,3),0)
    prof=g[:,x-band:x+band+1].mean(1)
    d=np.abs(np.gradient(prof))
    ys=np.arange(ya,yb); i=ys[np.argmax(d[ya:yb])]
    a,b,c=d[i-1],d[i],d[i+1]; off=0.5*(a-c)/(a-2*b+c) if (a-2*b+c)!=0 else 0
    return i+off
def phys(A,r):
    s=np.sin(A/2); R=r*s/(1-s); return 2*R, A*r
cases=[ # name, path, rows, left window, right window, stated range
 ('0052 t=1.0 n24','frames/o_24.png',range(530,561,5),(488,512),(632,656),2.612),
 ('0052 t=1.0 n23','frames/o_23.png',range(525,556,5),(495,525),(630,660),None),
 ('0052 t=1.0 n25','frames/o_25.png',range(535,566,5),(480,510),(632,662),None),
 ('0047 t=1.0 n24','frames/c0047_24.png',range(530,561,5),(438,460),(578,600),2.4985),
 ('0061 t=0.6 n14','frames/c0061_14.png',range(555,586,5),(474,498),(640,664),2.133),
 ('0061 t=0.6 n15','frames/c0061_15.png',range(550,581,5),(485,510),(645,670),2.133),
]
for name,p,rows,lw,rw,r in cases:
    img=cv2.imread(p)
    res=[]
    for y in rows:
        L=edge_row(img,y,*lw); R=edge_row(img,y,*rw); res.append((y,L,R,R-L,ang((L,y),(R,y))))
    res=np.array(res)
    i=np.argmax(res[:,3])
    y,L,R,w,A=res[i]
    s='%-16s widest row y=%d L=%.1f R=%.1f w=%.1f px  2alpha=%.4f'%(name,y,L,R,w,A)
    if r: 
        d,le=phys(A,r); s+='  -> physical diam %.1f cm, label-emul (A*r) %.1f cm'%(100*d,100*le)
    print(s, ' widths:',np.round(res[:,3],1))
