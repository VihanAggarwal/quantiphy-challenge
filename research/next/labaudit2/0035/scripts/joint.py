# Joint plane + soccer-diameter fit from ball sizes, for a take and a focal length; K for bb from camera a labels (my masks)
import sys
from geom import *
take=sys.argv[1]; f=float(sys.argv[2]) if len(sys.argv)>2 else 711.0
tr=load_tr(take); bb=tr['bb']; sb=tr['sb']
def Kfrom(d,rng_surf,R,f):
    return (rng_surf+R)*d['deq']*cosa(d['cx'],d['cy'],f)**1.5
# calibrate K_bb on camera a labels (same masks)
tra=load_tr('a')
Ka=[Kfrom(capframe_pos(tra['bb'],15),2.27,0.116,f),Kfrom(capframe_pos(tra['bb'],40),2.412,0.116,f)]
K=np.mean(Ka); print('K_bb from camera a labels',np.round(Ka,1),'->',round(K,1),' (f*D: implied f for D=0.232: %.0f)'%(K/0.232))
if take=='a':
    fb=[k for k in list(range(0,8))+list(range(20,49)) if k in bb]; fs=[k for k in range(20,49) if k in sb]
else:
    fb=[k for k in list(range(0,11))+list(range(28,46)) if k in bb]; fs=[k for k in list(range(0,11))+list(range(26,49)) if k in sb]
Pb=np.array([size_range(bb[k],K,f=f)*ray(bb[k]['cx'],bb[k]['cy'],f) for k in fb])
out=[]
for Ds in np.arange(0.150,0.210,0.001):
    Ks=K*Ds/0.232
    Ps=np.array([size_range(sb[k],Ks,f=f)*ray(sb[k]['cx'],sb[k]['cy'],f) for k in fs])
    n=np.array([0,-0.8,-0.6])
    for it in range(8):
        Q=np.vstack([Pb,Ps+(0.116-Ds/2)*n]); n,hc=fit_plane(Q)
    res=Q@n+hc; out.append((np.sqrt((res**2).mean()),Ds,n,hc))
out.sort(key=lambda x:x[0]); rms,Ds,n,hc=out[0]
print(f'best Ds={Ds:.3f} n={np.round(n,4)} cam_h={hc+0.116:.3f} pitch={np.degrees(np.arcsin(-n[2])):.1f} rms={100*rms:.2f}cm')
print('  rms vs Ds:',' '.join(f'{o[1]:.3f}:{100*o[0]:.2f}' for o in sorted(out,key=lambda x:x[1])[::5]))
# plane-only bb fit
nb,hb=fit_plane(Pb); print('bb-only plane',np.round(nb,4),'cam_h %.3f'%(hb+0.116),'angle to joint %.1f deg'%np.degrees(np.arccos(nb@n)))
np.save(f'{OUT}/plane_{take}_f{int(f)}.npy',np.array([*n,hc+0.116,Ds,K]))
# stated points vs model
St={'a':[(15,'sb',2.758),(15,'bb',2.27),(40,'sb',3.052),(40,'bb',2.412)],
    'b':[(22.5,'sb',2.477),(22.5,'bb',2.7777),(35,'sb',2.373),(35,'bb',2.602)]}[take]
h=hc+0.116
for c,key,lab in St:
    if c==int(c): d=capframe_pos(tr[key],int(c))
    else:
        d1=capframe_pos(tr[key],int(c)); d2=capframe_pos(tr[key],int(c)+1); d={kk:(d1[kk]+d2[kk])/2 for kk in ['cx','cy','deq','minor']}
    R=0.116 if key=='bb' else Ds/2; Kk=K if key=='bb' else K*Ds/0.232
    rs=size_range(d,Kk,f=f); P=plane_point(d['cx'],d['cy'],n,h,R,f); rp=np.linalg.norm(P)
    floor=np.linalg.norm(plane_point(d['cx'],d['cy'],n,h,0.0,f))
    print(f'  cap{c} {key} label {lab:.3f} | size surf {rs-R:.3f} | plane surf {rp-R:.3f} | floor-behind {floor:.3f} | px ({d["cx"]:.0f},{d["cy"]:.0f}) deq {d["deq"]:.1f}')
