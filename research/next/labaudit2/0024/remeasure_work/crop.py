import cv2,sys
def crop(src,x0,y0,x1,y1,s,out,step=10,lab=50):
    f=cv2.imread(src)
    c=f[y0:y1,x0:x1].copy()
    c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
    for x in range(x0,x1):
        if x%step==0: cv2.line(c,((x-x0)*s,0),((x-x0)*s,8),(0,0,255),1)
        if x%lab==0: cv2.putText(c,str(x),((x-x0)*s+2,20),0,0.45,(0,0,255),1)
    for y in range(y0,y1):
        if y%step==0: cv2.line(c,(0,(y-y0)*s),(8,(y-y0)*s),(0,0,255),1)
        if y%lab==0: cv2.putText(c,str(y),(10,(y-y0)*s+5),0,0.45,(0,0,255),1)
    cv2.imwrite(out,c)
if __name__=='__main__':
    a=sys.argv
    crop(a[1],*map(int,a[2:7]),a[7],*map(int,a[8:]))
