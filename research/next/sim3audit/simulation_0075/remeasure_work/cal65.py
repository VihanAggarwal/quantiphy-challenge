from curbs import *
from ov import draw
bg=cv2.imread('fr/bg_simulation_0065.png'); ch=cv2.GaussianBlur(chroma(bg),(3,3),0)
segs={
 'M_nearR':((1300,600),(1570,1060),(-1,0)),
 'M_nearL':((120,625),(15,760),(1,0)),
 'M_farL':((585,20),(430,260),(1,0)),
 'M_farR':((935,20),(1070,260),(-1,0)),
 'C_nearR':((1330,555),(2150,505),(0,-1)),
 'C_farR':((1200,305),(2150,250),(0,1)),
 'C_farL':((40,330),(320,312),(0,1)),
}
L={}
for k,(a,b,rd) in segs.items():
    P=road_edge(ch,a,b,rd,half=30)
    if len(P)<5: print(k,'few',len(P)); continue
    ln,rms,n=robust_line(P); L[k]=ln; print(k,n,len(P),'rms %.2f'%rms)
np.save('lines65.npy',L)
im=draw(bg,list(L.values()))
cv2.imwrite('fr/ov65.png',cv2.resize(im,(1080,540)))
vpM=[inter(L['M_nearR'],L['M_farL']),inter(L['M_nearR'],L['M_nearL']),inter(L['M_farL'],L['M_farR']),inter(L['M_nearL'],L['M_farR'])]
print('main VPs',np.round(vpM,1))
vpC=[inter(L['C_nearR'],L['C_farR']),inter(L['C_nearR'],L['C_farL']),inter(L['C_farR'],L['C_farL'])]
print('cross VPs',np.round(vpC,1))
