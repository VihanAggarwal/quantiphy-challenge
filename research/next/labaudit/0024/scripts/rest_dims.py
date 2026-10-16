import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from geo import *
def L(a,b): return np.linalg.norm(a-b)*100
h=0.0146
for A,D_,B,C in [((500,467),(550,461),(594,489),(640,479)),((498,467),(552,461),(596,488),(642,478)),((500,468),(548,462),(594,488),(640,480))]:
    PA,PD,PB,PC=[on_plane(*p,h) for p in (A,D_,B,C)]
    print('top: A-B %.1f D-C %.1f | A-D %.1f B-C %.1f | angle at B %.0f'%(L(PA,PB),L(PD,PC),L(PA,PD),L(PB,PC),np.degrees(np.arccos((PA-PB)@(PC-PB)/np.linalg.norm(PA-PB)/np.linalg.norm(PC-PB)))))
for Ab,Bb,Cb in [((500,479),(596,497),(642,488)),((498,478),(594,497),(645,487))]:
    PA,PB,PC=[on_plane(*p,0) for p in (Ab,Bb,Cb)]
    print('bottom: A-B %.1f B-C %.1f angle %.0f ranges %s'%(L(PA,PB),L(PB,PC),np.degrees(np.arccos((PA-PB)@(PC-PB)/np.linalg.norm(PA-PB)/np.linalg.norm(PC-PB))),np.round([np.linalg.norm(PA),np.linalg.norm(PB),np.linalg.norm(PC)],3)))
