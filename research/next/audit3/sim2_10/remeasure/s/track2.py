import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0246.mp4'
c=cv2.VideoCapture(V); F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
F=np.array(F); n=len(F)
def track_chain(box,ref,gap=1):
    # anchored template at ref frame, matched in all frames, restricted rows
    x0,x1,y0,y1=box
    T=F[ref][y0:y1,x0:x1]
    out=[]
    for i in range(n):
        R=cv2.matchTemplate(F[i],T,cv2.TM_CCOEFF_NORMED)
        ylo=max(0,y0-30); yhi=min(R.shape[0],y0+30)
        Rs=R[ylo:yhi]
        _,mv,_,ml=cv2.minMaxLoc(Rs)
        x,y=ml
        if 0<x<Rs.shape[1]-1:
            a,b,cc=Rs[y,x-1],Rs[y,x],Rs[y,x+1]; den=a-2*b+cc
            dx=0.5*(a-cc)/den if den!=0 else 0
        else: dx=0
        out.append((x+dx-x0,y+ylo-y0,mv))
    return np.array(out)
boxes={'torso_back':(500,640,530,610),'rump':(470,560,520,620),'shoulder':(640,760,530,610),'head':(840,940,540,620),'tailtuft':(340,400,555,600),'hornL_tip':(420,520,425,470),'hornR_tip':(420,520,605,650),'whole':(330,950,420,660)}
for k,b in boxes.items():
    t=track_chain(b,0)
    xs=t[:,0]; fr=np.arange(n)
    p=np.polyfit(fr,xs,1); res=xs-np.polyval(p,fr)
    print('%-10s fit %.3f px/f  e2e %.3f  rms %.1f  minscore %.2f meanscore %.2f  dy %d..%d'%(k,p[0],(xs[-1]-xs[0])/(n-1),res.std(),t[:,2].min(),t[:,2].mean(),t[:,1].min(),t[:,1].max()))
    if k in('torso_back','head','whole'):
        print('   x at 0,10..70,74:',np.round(xs[[0,10,20,30,40,50,60,70,74]],1))
