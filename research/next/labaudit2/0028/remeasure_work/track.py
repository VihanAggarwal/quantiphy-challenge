import cv2, numpy as np, sys
v = sys.argv[1] if len(sys.argv)>1 else 'captured_0028x'
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
for i,f in enumerate(fr):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    # white-ish: low saturation, high value
    m=((hsv[...,1]<60)&(hsv[...,2]>150)).astype(np.uint8)
    m[690:,:]=0  # watermark
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cands=[(st[k,4],cen[k],st[k,:4]) for k in range(1,n) if st[k,4]>15]
    cands.sort(key=lambda x:-x[0])
    print(i, [(a, tuple(np.round(b,1)), tuple(s)) for a,b,s in cands[:3]])
