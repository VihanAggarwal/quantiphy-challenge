import cv2, numpy as np, json
# Route 3 (no ToF of this clip): bounce-1 position from the table plane (h=0.173 m, from family 0032's stated ranges,
# same table and camera) + apex range from the ball's sharp-frame width (k = 30.6 px*m, ping-pong ball in 0032).
F=711.; CX=640.; CY=360.
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0028x.mp4'); Fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    Fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float))
capo=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0028.mp4'); Fo=[]
while True:
    ok,f=capo.read()
    if not ok: break
    Fo.append(f.astype(float))
# lower edge of the bounce-1 streak (video 26) from the whiteness (min channel) profile, o and x renders
for V,FF in (('x',None),('o',Fo)):
    pass
for k in (26,):
    m=Fo[k].min(2); prof=m[400:446,734:741].mean(1); bg=np.median(m[426:446,700:715]); pk=prof[:10].mean(); hh=(pk+bg)/2
    i=np.nonzero(prof>hh)[0][-1]; print(f'o render video {k}: streak bottom half-max y={400+i+(prof[i]-hh)/(prof[i]-prof[i+1]):.1f} (peak {pk:.0f}, bg {bg:.0f}); contact bottom ~4-9 px lower (blur turn-around)')
# table back edge row near x=737 in the o render: strongest vertical gradient of the table/wall boundary
o=Fo[10]; 
for c in (700,737,760,790):
    col=o[400:450,c-3:c+4].mean(1)  # BGR
    # table is brown (R>B); wall grey: use R-B
    rb=col[:,2]-col[:,0]
    d=np.diff(rb); i=np.argmax(d)
    print(f'back edge at x={c}: y={400+i+0.5:.1f} (R-B jump {d[i]:.1f})')
# plane: camera height above the table top h, horizon row vh (pitch), roll ignored
for h in (0.165,0.173,0.180):
  for vh in (348.,350.,352.):
    n=np.array([0., 1., (CY-vh)/F]); n/=np.linalg.norm(n)   # plane normal (down-ish), n.X = h
    def hit(u,v,hh):
        d=np.array([(u-CX)/F,(v-CY)/F,1.]); return d*hh/(n@d)
    out=[]
    for vb in (428.,430.,432.):
        Pc=hit(737.5,vb,h)                 # contact point on the table
        C=Pc - 0.02*n                      # ball centre 2 cm above (n points down)
        out.append((vb,np.linalg.norm(C)))
    s=' '.join(f'bottom{vb:.0f}->centre range {r:.3f}' for vb,r in out)
    print(f'h={h} vh={vh}: {s}')
k=30.6; w32=21.94; w31=21.48; w33=21.66
Ra=k/np.array([w31,w32,w33]); print('apex centre range from width (k=30.6):',np.round(Ra,3),' mean',Ra.mean().round(3))
for Rb in (1.53,1.56,1.59,1.62):
    zd=(Rb-Ra.mean())/((32.88-27.26)*0.04)
    print(f'bounce centre range {Rb}: approach speed {zd:.2f} m/s')
