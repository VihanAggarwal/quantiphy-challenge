import sys, os, pickle
W='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/scenegraph/work'
MD='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3'
sys.path.insert(0,W); os.chdir(W)
sys.dont_write_bytecode=True
import build as B
from build import *
import labpool2
labpool2.ti=ti; labpool2.v3=v3
from labpool2 import lab_size_groups, lab_facts, usc
sys.path.insert(0,'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/scene_graph')
import fix_build as FB
log=[]
new,why=FB.variant_fixed(('S3',),rule_LAB=True,log=log)
G=lab_size_groups(t)
out=dict(why=why,new=new,log=log,groups=G,A=A,t=t)
pickle.dump(out,open(MD+'/sg_state.pkl','wb'))
print(len(G),'groups'); print(log)
