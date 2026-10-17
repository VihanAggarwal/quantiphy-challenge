# Table plane from vanishing points (f=711), scale options, and ball-centre ranges near t=1.5
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
C={k:np.array(v) for k,v in json.load(open(D+'corners.json')).items()}
T=json.load(open(D+'track.json'))
def hh(p): return np.array([p[0],p[1],1.])
def plane(f=711.,cx=640.,cy=360.,Cc=C):
    K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]]); Ki=np.linalg.inv(K)
    def vp(a,b,c,d): return np.cross(np.cross(hh(a),hh(b)),np.cross(hh(c),hh(d)))
    v1=Ki@vp(Cc['BL'],Cc['FL'],Cc['BR'],Cc['FR']); v2=Ki@vp(Cc['BL'],Cc['BR'],Cc['FL'],Cc['FR'])
    v1/=np.linalg.norm(v1); v2/=np.linalg.norm(v2)
    n=np.cross(v1,v2); n/=np.linalg.norm(n)
    if n[1]<0: n=-n   # n points "down" in camera coords (y down) -> plane n.X = h (h>0)
    return n,Ki,v1@v2
def X_on(p,n,Ki,hp):
    r=Ki@hh(p); return r*hp/(n@r)
if __name__=='__main__':
  for f in [690,711,722,740]:
      n,Ki,c12=plane(f)
      P={k:X_on(v,n,Ki,1.0) for k,v in C.items()}
      Wf=np.linalg.norm(P['FR']-P['FL']); Wb=np.linalg.norm(P['BR']-P['BL']); Dl=np.linalg.norm(P['FL']-P['BL']); Dr=np.linalg.norm(P['FR']-P['BR'])
      hW=0.603/((Wf+Wb)/2); hD=0.760/((Dl+Dr)/2)
      # horizon: image of points at infinity on plane: line n.(Ki p)=0
      yh=[(lambda x: (lambda a,b,c: -(a*x+c)/b)(*(n@Ki)))(x) for x in [640]]
      print('f %d cos(v1,v2) %.4f n %s  h from width60.3: %.4f  from depth76: %.4f   Wf/Wb %.3f Dl/Dr %.3f horizon y@640 %.1f'%(f,c12,n.round(4),hW,hD,Wf/Wb,Dl/Dr,yh[0]))
      # stated-range anchors: ball centre at plane offset (h - r); surface range ~ |X|-r
      for name,key,R,rad in [('tennis','yel',1.183,0.0335),('ping','wht',1.353,0.020)]:
          out=[]
          for lab,uv in [('v35/c36',None),('c37 interp',None),('v36/c38',None),('v37/c39',None)]:
              pass
          def uvk(r,k): t=T[r][str(k)][key]; return np.array([t['cx'],t['cy']])
          for r in ['x','o']:
              u35,u36,u37=uvk(r,35),uvk(r,36),uvk(r,37)
              cand={'c36':u35,'c37':(u35+u36)/2,'c38':u36,'c39':u37}
              s=[]
              for cn,uv in cand.items():
                  # solve h such that surface range = R : |X(h-rad)| - rad = R ; X scales linearly with (h-rad)
                  Xu=X_on(uv,n,Ki,1.0); hsol=(R+rad)/np.linalg.norm(Xu)+rad
                  s.append('%s h=%.4f'%(cn,hsol))
              print('    %-6s %s: %s'%(name,r,'  '.join(s)))
