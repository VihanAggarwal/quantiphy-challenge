import cv2,numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0231.mp4'); ok,f=cap.read()
g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float)
for xc in [1652,1752,1792]:
    # find darkest column near xc per row, report contrast vs neighbors
    out=[]
    for y in range(960,1075,4):
        row=g[y,xc-8:xc+9]; k=np.argmin(row); c=(row[0]+row[-1])/2-row[k]
        out.append(f'{y}:{xc-8+k}/{c:.0f}')
    print(xc,' '.join(out))
