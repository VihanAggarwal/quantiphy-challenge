# Route 2: A2 level camera. Pixel acceleration of a falling object (g=9.8) + its table-contact row
# gives the camera height h above the table: h = g*(y_c - y_h)/(a_px*fps^2). Then
# letter length = px_L * h / (y_L - y_h) and table length = W(y)*h/(y-y_h).
import cv2, numpy as np, sys
SCR='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
def frames(vid):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4'); out=[]
    while True:
        ok,fr=cap.read()
        if not ok: break
        out.append(cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY).astype(np.float32))
    return out
vid=sys.argv[1]; F=frames(vid)
bg=F[-1]
yh=float(sys.argv[2]) if len(sys.argv)>2 else 540.0
recs=[]
for k in range(0,14):
    d=np.abs(F[k]-bg); m=(d>25).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    i=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
    x,y,w,h,a=st[i]
    ys,xs=np.where(lab==i)
    recs.append((k,cen[i][0],cen[i][1],y,y+h-1,x,x+w-1,a))
    print('k=%2d cx=%.1f cy=%.1f top=%d bot=%d left=%d right=%d area=%d'%(k,cen[i][0],cen[i][1],y,y+h-1,x,x+w-1,a))
np.save(f'{SCR}/{vid}_fall.npy',np.array(recs))
