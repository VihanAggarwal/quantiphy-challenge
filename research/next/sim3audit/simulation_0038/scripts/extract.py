import cv2, sys, os
out='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0038/frames'
for v, idxs in [('simulation_0037',[0,24,48,71]),('simulation_0037_segmented',[0,24,48,71]),('simulation_0038_segmented',[0,25,50,74]),('simulation_0036',[24]),('simulation_0039',[25])]:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    i=0
    while True:
        ok,f=c.read()
        if not ok: break
        if i in idxs:
            cv2.imwrite(f'{out}/{v}_f{i:03d}.png', f)
        i+=1
