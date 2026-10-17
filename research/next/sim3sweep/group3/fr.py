import cv2, sys, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/'
def get(vid, i):
    c=cv2.VideoCapture(V+vid+'.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES, i); ok,f=c.read(); return f
def allframes(vid):
    c=cv2.VideoCapture(V+vid+'.mp4'); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
def save(img, name, scale=1.0):
    if scale!=1.0: img=cv2.resize(img,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    cv2.imwrite('/home/user/quantiphy-challenge/research/next/sim3sweep/group3/img/'+name, img)
def crop(vid,i,x0,y0,x1,y1,name,scale=1.0,grid=None):
    f=get(vid,i)[y0:y1,x0:x1].copy()
    if scale!=1.0: f=cv2.resize(f,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST if scale>1 else cv2.INTER_AREA)
    if grid:
        for gx in range(0,x1-x0,grid):
            cv2.line(f,(int(gx*scale),0),(int(gx*scale),f.shape[0]),(0,255,255),1)
            cv2.putText(f,str(x0+gx),(int(gx*scale)+2,12),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1)
        for gy in range(0,y1-y0,grid):
            cv2.line(f,(0,int(gy*scale)),(f.shape[1],int(gy*scale)),(0,255,255),1)
            cv2.putText(f,str(y0+gy),(2,int(gy*scale)+12),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1)
    save(f,name)
if __name__=='__main__':
    vid=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]; sc=float(sys.argv[3]) if len(sys.argv)>3 else 0.4
    for i in idx:
        save(get(vid,i), f'{vid}_f{i}.png', sc)
