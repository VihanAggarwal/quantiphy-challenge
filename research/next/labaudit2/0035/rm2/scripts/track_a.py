# Independent soccer-ball centre track in render 'a' (blurred grey background): bright/dark threshold in a window.
import cv2, numpy as np, json
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0035/rm2/track_ax.json'))
def cap(i): return int(np.floor(i*25/24+0.5))
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0035a.mp4'); F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(f)
rows=[]
for i in range(27,48):
    d=T[str(i)]['sb']; x0,y0=int(d['cxw']),int(d['cyw'])
    W=45
    crop=F[i][y0-W:y0+W,x0-W:x0+W]
    g=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY).astype(int)
    bgv=np.median(np.r_[g[:5].ravel(),g[-5:].ravel(),g[:,:5].ravel(),g[:,-5:].ravel()])
    m=((g>bgv+45)|(g<bgv-60)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+int(np.argmax(st[1:,4]))
    mm=(lab==k).astype(np.uint8)
    cnt,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    hull=cv2.convexHull(max(cnt,key=cv2.contourArea))
    filled=np.zeros_like(mm); cv2.fillPoly(filled,[hull],1)
    ys,xs=np.nonzero(filled)
    cx=xs.mean()+x0-W; cy=ys.mean()+y0-W; deq=2*np.sqrt(filled.sum()/np.pi)
    rows.append((cap(i),cx,cy,deq,d['cxw'],d['cyw']))
rows=np.array(rows)
for r in rows: print('j%2d a:(%.2f,%.2f) deq %.1f | ax:(%.2f,%.2f)  diff (%.2f,%.2f)'%(r[0],r[1],r[2],r[3],r[4],r[5],r[1]-r[4],r[2]-r[5]))
m=(rows[:,0]>=31)
for k,nm in ((1,'u_a'),(2,'v_a'),(4,'u_ax'),(5,'v_ax')):
    print(nm,'slope px/capture-frame %.3f'%np.polyfit(rows[m,0],rows[m,k],1)[0])
