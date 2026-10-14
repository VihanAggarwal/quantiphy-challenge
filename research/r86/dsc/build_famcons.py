"""Candidate on combo3 (research only; not a submission): scene-family consistency levers from the dataset's
construction (test inputs + our own answers only; validation labels are never read here).

A  QPOOL  identical STATIC question text (size / static distance) asked in >= 3 base clips of one eye-verified
          extended family (path85_d3 TS_ext): a row > 1.3x off the log-mean of the other base clips, whose answers
          agree within 1.3x, takes that log-mean.  Premise check (test inputs): 23/23 size priors stated in >= 2 clips
          of one family carry identical values (labels are Blender read-outs of one asset).
B  MISSED FACTS  stated size facts of the same asset in a clip the families missed (verified on frames):
          simulation_0012(+seg) is the top-down camera of the 0010-0014 bird/house/cart scene -> bird length 1.19 m
          (0010's prior), wingspan rescaled by the same factor; dragon 0282/0302/0309 body length -> 0.75 m (0283's
          prior; same asset, README: body length = AABB length = the prior 'length').
C  README  'Body length of animals (e.g. the prior "length of the small bird"): AABB length' -> small-bird length
          rows of 0088/0090/0091 take 0089's stated 0.94 m (lower confidence).
D  DEPTH-IDENTICAL  simulation_0026(+seg): human depth track 114.8319/114.8356 m is byte-identical to 0025's, which
          states 'speed of the person = 1.3m/s' -> 1.3 (previously declined as a coin flip; separate slot).
E  SCRIPTED KINEMATICS  untimed acceleration prior/fact = uniformly accelerated (App. D.1.3 regime tag); objects that
          start at rest at t=0 (App. C.1.3 analytic script s=1/2 a t^2): Blender backward-difference label
          v(t) = a (t - 1/(2 fps)).  Only rows moved > 3%.
"""
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/r86/dsc')
from common import *
OUTD=f'{ROOT}/research/r86/dsc'
d=load(); new=d.set_index('qid').pred.copy(); log=[]
def setv(q,v,lever,why):
    old=new[q]; new[q]=v; log.append(dict(qid=q,video_id=d.set_index('qid').video_id[q],cat=d.set_index('qid').cg[q],lever=lever,old=old,new=v,ratio=v/old,why=why))
# A
A=pd.read_csv(f'{OUTD}/qpool_cands.csv')
for r in A.itertuples():
    if r.qid==992: continue  # dragon handled by its stated fact (B)
    setv(r.qid,r.new,'A_qpool',f'others {r.others}')
# B
P=d.set_index('qid').pred
k=1.19/P[6]; setv(6,1.19,'B_fact','0010 prior length of the bird = 1.19m'); setv(7,P[7]*k,'B_fact',f'wingspan x{k:.3f} (same-clip scale from the fact)')
k2=1.19/P[1649]; setv(1649,1.19,'B_fact','0010 prior'); setv(1650,P[1650]*k2,'B_fact',f'wingspan x{k2:.3f}')
for q in (992,1469,1486): setv(q,0.75,'B_fact','0283 prior length of the dragon = 0.75m')
# C
for q in (134,145,149): setv(q,0.94,'C_readme','0089 prior length of the small bird = 0.94m (AABB convention)')
# D
for q in (1115,1689): setv(q,1.3,'D_depthid','0025 identical human depth track, states 1.3 m/s')
# E  (a, fps=24, t)
E={1463:(5,1.0),1493:(5,1.0),1488:(2,1.0),1489:(2,2.0),365:(2.639,1.0),366:(2.639,1.5),1547:(2.639,1.0),1548:(2.639,1.5)}
for q,(a,tt) in E.items():
    v=a*(tt-1/48)
    if abs(np.log(v/P[q]))>0.03: setv(q,v,'E_kin',f'a={a} from rest: a(t-1/2fps)')
L=pd.DataFrame(log)
sub=pd.read_csv(f'{ROOT}/submissions/trackA_combo3_on_combo2.csv'); sub['parsed_value']=new.values
assert len(sub)==3289 and np.isfinite(sub.parsed_value).all() and (sub.parsed_value>0).all()
sub.to_csv(f'{OUTD}/cand_famcons_on_combo3.csv',index=False); L.to_csv(f'{OUTD}/changes_famcons.csv',index=False)
m=pd.read_pickle(f'{ROOT}/research/r86/loss_audit/master.pkl'); L['scored']=L.qid.map(m.scored)
pd.set_option('display.width',220); pd.set_option('display.max_colwidth',60)
print(L.to_string()); print(L.groupby(['lever','cat']).agg(n=('qid','count'),scored=('scored','sum')))
