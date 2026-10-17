import cv2, numpy as np
from common import load
for tag in 'ox':
    fr=load(tag)
    f=fr[18]; hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    for name,(x0,x1,y0,y1) in {'toybody':(440,465,170,215),'hand':(440,480,255,270),'forearm':(330,380,250,290)}.items():
        p=hsv[y0:y1,x0:x1].reshape(-1,3)
        print(tag,name,'H',np.percentile(p[:,0],[10,50,90]),'S',np.percentile(p[:,1],[10,50,90]),'V',np.percentile(p[:,2],[10,50,90]))
