import cv2, numpy as np
from geo import *
from slope3d import board_model, hit_plane
# column profiles of saturation (cover is bluish; board white; page block grey)
def profile(fr,x):
    im=cv2.imread(f'frames/{fr}.png'); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(float)
    s=hsv[:,x-3:x+4,1].mean(1); v=hsv[:,x-3:x+4,2].mean(1); return s,v
def edges(fr,x,y0,y1):
    s,v=profile(fr,x); seg=s[y0:y1]
    hi=np.percentile(seg,90); lo=np.percentile(seg,5); thr=(hi+lo)/2
    idx=np.nonzero(seg>thr)[0]
    a=idx[0]; b=idx[-1]
    ya=y0+a-1+(thr-seg[a-1])/(seg[a]-seg[a-1]); yb=y0+b+(seg[b]-thr)/(seg[b]-seg[b+1])
    return ya,yb
for route in ['stated','ruler']:
    M=board_model(route)
    for H in [0.0146]:
        print(route)
        for fr in ['o23','o24','o25','o26','o27','x24','x25','x26']:
            res=[]
            for x in [560,580,600,620]:
                fi=int(fr[1:]); 
                ya,yb=edges(fr,x,330,470)
                p0=M['B']+M['n']*H
                A=hit_plane(p0,M['n'],x,ya); B=hit_plane(p0,M['n'],x,yb)
                res.append((round(ya,1),round(yb,1),round(np.linalg.norm(A-B)*100,2)))
            print(' ',fr,res)
