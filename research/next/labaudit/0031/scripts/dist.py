import numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit/0031/'
tr=json.load(open(D+'track.json')); ci=json.load(open(D+'circ.json'))
cx,cy=640,360
pl=np.load(D+'scripts/plane_f711.npy'); n=pl[:3]; W=pl[3]; L=pl[4]
def interp(r,key,t,idx):
    a=int(np.floor(t)); w=t-a
    return (1-w)*tr[r][key][a][idx]+w*tr[r][key][a+1][idx]
for r in ['0','x']:
  for t0,lab in [(38.4,'24fps'),(40.0,'25fps')]:
    ut,vt=interp(r,'T',t0,1),interp(r,'T',t0,2); uw,vw=interp(r,'W',t0,1),interp(r,'W',t0,2)
    for f in [650,711,760]:
        Ki=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1.]]))
        rt=Ki@np.array([ut,vt,1]); rw=Ki@np.array([uw,vw,1]); et=rt/np.linalg.norm(rt); ew=rw/np.linalg.norm(rw)
        s1=np.linalg.norm(1.19*et-0.994*ew)*100
        s1c=np.linalg.norm((1.19+0.0335)*et-(0.994+0.02)*ew)*100
        sw=np.linalg.norm(0.994*et-1.19*ew)*100
        out=f'{r} {lab} f{f}: stated {s1:.2f} stated+r {s1c:.2f} swapped {sw:.2f}'
        if f==711:
            dt=interp(r,'T',t0,6); dw=interp(r,'W',t0,6)
            # use circle-fit white diameter (mask underestimates)
            dwc=np.interp(t0,[q[0] for q in ci[r]['W'] if q],[q[3] for q in ci[r]['W'] if q])
            Rt=f*6.7/dt; Rw=f*4.0/dwc
            out+=f' | size {np.linalg.norm(Rt*et-Rw*ew):.2f} (Rt {Rt:.1f} Rw {Rw:.1f})'
            for hn,h in [('W',60.3/W),('L',76.0/L)]:
                Pt=(h-3.35)*rt/(n@rt); Pw=(h-2.0)*rw/(n@rw)
                out+=f' | plane{hn} {np.linalg.norm(Pt-Pw):.2f}'
        print(out)
