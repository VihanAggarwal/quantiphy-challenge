import cv2, numpy as np
med=cv2.imread('median_o.png').astype(np.float32)
g=med.mean(2)
gx=cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
# structure tensor in windows
win=41
Jxx=cv2.boxFilter(gx*gx,-1,(win,win)); Jyy=cv2.boxFilter(gy*gy,-1,(win,win)); Jxy=cv2.boxFilter(gx*gy,-1,(win,win))
lines=[]
# floor sample region: avoid objects, cables
mask=np.zeros(g.shape,bool)
for y in range(300,700,20):
    for x in range(170,1000,20):
        mask[y,x]=True
# exclude objects
excl=[(530,380,610,470),(600,550,730,680),(900,320,1060,420),(600,380,720,420),(850,640,1000,720),(880,550,940,590),(700,280,900,480)]
for x0,y0,x1,y1 in excl: mask[y0:y1,x0:x1]=False
# exclude right of right-wall junction roughly: y < 87+0.712(x-680)
yy,xx=np.mgrid[0:720,0:1280]
mask&= yy> 87+0.712*(xx-680)+20
for y,x in zip(*np.where(mask)):
    a,b,c=Jxx[y,x],Jyy[y,x],Jxy[y,x]
    # dominant gradient orientation
    th=0.5*np.arctan2(2*c,a-b)
    coh=np.sqrt((a-b)**2+4*c*c)/(a+b+1e-6)
    # line direction perpendicular to gradient
    d=np.array([-np.sin(th),np.cos(th)])
    lines.append((x,y,d[0],d[1],coh))
L=np.array(lines)
print(len(L),'coh median',np.median(L[:,4]))
L=L[L[:,4]>0.5]
# line eq: n.(p - p0)=0 with n=(-dy,dx)
def fit(L):
    n=np.c_[-L[:,3],L[:,2]]
    c=(n*L[:,:2]).sum(1)
    w=L[:,4]
    # minimize sum w (n.v - c)^2
    A=n*w[:,None]; b=c*w
    v,*_=np.linalg.lstsq(A,b,rcond=None)
    r=(n@v-c)
    return v,r
v,r=fit(L)
for it in range(3):
    # residual as angle: distance / dist to vp
    dist=np.hypot(L[:,0]-v[0],L[:,1]-v[1])
    ang=np.degrees(np.abs(r)/dist)
    keep=ang<3
    v,r2=fit(L[keep]); r=np.c_[-L[:,3],L[:,2]]@v-(np.c_[-L[:,3],L[:,2]]*L[:,:2]).sum(1)
print('carpet VP',v,'n used',keep.sum(),'of',len(L))
angs=np.degrees(np.arctan2(L[:,3],L[:,2]))
print('streak angle stats (deg, image)',np.percentile(angs,[10,50,90]))
for vpv,name in [((453,1379),'roll'),((640,1395),'noroll')]:
    F=711.
    dv=np.array([(vpv[0]-640)/F,(vpv[1]-360)/F,1])
    dc=np.array([(v[0]-640)/F,(v[1]-360)/F,1])
    print(name,'cos angle between carpet dir and vertical',dv@dc/np.linalg.norm(dv)/np.linalg.norm(dc))
np.save('carpet_lines.npy',L)
