import numpy as np, json
f=711.; c=np.array([640.,360.])
PL=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/plane.json'))['gm']
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0030/track.json'))
def cap(k): return k+(k>=12)+(k>=36)
def rayv(x,y): return np.array([(x-c[0])/f,(y-c[1])/f,1.])
def pos_plane(x,y,R=0.035,pl=PL):
    n=np.array(pl['n']); d=pl['d']; rr=rayv(x,y); return (d+R)/(n@rr)*rr
anch={5:0.8715,10:1.166,15:1.372,20:1.315}
for k in range(0,26):
    t=T['s'][k]; o=T['o'][k]
    p=pos_plane(t['cx'],t['cy']); pb=pos_plane(t['cx'],t['bot'],R=0.0)
    n=cap(k)
    # size-based centre range from mask width (underestimates size)
    print(f"v{k:2d} n{n:2d} cx{t['cx']:6.1f} cy{t['cy']:5.1f} bot{t['bot']} plane_ctr_rng {np.linalg.norm(p):.3f} surf {np.linalg.norm(p)-0.035:.3f}  bottom-contact rng {np.linalg.norm(pb):.3f}  w{t['w']} h{t['h']} size_rng(w) {711*0.07/max(t['w'],1):.3f}  stated {anch.get(n,'')}")
