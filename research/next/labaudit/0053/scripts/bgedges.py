import cv2, numpy as np
med=cv2.imread('median_o.png').astype(float)
g=cv2.GaussianBlur(med.mean(2),(0,0),1.0)
gx=np.zeros_like(g); gx[:,1:-1]=(g[:,2:]-g[:,:-2])/2
def track(x0,y0,y1,halfw=8,sign=None):
    pts=[]
    for y in range(y0,y1):
        xs=np.arange(int(x0)-halfw,int(x0)+halfw+1)
        p=gx[y,xs]
        if sign is None: i=np.argmax(np.abs(p))
        elif sign>0: i=np.argmax(p)
        else: i=np.argmin(p)
        if 0<i<len(p)-1 and abs(p[i])>4:
            a,b,c=p[i-1],p[i],p[i+1]; d=a-2*b+c
            pts.append((y,xs[i]+(0.5*(a-c)/d if d!=0 else 0)))
    pts=np.array(pts)
    A=np.c_[np.ones(len(pts)),pts[:,0]]
    sol,*_=np.linalg.lstsq(A,pts[:,1],rcond=None)
    for it in range(3):
        r=pts[:,1]-A@sol; keep=np.abs(r)<1.2
        sol,*_=np.linalg.lstsq(A[keep],pts[keep,1],rcond=None)
    return sol,keep.sum(),len(pts)
for name,x0,y0,y1 in [('cab_right',310,5,120),('cab_left',100,5,120),('pedestal',383,45,105),('pedestal2',390,45,105)]:
    for s in (1,-1):
        sol,k,n=track(x0,y0,y1,sign=s)
        x_mid=sol[0]+sol[1]*(y0+y1)/2
        print(name,s,'x=%.1f+%.4f*y'%tuple(sol),'n',k,n,'angle %.1f deg'%np.degrees(np.arctan(sol[1])),'x_mid %.1f'%x_mid)
    # predictions
    ym=(y0+y1)/2
    for vp in [(453,1379),(640,1395)]:
        print('   pred slope for VP',vp,'%.4f'%((vp[0]-x0)/(vp[1]-ym)))
