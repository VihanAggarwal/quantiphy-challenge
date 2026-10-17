import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0038_segmented.mp4')
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f)
print(len(fr))
# duplicates
d=[np.abs(fr[i].astype(int)-fr[i-1].astype(int)).mean() for i in range(1,len(fr))]
print('dup diffs', [ (i+1,round(x,3)) for i,x in enumerate(d) if x<0.05])
# rock mask on frame 30
g=fr[30].astype(np.int16)
nonw=(255-g.min(axis=2))>30
n,lab,st,cen=cv2.connectedComponentsWithStats(nonw.astype(np.uint8))
order=np.argsort(-st[:,cv2.CC_STAT_AREA])
for k in order[:6]:
    print(k, st[k], cen[k])
