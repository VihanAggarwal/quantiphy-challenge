import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f.astype(np.float32))
t=np.loadtxt('research/next/audit3/internet_11/remeasure/track47d.txt')
pos=dict((int(a),b) for a,b in zip(t[:,0],t[:,1]))
for i in range(9,19):
    xc=int(round(pos[i]))
    res=[]
    for dx in range(-20,21,4):
        col=fr[i][:,xc+dx,:].sum(axis=1)
        col=np.convolve(col,np.ones(3)/3,'same')
        gr=np.gradient(col)
        # top edge: wood (bright) above -> ball (dark) below: strong negative gradient, search 330-450
        a,b=330,460
        k=a+np.argmin(gr[a:b])
        # subpixel parabola
        y0=k+0.5*(gr[k-1]-gr[k+1])/(gr[k-1]-2*gr[k]+gr[k+1])
        a2,b2=570,680
        k2=a2+np.argmax(gr[a2:b2])
        y1=k2+0.5*(gr[k2-1]-gr[k2+1])/(gr[k2-1]-2*gr[k2]+gr[k2+1])
        res.append(y1-y0)
    res=np.array(res)
    print(i,'xc',xc,'maxgrad vertical extent: max %.1f median %.1f'%(res.max(),np.median(res)), np.round(res,1))
