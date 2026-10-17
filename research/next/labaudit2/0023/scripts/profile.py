import cv2, numpy as np, sys
V=sys.argv[1]; frames=[int(a) for a in sys.argv[2].split(',')]; y0,y1=[int(a) for a in sys.argv[3].split(',')]; xs=[int(a) for a in sys.argv[4].split(',')]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{V}.mp4')
F={}
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames: F[i]=f.astype(int)
    i+=1
for fi in frames:
    f=F[fi]
    print('frame',fi)
    for y in range(y0,y1):
        row=[]
        for x in xs:
            b,g,r=f[y,x-2:x+3].mean(0)
            row.append('%3d,%3d,%3d'%(r,g,b))
        print(y,' | '.join(row))
