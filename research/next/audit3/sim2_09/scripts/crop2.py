import cv2,numpy as np,sys
def save(v,fi,x0,y0,x1,y1,out,scale=1.0,step=50):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    c.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,f=c.read()
    im=f[y0:y1,x0:x1].copy()
    im=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    pad=30
    canvas=np.full((im.shape[0]+2*pad,im.shape[1]+2*pad,3),255,np.uint8)
    canvas[pad:-pad,pad:-pad]=im
    for x in range(x0,x1):
        if x%step==0:
            X=int(pad+(x-x0)*scale)
            cv2.line(canvas,(X,pad-8),(X,pad),(0,0,255),1); cv2.line(canvas,(X,canvas.shape[0]-pad),(X,canvas.shape[0]-pad+8),(0,0,255),1)
            cv2.putText(canvas,str(x),(X-12,10),cv2.FONT_HERSHEY_SIMPLEX,0.3,(0,0,0),1)
        elif x%10==0:
            X=int(pad+(x-x0)*scale)
            cv2.line(canvas,(X,pad-3),(X,pad),(0,0,0),1); cv2.line(canvas,(X,canvas.shape[0]-pad),(X,canvas.shape[0]-pad+3),(0,0,0),1)
    for y in range(y0,y1):
        if y%step==0:
            Y=int(pad+(y-y0)*scale)
            cv2.line(canvas,(pad-8,Y),(pad,Y),(0,0,255),1); cv2.line(canvas,(canvas.shape[1]-pad,Y),(canvas.shape[1]-pad+8,Y),(0,0,255),1)
            cv2.putText(canvas,str(y),(0,Y+3),cv2.FONT_HERSHEY_SIMPLEX,0.3,(0,0,0),1)
        elif y%10==0:
            Y=int(pad+(y-y0)*scale)
            cv2.line(canvas,(pad-3,Y),(pad,Y),(0,0,0),1); cv2.line(canvas,(canvas.shape[1]-pad,Y),(canvas.shape[1]-pad+3,Y),(0,0,0),1)
    cv2.imwrite(out,canvas)
a=sys.argv
save(a[1],int(a[2]),int(a[3]),int(a[4]),int(a[5]),int(a[6]),a[7],float(a[8]) if len(a)>8 else 1.0,int(a[9]) if len(a)>9 else 50)
