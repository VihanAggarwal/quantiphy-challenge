from curbs import *
from geom import *
from ov import draw
bg=cv2.imread('fr/bg_simulation_0066.png'); ch=cv2.GaussianBlur(chroma(bg),(3,3),0)
A=np.load('auto66.npy')
L={'R2_top':A[0],'R1_right':A[1],'R2_bot':A[2]}
for k,(a,b,rd) in {'R1_left_far':((672,165),(790,385),(1,0)),'R1_left_near':((1088,925),(1150,1060),(1,0))}.items():
    P=road_edge(ch,a,b,rd,half=20,step=2)
    print(k,len(P))
    if len(P)>=5:
        ln,rms,n=robust_line(P); L[k]=ln; print(k,n,'rms %.2f'%rms)
im=draw(bg,list(L.values())); cv2.imwrite('fr/ov66b.png',cv2.resize(im,(1080,540)))
np.save('lines66.npy',L)
vp1a=inter(L['R1_right'],L['R1_left_far']); vp1b=inter(L['R1_right'],L['R1_left_near']) if 'R1_left_near' in L else None
vp2=inter(L['R2_top'],L['R2_bot'])
print('vp1',vp1a,vp1b,'vp2',vp2)
pp=np.array([1079.5,539.5])
for vp1 in [vp1a,vp1b]:
    if vp1 is None: continue
    f2=-((vp1-pp)@(vp2-pp)); print('f from orthogonality', np.sqrt(f2) if f2>0 else None)
