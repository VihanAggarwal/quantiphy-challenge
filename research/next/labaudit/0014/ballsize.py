import cv2, numpy as np
def width(row):
    # distance from green: use green-ness metric G - (R+B)/2
    g=row[:,1].astype(float)-(row[:,0].astype(float)+row[:,2].astype(float))/2
    # inside ball g small (~ -10..5), background g large (~40)
    bgv=np.median(np.r_[g[:5],g[-5:]]); inv=np.median(g[len(g)//2-3:len(g)//2+3])
    thr=(bgv+inv)/2
    inside=np.where(g<thr)[0]
    # subpixel edges
    i0=inside.min(); i1=inside.max()
    x0=i0-1+(g[i0-1]-thr)/(g[i0-1]-g[i0])
    x1=i1+(g[i1]-thr)/(g[i1]-g[i1+1])
    return x1-x0, x0, x1, bgv, inv
for R in ['rs','rx','ro']:
  for f in [0,3,4,8,9]:
    im=cv2.imread(f'frames/{R}_{f:02d}.png')
    ws=[]
    for y in range(292,301):
        row=im[y,505:585]
        try:
            w,x0,x1,b,i=width(row); ws.append((y,round(w,1),round(x0+505,1),round(x1+505,1)))
        except Exception as e: pass
    print(R,f,ws)
