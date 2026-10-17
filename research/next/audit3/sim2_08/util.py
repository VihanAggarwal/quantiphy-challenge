import cv2, numpy as np
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
    fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    return fr
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_08/'
def save(name, img, x0,y0,x1,y1, k=4, grid=20):
    cr=img[y0:y1,x0:x1].copy()
    cr=cv2.resize(cr,None,fx=k,fy=k,interpolation=cv2.INTER_NEAREST)
    for x in range((x0//grid+1)*grid, x1, grid):
        cv2.line(cr,((x-x0)*k,0),((x-x0)*k,6),(0,255,255),1)
        if x%100==0: cv2.putText(cr,str(x),((x-x0)*k+2,18),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1)
    for y in range((y0//grid+1)*grid, y1, grid):
        cv2.line(cr,(0,(y-y0)*k),(6,(y-y0)*k),(0,255,255),1)
        cv2.putText(cr,str(y),(8,(y-y0)*k+4),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1)
    cv2.imwrite(W+name, cr)
