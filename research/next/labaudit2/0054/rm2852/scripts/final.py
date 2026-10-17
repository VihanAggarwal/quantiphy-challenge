import sys, os, math, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import ballfit as B
anc_w=3.0735+0.033; r_w=0.033
def run(f, kw, c0=24, c1=39, label=''):
    B.F=f
    r=B.fit('white',c0,c1,anchor=anc_w,**kw)
    tr=B.track('white')
    def Pfit(c): return B.model(r['q'],np.array([c/25]),r['th'],r['rho'],r['g'])[0]
    # observed-pixel clicked points: pixel centroid, surface range = fitted centre range - r
    def Pclick(c):
        u,v=tr[c]; rng=np.linalg.norm(Pfit(c))-r_w
        d=np.array([(u-B.CX)/f,(v-B.CY)/f,1.0]); return d/np.linalg.norm(d)*rng
    vf37=np.linalg.norm(Pfit(38)-Pfit(37))*25; vf38=np.linalg.norm(Pfit(39)-Pfit(38))*25
    vc38=np.linalg.norm(Pclick(39)-Pclick(38))*25
    # dropped c37: click = midpoint-ish of fit
    Vinst=r['q'][3:6]+B.gvec(r['th'],r['rho'],r['g'])*0.5
    print('%-34s f=%.0f rms=%.2f th=%.2f rho=%.2f free-range-check=%.3f | fit c37->38=%.3f  fit c38->39=%.3f  click(video36->37) c38->39=%.3f | inst|V(1.5)|=%.3f V=(%.2f,%.2f,%.2f)'%(label,f,r['rms'],math.degrees(r['th']),math.degrees(r['rho']),np.linalg.norm(Pfit(25)),vf37,vf38,vc38,np.linalg.norm(Vinst),*Vinst))
    return vf37,vf38,vc38
if __name__=='__main__':
    res=[]
    for f in [708,711,722,770]:
        for lab,kw in [('anch, pitch/roll free',{}),('anch, pitch 1.0 roll 0',dict(th=math.radians(1.0),rho=0.0)),('anch, pitch 2.5 roll -0.6',dict(th=math.radians(2.5),rho=math.radians(-0.6))),('anch, tennis-fit pitch -0.1 roll -1.1',dict(th=math.radians(-0.1),rho=math.radians(-1.1)))]:
            res.append(run(f,kw,label=lab))
    res=np.array(res)
    print('ranges over variants: c37->38 %.3f-%.3f  c38->39(fit) %.3f-%.3f  c38->39(click) %.3f-%.3f'%(res[:,0].min(),res[:,0].max(),res[:,1].min(),res[:,1].max(),res[:,2].min(),res[:,2].max()))
    print('medians:',np.median(res,0))
