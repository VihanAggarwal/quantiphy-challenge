import numpy as np, sys
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
V,ph=sys.argv[1],sys.argv[2]; y0,y1=[int(a) for a in sys.argv[3].split(',')]; xs=[int(a) for a in sys.argv[4].split(',')]
A=np.load(D+f'frames/avg_{V}_{ph}.npy')  # offset (300,400)
for y in range(y0,y1):
    row=[]
    for x in xs:
        b,g,r=A[y-300,x-400-2:x-400+3].mean(0)
        row.append('%3d %3d %3d'%(r,g,b))
    print(y,' | '.join(row))
