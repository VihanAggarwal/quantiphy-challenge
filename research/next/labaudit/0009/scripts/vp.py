import cv2, numpy as np
f=711.;CX=640;CY=360
res={}
for fr in [0,24,48]:
    im=cv2.imread('frames/ro_f%02d.png'%fr)
    g=cv2.GaussianBlur(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),(3,3),0).astype(float)
    gx=np.abs(cv2.Sobel(g,cv2.CV_64F,1,0,ksize=5))
    # seeds: (x_top,y_top,x_bot,y_bot) rough
    seeds={'L1':(110,15,215,320),'L2':(135,15,238,315),'B1':(515,10,530,125),'B2':(545,10,560,150),'B3':(640,10,650,185),'B4':(665,10,670,185),'R1':(1215,10,1160,270),'R2':(1250,10,1190,270)}
    lines={}
    for k,(x0,y0,x1,y1) in seeds.items():
        pts=[]
        for y in range(y0,y1,3):
            xe=x0+(x1-x0)*(y-y0)/(y1-y0)
            a=int(xe-8);b=int(xe+9)
            if a<0 or b>1279: continue
            row=gx[y,a:b]
            j=np.argmax(row)
            if row[j]>np.percentile(gx,90):
                # subpixel
                if 0<j<len(row)-1:
                    den=row[j-1]-2*row[j]+row[j+1]
                    dj=0.5*(row[j-1]-row[j+1])/den if den!=0 else 0
                else: dj=0
                pts.append((a+j+dj,y))
        pts=np.array(pts)
        if len(pts)<8: continue
        # robust line fit x = m y + c
        for it in range(3):
            m,c=np.polyfit(pts[:,1],pts[:,0],1)
            r=np.abs(pts[:,0]-(m*pts[:,1]+c))
            pts=pts[r<max(1.5,2.5*np.median(r))]
        lines[k]=(m,c,len(pts),np.std(pts[:,0]-(m*pts[:,1]+c)))
    res[fr]=lines
    # VP: lines x = m y + c -> homogeneous line: x - m y - c = 0
    A=[];W=[]
    for k,(m,c,n,s) in lines.items():
        l=np.array([1.,-m,-c]); l/=np.linalg.norm(l[:2]); A.append(l)
    A=np.array(A)
    # least squares VP minimizing distance: solve A[:,:2] p = -A[:,2]
    p,_,_,_=np.linalg.lstsq(A[:,:2],-A[:,2],rcond=None)
    d=np.array([(p[0]-CX)/f,(p[1]-CY)/f,1.]);d/=np.linalg.norm(d)
    print('frame',fr,{k:(round(v[0],4),round(v[1],1),v[2],round(v[3],2)) for k,v in lines.items()})
    print('  VP=(%.0f,%.0f) down dir=%s pitch=%.1f deg'%(p[0],p[1],d.round(4),np.degrees(np.arcsin(d[2]))))
    # leave-one-group-out
    for grp in ['L','B','R']:
        keep=[i for i,k in enumerate(lines) if not k.startswith(grp)]
        p2,_,_,_=np.linalg.lstsq(A[keep,:2],-A[keep,2],rcond=None)
        d2=np.array([(p2[0]-CX)/f,(p2[1]-CY)/f,1.]);d2/=np.linalg.norm(d2)
        print('   without %s: VP=(%.0f,%.0f) pitch=%.1f'%(grp,p2[0],p2[1],np.degrees(np.arcsin(d2[2]))))
