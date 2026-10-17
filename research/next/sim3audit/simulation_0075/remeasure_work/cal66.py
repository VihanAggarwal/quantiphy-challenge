from curbs import *
from ov import draw
bg=cv2.imread('fr/bg_simulation_0066.png'); ch=cv2.GaussianBlur(chroma(bg),(3,3),0)
segs={
 'R1_L':((610,180),(770,410),(1,0)),
 'R1_R':((820,170),(1180,330),(-1,1)),
 'R2_TL':((60,555),(380,505),(0,1)),
 'R2_TR':((1320,355),(2100,238),(0,1)),
 'R2_BR':((1830,570),(2140,478),(0,-1)),
 'R2_BL':((600,1040),(930,915),(0,-1)),
 'R1_NR':((1080,930),(1130,1060),(-1,0)),
}
L={}
for k,(a,b,rd) in segs.items():
    P=road_edge(ch,a,b,rd,half=25)
    if len(P)<5: print(k,'few',len(P)); continue
    ln,rms,n=robust_line(P); L[k]=ln; print(k,n,len(P),'rms %.2f'%rms)
np.save('lines66.npy',L)
im=draw(bg,list(L.values()))
cv2.imwrite('fr/ov66.png',cv2.resize(im,(1080,540)))
for a,b in [('R1_L','R1_R'),('R1_L','R1_NR'),('R1_R','R1_NR')]:
    if a in L and b in L: print(a,b,inter(L[a],L[b]))
for a,b in [('R2_TL','R2_TR'),('R2_TL','R2_BR'),('R2_TR','R2_BR'),('R2_TL','R2_BL'),('R2_TR','R2_BL'),('R2_BR','R2_BL')]:
    if a in L and b in L: print(a,b,inter(L[a],L[b]))
