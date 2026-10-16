import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
D='/home/user/quantiphy-challenge/research/next/labaudit/0022/'
fr=np.load(S+'fr0022x.npy')
im=fr[30]
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
m=(im.max(2)>40)
gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(float)
def fitline(pts):
    pts=np.array(pts,float)
    for it in range(4):
        vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
        res=(pts[:,0]-x0)*vy-(pts[:,1]-y0)*vx
        keep=np.abs(res)<max(1.5,3*np.median(np.abs(res)))
        pts=pts[keep]
    res=(pts[:,0]-x0)*vy-(pts[:,1]-y0)*vx
    return np.array([vx,vy,x0,y0]),np.abs(res).max(),np.abs(res).mean()
# far edge: topmost mask pixel per column, subpixel by threshold crossing
far=[];left=[];right=[];near=[];nearbot=[]
for u in range(310,580):
    col=im[:,u].max(1).astype(float)
    v=np.argmax(col>40)
    # subpixel: interpolate crossing of half max between bg(~5) and table(~180)
    far.append((u,v))
for v in range(440,595):
    row=im[v].max(1).astype(float)
    u=np.argmax(row[:700]>40); left.append((u,v))
for v in range(385,500):
    row=im[v].max(1).astype(float)
    nz=np.where(row[:900]>40)[0]; right.append((nz.max(),v))
# near edge top surface: per column, scanning down from the ball path, find strongest negative brightness step above the mask bottom
for u in list(range(250,440))+list(range(530,650)):
    col=gray[:,u]
    nz=np.where(im[:,u].max(1)>40)[0]
    bot=nz[nz<700].max()
    seg=col[bot-25:bot+1]
    g=np.diff(seg)
    k=np.argmin(g)  # biggest drop (top -> front face darker)
    near.append((u,bot-25+k+0.5)); nearbot.append((u,bot))
out={}
for name,p in [('far',far),('left',left),('right',right),('near',near),('nearbot',nearbot)]:
    L,mx,mn=fitline(p); out[name]=L.tolist(); print(name,np.round(L,4),'maxres',round(mx,2),'meanres',round(mn,2))
def inter(a,b):
    a=np.array(a);b=np.array(b)
    A=np.array([[a[0],-b[0]],[a[1],-b[1]]]); t=np.linalg.solve(A,b[2:]-a[2:]); return a[2:]+t[0]*a[:2]
C={'FL':inter(out['far'],out['left']),'FR':inter(out['far'],out['right']),'NR':inter(out['near'],out['right']),'NL':inter(out['near'],out['left']),
   'NRb':inter(out['nearbot'],out['right']),'NLb':inter(out['nearbot'],out['left'])}
for k,v in C.items(): print(k,np.round(v,1))
json.dump({k:v.tolist() for k,v in C.items()},open(S+'corners.json','w'))
vis=im.copy()
for k,v in C.items(): cv2.circle(vis,tuple(int(x) for x in v),4,(0,0,255),-1)
for p in near[::5]: cv2.circle(vis,(int(p[0]),int(p[1])),1,(0,255,0),-1)
cv2.imwrite(D+'corners_x30.png',vis[330:660,180:720])
