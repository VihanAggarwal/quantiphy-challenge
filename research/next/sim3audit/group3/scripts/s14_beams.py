import cv2, numpy as np
f=cv2.imread('/home/user/quantiphy-challenge/research/next/sim3audit/group3/frames/simulation_0014/f072.png')
g=cv2.GaussianBlur(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float),(3,3),0)
gy=np.diff(g,axis=0)
# beams: search windows (y ranges) and x samples avoiding door/vines/barrels
def edges(y0,y1,xs,sign):
    out=[]
    for x in xs:
        col=gy[y0:y1,x-3:x+4].mean(1)
        k=np.argmax(sign*col)
        # subpixel
        if 0<k<len(col)-1:
            a,b,c=col[k-1],col[k],col[k+1]; d=0.5*(a-c)/(a-2*b+c)
        else: d=0
        out.append((x,y0+k+0.5+d,sign*col[k]))
    return out
for name,(y0,y1) in {'eave_beam':(835,875),'mid_beam':(925,960),'low_beam':(1070,1100),'base':(1160,1195)}.items():
    for sign,lab in ((1,'dark->bright (top edge if beam bright)'),(-1,'bright->dark')):
        xs=[440,470,500,540,580,600,640,660,700,800,840,880,900,920,935]
        e=edges(y0,y1,xs,sign)
        e=[t for t in e if t[2]>3]
        if len(e)<4: continue
        X=np.array([t[0] for t in e]); Y=np.array([t[1] for t in e])
        p=np.polyfit(X,Y,1); r=Y-np.polyval(p,X)
        print(name,lab,'slope=%.4f'%p[0],'n=%d'%len(e),'rms=%.2f'%r.std(), ' '.join('%d:%.1f'%(a,b) for a,b in zip(X,Y)))
