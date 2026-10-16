import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from slopeplane import *
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
ims=[cv2.imread(D+f'frames/x{i:02d}.png').astype(float) for i in range(2,18)]
im=np.median(np.stack(ims),0); cv2.imwrite(D+'median_x_rest_top.png',im.astype(np.uint8))
g=im.mean(2)
b,gg,r=im[...,0],im[...,1],im[...,2]
def topsil(x):
    col=g[330:400,x]; k=np.where(col>60)[0]; 
    if len(k)==0: return None
    k=k[0]; y=330+k-1+(60-col[k-1])/(col[k]-col[k-1]); return y
def pages_bottom(x):
    # darkest row (shadow line) between 386 and 400 under the pages
    col=g[384:402,x]; k=np.argmin(col); return 384+k, col[k]
out=[]
for x in range(735,846,5):
    t=topsil(x); pb,val=pages_bottom(x)
    out.append((x,t,pb,val))
    print(x, None if t is None else round(t,1), pb, round(val,1))
np.save(D+'scripts/book_top_scan.npy',np.array([(o[0],o[1] if o[1] else np.nan,o[2]) for o in out]))
