# Check that simulation_0020 (1080x1080) is the centre crop (x offset 420) of simulation_0032_segmented (1920x1080)
import cv2, numpy as np, json
b={r['f']:r for r in json.load(open('/home/user/quantiphy-challenge/research/next/sim3audit/group3/s32_ball.json'))}
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0020.mp4')
c2=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0032_segmented.mp4')
res=[]
for i in range(130):
    ok,f=c.read(); ok2,g=c2.read()
    if not (ok and ok2): break
    m=((765-g.astype(int).sum(2))>60)
    mc=m[:,420:1500]
    # in 0020, compare pixel colours under the 0032 mask: segmented pixels should equal 0020 pixels
    diff=np.abs(f.astype(int)-g[:,420:1500].astype(int)).sum(2)
    if mc.sum()>0:
        res.append((i, float(np.median(diff[mc])), float(np.median(diff[~mc]))))
for r in res[::13]: print('frame %d  median |0020-0032| inside mask %.1f  outside mask %.1f'%r)
# shifted alternatives
f0=None
