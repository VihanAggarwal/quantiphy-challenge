import cv2, sys
def gridcrop(src,dst,x0,y0,x1,y1,s=4,step=10):
    f=cv2.imread(src); c=f[y0:y1,x0:x1]; c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
    for x in range(x0-x0%step+step,x1,step):
        L=c.shape[0] if x%50==0 else 12
        col=(0,255,255) if x%50==0 else (0,0,255)
        cv2.line(c,((x-x0)*s,0),((x-x0)*s,L if x%50==0 else 12),col,1)
        if x%50==0: cv2.putText(c,str(x),((x-x0)*s+2,24),cv2.FONT_HERSHEY_SIMPLEX,0.5,col,1)
    for y in range(y0-y0%step+step,y1,step):
        col=(0,255,255) if y%50==0 else (0,0,255)
        cv2.line(c,(0,(y-y0)*s),(c.shape[1] if y%50==0 else 12,(y-y0)*s),col,1)
        if y%50==0: cv2.putText(c,str(y),(14,(y-y0)*s-3),cv2.FONT_HERSHEY_SIMPLEX,0.5,col,1)
    cv2.imwrite(dst,c)
if __name__=='__main__':
    a=sys.argv; gridcrop(a[1],a[2],*map(int,a[3:7]),s=int(a[7]) if len(a)>7 else 4)
