import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0148')
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in F]
# use gradient x images in a band
def gx(g): return cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3)
band=slice(430,800)
res=[]
for i in range(4,20):
    a=gx(G[i-1])[band]; b=gx(G[i])[band]
    # frame i content = frame i-1 shifted left by s: b[x]=a[x+s]
    best=None
    scores=[]
    for s in range(200,520):
        # compare over x in b region [1100, 1850-s] where both inside right opening? use full width 100..1900
        x0,x1=60,1900-s
        A=a[:,x0+s:x1+s]; B=b[:,x0:x1]
        num=(A*B).sum(); den=np.sqrt((A*A).sum()*(B*B).sum())+1e-6
        scores.append(num/den)
    scores=np.array(scores); k=np.argmax(scores)
    # subpixel
    if 0<k<len(scores)-1:
        d=0.5*(scores[k-1]-scores[k+1])/(scores[k-1]-2*scores[k]+scores[k+1])
    else: d=0
    top2=np.argsort(scores)[-5:]
    res.append((i,200+k+d,scores[k]))
    print(i,round(200+k+d,1),round(float(scores[k]),3), 'other peaks', sorted([(200+t, round(float(scores[t]),3)) for t in top2]))
