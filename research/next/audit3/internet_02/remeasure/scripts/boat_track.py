import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0070.mp4'
OUT='/home/user/quantiphy-challenge/research/next/audit3/internet_02/remeasure/'
cam=np.loadtxt(OUT+'boat_cam.txt')
c=cv2.VideoCapture(V); F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)[380:600,:].copy())
def subpix(r,x,y):
    def p(a,b,cc): 
        d=a-2*b+cc; return 0 if d==0 else 0.5*(a-cc)/d
    return x+p(r[y,x-1],r[y,x],r[y,x+1]), y+p(r[y-1,x],r[y,x],r[y+1,x])
def track(ref, x0,x1,y0,y1, rng):
    tpl=F[ref][y0-380:y1-380, x0:x1]
    out=[]
    for k in rng:
        r=cv2.matchTemplate(F[k],tpl,cv2.TM_CCOEFF_NORMED)
        _,mv,_,ml=cv2.minMaxLoc(r)
        sx,sy=subpix(r,*ml)
        out.append((k,sx-x0,sy+380-y0,mv))
    return np.array(out)
# template: hull+bimini at f30, avoid spray (spray is left of flag, below hull)
for ref,box in [(30,(185,402,440,512)),(30,(250,402,440,505)),(24,None),(36,None)]:
    if box is None:
        # shift box by approx motion
        b0=(185,402,440,512); dx=int(round(15.8*(ref-30)))
        box=(b0[0]+dx,b0[1]+dx,b0[2],b0[3])
    T=track(ref,*box,range(max(ref-18,8),ref+19))
    k=T[:,0]; x=T[:,1]-cam[k.astype(int),3]  # camera corrected (rel f30), x shift of boat relative to ref position
    y=T[:,2]-cam[k.astype(int),4]
    # absolute x = box x0 + shift; speeds
    for half in [4,6,8,10]:
        m=np.abs(k-30)<=half
        if m.sum()<5: continue
        p=np.polyfit(k[m]-30,x[m],2); q=np.polyfit(k[m]-30,y[m],2)
        praw=np.polyfit(k[m]-30,T[m,1],2)
        print('ref',ref,box,'±%d'%half,'vx_corr %.3f vy_corr %.3f |v| %.3f  raw vx %.3f  minNCC %.3f'%(p[1],q[1],np.hypot(p[1],q[1]),praw[1],T[m,3].min()))
    if ref==30 and box[0]==185:
        np.savetxt(OUT+'boat_track_f30tpl.txt',np.column_stack([T,x,y]),fmt='%.3f',header='frame dx_raw dy_raw ncc dx_camcorr dy_camcorr')
