import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
import geo
exec(open('scripts/wb62b.py').read().split('for n in (24,40,48):')[0])
C40,_,_=board_corners(40); C48,_,_=board_corners(48)
quad=np.load('book_quad.npy')
vpv=np.array([452.6,1379.1]); vpc=np.array([2194.6,121.2]); vpj=np.array([219.5,-241.0])
def ray(u,v,f):
    d=np.array([(u-640)/f,(v-360)/f,1.0]); return d/np.linalg.norm(d)
for f in (650,700,711,730,760,800,850):
    dn=ray(*vpv,f)
    H=2.082*ray(666.4,617.9,f)@dn+0.018
    def fp(u,v,z):
        r=ray(u,v,f); return r*(H-z)/(r@dn)
    out=[]
    for C in (C40,C48,quad):
        z=0.01 if C is not quad else 0.018
        Q=np.array([fp(u,v,z) for u,v in C])
        e=[np.linalg.norm(Q[(j+1)%4]-Q[j]) for j in range(4)]
        ang=[np.degrees(np.arccos((Q[j-1]-Q[j])@(Q[(j+1)%4]-Q[j])/np.linalg.norm(Q[j-1]-Q[j])/np.linalg.norm(Q[(j+1)%4]-Q[j]))) for j in range(4)]
        out.append((np.round(np.array(e)*100,1),np.round(np.abs(np.array(ang)-90).max(),1)))
    # ball floating height
    Cb=3.041*ray(985.8,369.6,f); zb=H-Cb@dn
    print(f,'orth %.3f %.3f'%(dn@ray(*vpc,f),dn@ray(*vpj,f)),'H %.3f'%H,'wb40',out[0],'wb48',out[1],'book',out[2],'ball centre z %.3f'%zb)
