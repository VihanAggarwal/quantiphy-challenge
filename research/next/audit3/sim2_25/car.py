import cv2,numpy as np
v='data/QuantiPhy/simulation_0118.mp4'
c=cv2.VideoCapture(v); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im)
print(len(fr))
# saturation mask in car band
for f in [0,1,30,60,90,120]:
    hsv=cv2.cvtColor(fr[f],cv2.COLOR_BGR2HSV)
    band=hsv[680:780,:,1].astype(float)
    m=band>110
    cols=np.nonzero(m.sum(0)>3)[0]; rows=np.nonzero(m.sum(1)>3)[0]
    # largest run of cols
    runs=np.split(cols,np.where(np.diff(cols)>3)[0]+1); r=max(runs,key=len)
    print(f,'x %d-%d (%d)'%(r[0],r[-1],r[-1]-r[0]+1),'rows',rows.min()+680,rows.max()+680)
# template tracking
g=[cv2.cvtColor(x,cv2.COLOR_BGR2GRAY).astype(np.float32) for x in fr]
T=g[60][690:770,380:540]
xs=[]
for f in range(len(g)):
    r=cv2.matchTemplate(g[f][680:780,:],T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
    j=ml[0]; i=ml[1]; dx=(r[i,j-1]-r[i,j+1])/(2*(r[i,j-1]-2*r[i,j]+r[i,j+1]))
    xs.append(j+dx)
xs=np.array(xs); t=np.arange(len(xs))
p=np.polyfit(t,xs,1); print('px/frame %.4f'%p[0],'rms %.3f'%np.std(xs-np.polyval(p,t)),'x0-x120 %.2f'%(xs[-1]-xs[0]))
print('first diffs',np.round(np.diff(xs[:6]),2),'last',np.round(np.diff(xs[-5:]),2))
