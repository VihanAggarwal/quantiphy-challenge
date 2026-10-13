from build_s3 import *
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',60); pd.set_option('display.max_rows',200)
for v in ['simulation_0074','simulation_0035','simulation_0026','simulation_0040','simulation_0036','simulation_0031','simulation_0023','simulation_0025','simulation_0039','simulation_0310','simulation_0311','simulation_0143']:
    g=A[A.video_id==v]
    print(v); print(g[['qid','question','kind','value','v3','src','line','why']].to_string() if len(g) else '  (no facts)')
# all S3 clips' facts
print(A[A.cat=='S3'][['qid','video_id','question','kind','value','v3','src','line','why']].to_string())
