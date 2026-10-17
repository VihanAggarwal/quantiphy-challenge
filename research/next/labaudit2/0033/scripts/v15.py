# t = 1.5 s: c37->c38 (floor) and c38->c39 (round half up). Route A: 3D from the straight-line horizontal motion
# (rolling line, ToF-anchored scale) + height from image v; free-fall fit for the height history.
# Route B: label-style clicks with size-based depths (capsule diameter, calibrated at c35 to the stated range).
import numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0033/scripts')
from geo import *
from fall import run
for R in ['x','s']:
  for f in [711,740]:
    out,bx,by,k,P=run(R,f,verbose=False)
    Cp=json.load(open(BASE+'capsule_%s.json'%R)); T=load_track(R); inv={cap(kk):kk for kk in T}
    # height history: z(c36)=out36, z(c38 mid), z(c39 start ~ c38+e/2...). Fit free fall z = z0 - 0.5 g (t-te)^2 for t>te
    # using c38 mid (t=38) and c39 p0 (t=39 - e/2, e = exposure fraction from c38 capsule vs inter-frame motion)
    c38=Cp[str(inv[38])]; c39=Cp[str(inv[39])]
    L38=np.linalg.norm(np.array(c38['p1'])-np.array(c38['p0']))
    gap=np.linalg.norm(np.array(c39['p0'])-np.array(c38['p1']))
    e=L38/(L38+gap)  # rough exposure fraction
    t39s=39-e/2
    z38=out[38]['z']; z39s=out[39]['z']
    # free fall from rest at height 2 (rolling centre) at time te: solve with z38 and z39s (2 unknowns: te, g_eff) -> report g_eff
    # and with g fixed at 980 (in plane units / k): te from z38
    gp=980/k  # gravity in plane-scale units (cm/s^2) since plane cm = true cm / k
    te38=38-np.sqrt(2*(2-z38)/gp)*25; te39=t39s-np.sqrt(2*(2-z39s)/gp)*25
    te=(te38+te39)/2
    def z(t): return 2-0.5*gp*(max(t-te,0)/25)**2
    def pos(t):  # table coords on the line + z
        tau=t-35
        return np.array([bx[1]+bx[0]*tau, by[1]+by[0]*tau, z(t)])
    def cam(t): return P['R']@pos(t)+P['t']
    phys={}
    for (a,b) in [(35,36),(37,38),(38,39)]:
        phys[(a,b)]=np.linalg.norm(cam(b)-cam(a))*25*k
    inst={t: np.hypot(np.hypot(bx[0],by[0])*25, gp*max(t-te,0)/25)*k for t in [37.5,38,38.5]}
    # label-style with clicks: c38 mid, c39 mid estimated as p0 + e/2 * (direction of streak) * (L39 per full frame)
    d39=np.array(c39['p1'])-np.array(c39['p0']); d39/=np.linalg.norm(d39)
    # model image speed at c39 from projection of the model
    uv=lambda t: project(cam(t)[None,:],f)[0]
    mid39=np.array(c39['p0'])+ (uv(39)-uv(t39s))
    clicks={36:np.array(Cp[str(inv[36])]['mid']),38:np.array(c38['mid']),39:mid39}
    clicks[37]=uv(37)+ (clicks[36]-uv(36))*0.5 + (clicks[38]-uv(38))*0.5   # model-interpolated, offset-corrected
    rngA={c: np.linalg.norm(cam(c))*k for c in [36,37,38,39]}
    # Route B depths: size (capsule diam) calibrated at c35
    d35=2*Cp[str(inv[35])]['r']; cal=(75.8)/(f*4/d35)
    rngB={36:f*4/(2*Cp[str(inv[36])]['r'])*cal,38:f*4/(2*c38['r'])*cal,39:f*4/(2*c39['r'])*cal}
    rngB[37]=(rngB[36]+rngB[38])/2
    def lab(a,b,rng): return np.linalg.norm(rng[b]*ray(*clicks[b],f)-rng[a]*ray(*clicks[a],f))*25
    print('%s f%d k=%.3f e=%.2f te=c%.2f (from c38 %.2f, c39 %.2f) | ranges A %s | B %s'%(R,f,k,e,te,te38,te39,
          {c:round(v,1) for c,v in rngA.items()},{c:round(v,1) for c,v in rngB.items()}))
    print('   physical FD: c35->36 %.0f  c37->38 %.0f  c38->39 %.0f | inst c37.5 %.0f c38 %.0f c38.5 %.0f'%(phys[(35,36)],phys[(37,38)],phys[(38,39)],inst[37.5],inst[38],inst[38.5]))
    print('   label clicks %s'%({c:np.round(v,1).tolist() for c,v in clicks.items()}))
    print('   label A (model depth): c37->38 %.0f  c38->39 %.0f | label B (size depth): c37->38 %.0f  c38->39 %.0f'%(lab(37,38,rngA),lab(38,39,rngA),lab(37,38,rngB),lab(38,39,rngB)))
