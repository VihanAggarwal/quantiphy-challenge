import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from geo import *
def d(a,b): return np.linalg.norm(a-b)*100
# bottom (contact) corners
Ab=on_plane(497,480); Bb=on_plane(589,498); Cb=on_plane(645,488)
print('bottom A-B %.1f  B-C %.1f cm; ranges A %.3f B %.3f C %.3f'%(d(Ab,Bb),d(Bb,Cb),*[np.linalg.norm(X) for X in (Ab,Bb,Cb)]))
for h in [0.010,0.0146,0.02]:
    A=on_plane(497,468,h); B=on_plane(590,487,h); C=on_plane(643,480,h); Dd=on_plane(555,463,h)
    print('h=%.4f top A-B %.1f B-C %.1f C-D %.1f D-A %.1f'%(h,d(A,B),d(B,C),d(C,Dd),d(Dd,A)), 'angle at B', round(np.degrees(np.arccos(((A-B)@(C-B))/np.linalg.norm(A-B)/np.linalg.norm(C-B))),1))
# thickness: front corner top (590,487) vs bottom (589,498): vertical line through bottom point
Xb=Bb; up=n
# find h such that projection of Xb+h*up hits v=487
for h in np.arange(0.005,0.03,0.0005):
    X=Xb+h*up; v=711*X[1]/X[2]+360
    if v<=487: print('thickness at front corner ~%.2f cm'%(h*100)); break
X=Ab
for h in np.arange(0.005,0.03,0.0005):
    Y=X+h*up; v=711*Y[1]/Y[2]+360
    if v<=466: print('thickness at left corner ~%.2f cm'%(h*100)); break
