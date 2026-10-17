import cv2, numpy as np
def frames(v, idx):
    c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); out=[]; i=0
    while True:
        ok,f=c.read()
        if not ok: break
        if i in idx: out.append(f.astype(np.float32))
        i+=1
    return out
a = frames('simulation_0141', [0,10,20,30,40,50,59])
b = frames('simulation_0143', [0,20,40,60,80,99])
ma = np.median(np.stack(a),0); mb=np.median(np.stack(b),0)
d = np.abs(ma-mb).mean(2)
print('mean abs diff', d.mean(), 'median', np.median(d), 'p90', np.percentile(d,90))
# region bottom-right floor without people
for (y0,y1,x0,x1) in [(900,1080,1100,1900),(0,300,0,1920),(600,900,1200,1900)]:
    print((y0,y1,x0,x1), d[y0:y1,x0:x1].mean())
cv2.imwrite('frames/bg0141.png', ma.astype(np.uint8)); cv2.imwrite('frames/bg0143.png', mb.astype(np.uint8))
