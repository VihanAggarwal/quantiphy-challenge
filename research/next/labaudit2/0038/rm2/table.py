import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/'
fr=[cv2.imread(D+'fx/%02d.jpg'%i).astype(np.float32) for i in range(0,49,3)]
bg=np.median(np.stack(fr),axis=0).astype(np.uint8)
cv2.imwrite(D+'bg_x.png',bg)
g=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY).astype(np.float32)
mask=g>40
# top boundary of mask per column (first True from top) in table area rows 400..650
top=[]
for x in range(200,1150):
    col=mask[400:650,x]
    ys=np.where(col)[0]
    if len(ys): top.append((x,400+ys[0]))
top=np.array(top,float)
# front edge: for each column, find strongest bright->dark transition (gradient) in rows 520..600
gy=cv2.Sobel(cv2.GaussianBlur(g,(5,5),0),cv2.CV_32F,0,1,ksize=5)
front=[]
for x in range(240,1100):
    # expected front line approx y = 538 + (x-211)*(587-538)/(1139-211)
    ye=538+(x-211)*(49/928.)
    y0=int(ye-12); y1=int(ye+12)
    k=np.argmin(gy[y0:y1,x])  # bright above, dark below -> negative gy
    front.append((x,y0+k))
front=np.array(front,float)
np.save(D+'top.npy',top); np.save(D+'front.npy',front)
def fitline(p):
    vx,vy,x0,y0=cv2.fitLine(p.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
    return np.array([vx,vy,x0,y0])
# segments of the top boundary
L=top[(top[:,0]>225)&(top[:,0]<430)]
B=top[(top[:,0]>480)&(top[:,0]<900)]
R=top[(top[:,0]>940)&(top[:,0]<1120)]
# remove objects from back edge (bottle/cup cover back edge?) : keep points close to robust line
def robust(p,it=3):
    l=fitline(p)
    for _ in range(it):
        n=np.array([-l[1],l[0]]); d=(p-l[2:])@n
        p=p[np.abs(d)<2.0]; l=fitline(p)
    return l,p
lines={}
for name,p in [('left',L),('back',B),('right',R),('front',front)]:
    l,pp=robust(p); lines[name]=l
    print(name, 'n=%d'%len(pp), 'dir=(%.4f,%.4f) pt=(%.1f,%.1f)'%tuple(l))
def inter(a,b):
    A=np.array([[a[0],-b[0]],[a[1],-b[1]]]); t=np.linalg.solve(A,b[2:]-a[2:]); return a[2:]+t[0]*a[:2]
C={'FL':inter(lines['left'],lines['front']),'BL':inter(lines['left'],lines['back']),'BR':inter(lines['back'],lines['right']),'FR':inter(lines['right'],lines['front'])}
for k,v in C.items(): print(k,v)
np.save(D+'corners.npy',np.array([C['FL'],C['FR'],C['BR'],C['BL']]))
vis=bg.copy()
for p in front[::5]: cv2.circle(vis,(int(p[0]),int(p[1])),1,(0,0,255),-1)
for p in top[::5]: cv2.circle(vis,(int(p[0]),int(p[1])),1,(0,255,0),-1)
for k,v in C.items(): cv2.circle(vis,(int(round(v[0])),int(round(v[1]))),4,(255,0,255),1)
cv2.imwrite(D+'table_vis.jpg',vis[380:660,150:1180])
