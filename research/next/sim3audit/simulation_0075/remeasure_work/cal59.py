from curbs import *
from ov import draw
bg=cv2.imread('fr/bg_simulation_0059.png'); ch=cv2.GaussianBlur(chroma(bg),(3,3),0)
segs={'L':((60,1010),(780,832),(1,0)),'R':((1640,840),(2140,1045),(-1,0)),
      'Lfar':((850,790),(1000,752),(1,0)),'Rfar':((1450,775),(1600,812),(-1,0))}
L={}
for k,(a,b,rd) in segs.items():
    P=road_edge(ch,a,b,rd,half=20)
    if len(P)<5: print(k,'few',len(P)); continue
    ln,rms,n=robust_line(P); L[k]=ln; print(k,n,len(P),'rms %.2f'%rms, ln)
np.save('lines59.npy',L)
im=draw(bg,list(L.values()))
cv2.imwrite('fr/ov59.png',cv2.resize(im[600:1080],(1080,240)))
vp=inter(L['L'],L['R']); print('VP near',vp)
if 'Lfar' in L and 'Rfar' in L: print('VP far', inter(L['Lfar'],L['Rfar']))
