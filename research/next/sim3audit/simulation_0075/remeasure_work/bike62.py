from common import *
V=load('simulation_0062')
g=V.astype(np.float32).mean(3)
# template: front wheel + fork region at frame 60
y0,y1,x0,x1=560,625,1690,1760
T=g[60,y0:y1,x0:x1]
res=[]
for i in range(20,72):
    # search band
    S=g[i,y0-10:y1+10,:]
    r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(r)
    # subpixel parabola in x
    x=loc[0]; y=loc[1]
    if 0<x<r.shape[1]-1:
        a,b,c=r[y,x-1],r[y,x],r[y,x+1]; dx=0.5*(a-c)/(a-2*b+c)
    else: dx=0
    res.append((i,x+dx,y-10,mx))
res=np.array(res)
for row in res: print('%d %.2f %d %.3f'%tuple(row))
np.save('bike62_track.npy',res)
