import cv2,numpy as np
v='data/QuantiPhy/simulation_0118.mp4'
c=cv2.VideoCapture(v); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[650:800].astype(np.int16))
S=np.stack(fr); bg=np.median(S,0)
L=[]
for f in range(len(fr)):
    d=np.abs(S[f]-bg).max(2)
    m=(d>25).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    i=1+np.argmax(st[1:,4]); x,y,w,h,a=st[i]
    # include other comps overlapping in rows close by
    L.append((f,x,x+w-1,y+650,y+h-1+650,a))
L=np.array(L)
for r in L[::10]: print(r)
t=L[:,0]
for k,name in [(1,'left'),(2,'right')]:
    p=np.polyfit(t[5:-5],L[5:-5,k],1); print(name,'px/frame %.4f rms %.2f'%(p[0],np.std(L[5:-5,k]-np.polyval(p,t[5:-5]))))
print('length px median',np.median(L[:,2]-L[:,1]+1),'height',np.median(L[:,4]-L[:,3]+1))
g=[cv2.cvtColor(x.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32) for x in fr]
x60=L[L[:,0]==60][0]
T=g[60][40:110,int(x60[1])-5:int(x60[2])+5]
xs=[]
for f in range(len(g)):
    r=cv2.matchTemplate(g[f],T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
    j=ml[0]; i=ml[1]; dx=(r[i,j-1]-r[i,j+1])/(2*(r[i,j-1]-2*r[i,j]+r[i,j+1])) if 0<j<r.shape[1]-1 else 0
    xs.append(j+dx)
xs=np.array(xs); tt=np.arange(len(xs))
p=np.polyfit(tt,xs,1); print('template px/frame %.4f rms %.3f x0..x120 %.2f'%(p[0],np.std(xs-np.polyval(p,tt)),xs[-1]-xs[0]))
print(np.round(np.diff(xs[:4]),2),np.round(np.diff(xs[-4:]),2))
