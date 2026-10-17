import cv2, numpy as np
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/remeasure_work/'
def load(v, gray=False):
    c=cv2.VideoCapture(D+'simulation_%s.mp4'%v); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) if gray else f)
    return np.array(fr)
def frame(v,k):
    c=cv2.VideoCapture(D+'simulation_%s.mp4'%v); c.set(1,k); ok,f=c.read(); return f
