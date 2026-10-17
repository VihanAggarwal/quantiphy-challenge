import cv2, numpy as np

c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0031x.mp4')
F=[]
while True:
    ok,x=c.read()
    if not ok: break
    F.append(x)
img=F[48].astype(int)
# mask of non-black
m=(img.sum(2)>60).astype(np.uint8)
m[:380]=0; m[530:]=0
# the table top+edge region: find per-row extents
rows={}
for y in range(400,530):
    xs=np.where(m[y])[0]
    if len(xs): rows[y]=(xs.min(),xs.max())
for y in range(415,515,3): print(y, rows.get(y))
ys=np.arange(431,481); xl=np.array([rows[y][0] for y in ys]); 
L=np.polyfit(ys,xl,1)
ys2=np.arange(431,481); xr=np.array([rows[y][1] for y in ys2]); R=np.polyfit(ys2,xr,1)
print('left x=%.4f*y+%.2f'%tuple(L),'right x=%.4f*y+%.2f'%tuple(R))
# back edge: top-most y per column
bx=np.arange(600,820,2); by=[]
for x in bx:
    yy=np.where(m[400:470,x])[0]; by.append(400+yy.min())
B=np.polyfit(bx,by,1); print('back y=%.5f*x+%.2f'%tuple(B))
# front top edge: brightness drop
g=cv2.cvtColor(F[48],cv2.COLOR_BGR2GRAY).astype(float)
fx=np.arange(520,900,4); fy=[]
for x in fx:
    col=g[470:510,x]; d=np.diff(col); k=np.argmin(d); fy.append(470+k+0.5)
fy=np.array(fy); Fr=np.polyfit(fx,fy,1); print('front y=%.5f*x+%.2f'%tuple(Fr), np.std(fy-np.polyval(Fr,fx)))
def inter(Lx, Ly):
    # x = a*y+b ; y = c*x+d
    a,b=Lx; cc,d=Ly
    y=(cc*b+d)/(1-cc*a); x=a*y+b; return np.array([x,y])
P=np.array([inter(L,B),inter(R,B),inter(R,Fr),inter(L,Fr)])
print(P)
np.save('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/corners.npy',P)
