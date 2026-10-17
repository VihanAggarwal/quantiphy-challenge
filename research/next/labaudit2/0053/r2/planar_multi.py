import numpy as np, json, sys
sys.argv=[sys.argv[0],'34']; src=open('planar.py').read().split('results=[]')[0]
exec(src)
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
P10=2.73*ray(T[10]['cx'],T[10]['cy']); r34=ray(T[34]['cx'],T[34]['cy'])
sets={'0053 ref10':'track_captured_0053_10.npy','0053 ref22':'track_captured_0053_22.npy','0053 ref34':'track_captured_0053_34.npy','0053s ref22':'track_captured_0053s_22.npy','0053x ref22':'track_captured_0053x_22.npy'}
for name,fn in sets.items():
    tr=np.load(fn); ok=~np.isnan(tr[10,:,0])&~np.isnan(tr[34,:,0])
    data={34:(normc(tr[10][ok]),normc(tr[34][ok]))}
    globals()['data']=data
    line=[]
    for pitch,roll in [(30,15),(34,13),(37,10),(41,6),(37,8),(37.4,1.4),(34.7,10.1),(38.4,10.9)]:
        n=nvec(pitch,roll); c,psi,phi=fitpair(n,34)
        e1,e2=basis(n); d=np.cos(phi)*e1+np.sin(phi)*e2; R=rot(n,psi)
        lam,s=np.linalg.lstsq(np.c_[d,-r34],-R@P10,rcond=None)[0]
        if lam<0:
            d=-d; lam,s=np.linalg.lstsq(np.c_[d,-r34],-R@P10,rcond=None)[0]
        line.append(f'({pitch},{roll}) r={c/ok.sum():.3f} yaw={np.degrees(psi):.1f} D={np.linalg.norm(s*r34-P10):.3f}')
    print(name, ok.sum()); print('   '+'\n   '.join(line))
