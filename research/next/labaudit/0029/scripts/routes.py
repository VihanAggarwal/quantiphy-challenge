import numpy as np, json
f=711.0; c=np.array([640,360.])
def ray(u,v):
    d=np.array([(u-c[0])/f,(v-c[1])/f,1.0]); return d/np.linalg.norm(d)
seg=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0029/scripts/track_seg.json'))
bf=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0029/scripts/ballfit.json'))
P=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0029/scripts/P_plane_W.npy'); Pp={int(r[0]):r[1:] for r in P}
st={1.0:0.901,1.24:1.144,1.6:1.027}
def pix(i):
    i0=int(np.floor(i)); a=i-i0
    p0=np.array(seg[str(i0)]); p1=np.array(seg[str(i0+1)]) if a>0 else p0
    return (1-a)*p0+a*p1
print('Route A: stated ranges + pixel centres (x-render seg centres)')
for fps in [24,25]:
    for hit in ([29.76,30] if fps==24 else [31,30]):
        i1=1.0*fps if fps==24 else 25
        A=st[1.0]*ray(*pix(i1)); B=st[1.24]*ray(*pix(hit))
        print(f' fps={fps} t1->frame {i1}, hit->frame {hit}: chord = {100*np.linalg.norm(B-A):.1f} cm')
print('Route B: table plane (W=76.0 scale)')
for a,b in [(24,30),(24,29),(25,30),(25,31),(24,31)]:
    ch=100*np.linalg.norm(Pp[b]-Pp[a]); pl=100*sum(np.linalg.norm(Pp[k+1]-Pp[k]) for k in range(a,b))
    print(f' frames {a}->{b}: chord {ch:.1f} cm, summed path {pl:.1f} cm')
print('Route C: ball-size ranges (D px from circle fit, 6.7cm, f=711), corrected by global size/stated ratio')
Rs={int(k):f*0.067/v['D'] for k,v in bf.items()}
for a,b in [(24,30),(25,30),(26,30)]:
    A=Rs[a]*ray(*seg[str(a)]); B=Rs[b]*ray(*seg[str(b)])
    print(f' frames {a}->{b}: ranges {Rs[a]:.3f},{Rs[b]:.3f} chord {100*np.linalg.norm(B-A):.1f}')
# release->hit using plane where valid
for a in [19,20,21,22]:
    ch=100*np.linalg.norm(Pp[30]-Pp[a]); print(f' plane chord frame {a}->30: {ch:.1f}')
