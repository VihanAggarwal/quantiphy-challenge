from common import *

K_BB=166.1   # f*D for the basketball with deq*cos^1.5 (calibrated on static stated basketballs, round-1 remeasure)
def load_tr(take):
    r=json.load(open(f'{OUT}/tr_{take}.json'))
    return {k:{int(i):d for i,d in r[k].items()} for k in r}
def cosa(u,v,f=F):
    return f/np.sqrt(f*f+(u-CX)**2+(v-CY)**2)
def size_range(d,k=K_BB,key='deq',f=F):
    c=cosa(d['cx'],d['cy'],f)
    if key=='deq': return k/(d['deq']*c**1.5)
    return k/(d[key]*c)
def plane_point(u,v,n,h,R,f=F):
    # n: unit floor normal pointing up (camera coords: y down), floor: n.X=-h ; centre plane n.X=-h+R
    r=ray(u,v,f); t=(-h+R)/(n@r); return t*r
def fit_plane(P,w=None):
    P=np.asarray(P); w=np.ones(len(P)) if w is None else np.asarray(w)
    c=(P*w[:,None]).sum(0)/w.sum(); U,s,Vt=np.linalg.svd((P-c)*np.sqrt(w)[:,None]); n=Vt[2]
    if n[1]>0: n=-n
    return n,-(n@c)   # n.X = -hc  -> hc = distance of plane below camera
def line_normal(a,b):
    # image line y=a x+b -> back-projected plane normal
    p1=np.array([(0-CX)/F,(b-CY)/F,1.0]); p2=np.array([(1000-CX)/F,(a*1000+b-CY)/F,1.0])
    m=np.cross(p1,p2); return m/np.linalg.norm(m)
def capframe_pos(tr,c):
    # position of a track at capture frame c (interpolating the dropped capture frames 12, 37)
    inv={cap(k):k for k in tr}
    if c in inv: return tr[inv[c]]
    if c-1 in inv and c+1 in inv:
        a,b=tr[inv[c-1]],tr[inv[c+1]]
        return {kk:(a[kk]+b[kk])/2 for kk in ['cx','cy','deq','minor','major','dhull']}
    return None
