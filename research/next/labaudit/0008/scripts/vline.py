# Heights along a vertical line through the contact point (ball assumed to fall/bounce nearly vertically).
import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts')
f=float(sys.argv[1]) if len(sys.argv)>1 else 711.; cx=640.; cy=360.
h=float(sys.argv[2]) if len(sys.argv)>2 else 0.855
n=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/normal.npy')
R=0.116
def ray(p):
    r=np.array([p[0]-cx,p[1]-cy,f]); return r/np.linalg.norm(r)
# loose-mask centres (bbox mid) from ballistic.py output
T={23:(526.0,132.0),24:(534.5,158.0),25:(538.0,191.0),26:(544.0,237.0),27:(550.0,284.5),28:(567.0,337.0),29:(575.5,393.0),
   31:(569.0,386.5),32:(566.0,358.5),33:(558.0,338.0),34:(553.0,318.0),35:(551.0,307.0),36:(548.0,306.0),37:(550.0,314.0),
   38:(552.0,332.0),39:(555.5,353.0),40:(562.0,380.0)}
contact=(577.5,418.0)  # frame 30 ball centre (fit), bottom cut by table/shadow
def plane_pt(p,off):  # point on plane offset 'off' above desk along ray p
    r=ray(p); t=-(h-off)/(n@r); return t*r
Cc=plane_pt(contact,R)
print('contact centre range %.3f'%np.linalg.norm(Cc))
def closest(p):
    r=ray(p); # line1: Cc + s n ; line2: t r
    A=np.array([[n@n,-n@r],[n@r,-r@r]]); b=np.array([-(Cc@n),-(Cc@r)])
    s,t=np.linalg.solve(A,b); gap=np.linalg.norm(Cc+s*n-t*r); return s,t,gap
H={}
for i,p in T.items():
    s,t,gap=closest(p); H[i]=s; print(f'f{i} t={i/24:.3f} centre height above contact-centre {100*s:6.1f} cm (above desk {100*(s+R):6.1f}) range {t:.3f} miss {100*gap:.1f} cm')
for name,fr in [('fall',[24,25,26,27,28,29]),('fall23',[23,24,25,26,27,28,29]),('reb',list(range(31,41))),('reb32',list(range(32,41)))]:
    t=np.array(fr)/24.; s=np.array([H[i] for i in fr])
    c=np.polyfit(t,s,2); print(name,'free fit g=%.2f'%(-2*c[0]), end='; ')
    # fixed g=9.8 fit
    y=s+4.9*t**2; c2=np.polyfit(t,y,1); res=y-np.polyval(c2,t)
    v=lambda tt: c2[0]-9.8*tt
    print('g=9.8 fit: rms %.1f cm; height(1.0) %.1f, v(1.0) %.2f, v(1.2) %.2f; zero-crossings'%(100*np.sqrt(np.mean(res**2)),100*(np.polyval(c2,1.0)-4.9+R),v(1.0),v(1.2)),
          np.round(np.roots([-4.9,c2[0],c2[1]]),3), 'apex t %.3f h %.1f cm'%(c2[0]/9.8, 100*(np.polyval(c2,c2[0]/9.8)-4.9*(c2[0]/9.8)**2+R)))
