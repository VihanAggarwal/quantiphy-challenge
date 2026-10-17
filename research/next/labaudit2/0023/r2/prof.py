import cv2, numpy as np, sys
R1='/home/user/quantiphy-challenge/research/next/labaudit/0023/frames/'
pre=sys.argv[1]; frames=[int(a) for a in sys.argv[2].split(',')]; y0,y1=[int(a) for a in sys.argv[3].split(',')]; xs=[int(a) for a in sys.argv[4].split(',')]
for fi in frames:
    f=cv2.imread(R1+f'{pre}{fi:02d}.png').astype(int)
    print('frame',fi)
    for y in range(y0,y1):
        print(y,' | '.join('%3d,%3d,%3d'%tuple(f[y,x-2:x+3].mean(0)[::-1]) for x in xs))
