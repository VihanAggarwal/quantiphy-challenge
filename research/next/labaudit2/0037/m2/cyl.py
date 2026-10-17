import numpy as np, cv2, itertools
FL=np.array([209.86651675,535.34671656]);FR=np.array([1141.40204572,586.79827895]);BR=np.array([917.62267403,467.91646082]);BL=np.array([453.34799452,446.40715519])
img=np.array([FL,FR,BR,BL])
def pose(f,W=0.760,D=0.603,cx=640,cy=360):
    K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]])
    obj=np.array([[0,0,0],[W,0,0],[W,D,0],[0,D,0]],float)
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
    ok,rv,tv=cv2.solvePnP(obj,img,K,None,rv,tv,True,flags=cv2.SOLVEPNP_ITERATIVE)
    pr,_=cv2.projectPoints(obj,rv,tv,K,None)
    res=np.abs(pr.reshape(-1,2)-img).max()
    return K,rv,tv,res
def proj(K,rv,tv,P):
    pr,_=cv2.projectPoints(np.asarray(P,float).reshape(-1,3),rv,tv,K,None); return pr.reshape(-1,2)
def cyl_outline(K,rv,tv,C,r,H,n=360):
    th=np.linspace(0,2*np.pi,n,endpoint=False)
    bot=np.c_[C[0]+r*np.cos(th),C[1]+r*np.sin(th),np.zeros(n)]
    top=bot.copy(); top[:,2]=H
    pb=proj(K,rv,tv,bot); pt=proj(K,rv,tv,top)
    return pb,pt
def measure(K,rv,tv,C,r,H):
    pb,pt=cyl_outline(K,rv,tv,C,r,H)
    allp=np.r_[pb,pt]
    return np.array([allp[:,0].min(),allp[:,0].max(),pt[:,1].min(),pb[:,1].max()])
def ray_plane(K,rv,tv,uv,z=0):
    R,_=cv2.Rodrigues(rv); cam=-R.T@tv.ravel()
    d=R.T@np.linalg.inv(K)@np.array([uv[0],uv[1],1.])
    s=(z-cam[2])/d[2]; return cam+s*d, cam
def fit(K,rv,tv,meas):
    # init
    P,_=ray_plane(K,rv,tv,((meas[0]+meas[1])/2,meas[3]))
    x=np.array([P[0],P[1]+0.03,0.03,0.09])
    for it in range(50):
        m=measure(K,rv,tv,x[:2],x[2],x[3]); r=m-meas
        J=np.zeros((4,4))
        for j in range(4):
            dx=np.zeros(4); dx[j]=1e-5
            J[:,j]=(measure(K,rv,tv,(x+dx)[:2],(x+dx)[2],(x+dx)[3])-m)/1e-5
        x=x-np.linalg.lstsq(J,r,rcond=None)[0]
    return x, measure(K,rv,tv,x[:2],x[2],x[3])-meas
if __name__=='__main__':
    for f in [680,711,740]:
        K,rv,tv,res=pose(f)
        R,_=cv2.Rodrigues(rv); cam=-R.T@tv.ravel()
        print('f',f,'reproj max',round(res,2),'cam pos (table coords, m)',cam.round(3))
        for meas in [[443.5,498.8,407.8,485.5],[443.5,498.8,407.8,484.5],[443.5,498.8,407.8,486.5],[443.0,499.0,407.5,485.5]]:
            x,rr=fit(K,rv,tv,np.array(meas))
            C=np.array([x[0],x[1],0.045]); R,_=cv2.Rodrigues(rv)
            Pc=R@C+tv.ravel()
            print('  meas',meas,'C=',x[:2].round(4),'r=%.4f D=%.2fcm H=%.2fcm'%(x[2],200*x[2],100*x[3]),'resid',rr.round(2),'range to centre %.3f'%np.linalg.norm(Pc))
