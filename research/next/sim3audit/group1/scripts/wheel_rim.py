import cv2, numpy as np
frames=[]
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0010.mp4')
while True:
    ok,f=c.read()
    if not ok: break
    frames.append(f.astype(np.float32))
img = np.median(np.stack(frames[::4]),0)   # static cart; median reduces noise
g = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
cv2.imwrite('frames/cart_med.png', img.astype(np.uint8)[1030:1300,1590:1880])
cx0, cy0 = 1731.5, 1164.3
res=[]
for adeg in np.arange(0,360,1.0):
    a=np.deg2rad(adeg)
    rs=np.arange(60,118,0.25)
    xs=(cx0+rs*np.cos(a)).astype(np.float32); ys=(cy0+rs*np.sin(a)).astype(np.float32)
    prof=cv2.remap(g, xs.reshape(1,-1), ys.reshape(1,-1), cv2.INTER_CUBIC).ravel()
    res.append(prof)
res=np.array(res)
np.save('scripts/rim_polar.npy', res)
# print a coarse polar map: rows=angle every 10 deg, columns r 60..118 step 2
for i in range(0,360,10):
    p=res[i][::8]
    print('%3d '%i + ''.join(' .:-=+*#%@'[min(9,int(v/20))] for v in p))
