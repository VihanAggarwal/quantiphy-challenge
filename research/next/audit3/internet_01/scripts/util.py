import numpy as np
def find_peaks(y,height,distance):
    idx=[i for i in range(1,len(y)-1) if y[i]>=height and y[i]>=y[i-1] and y[i]>=y[i+1]]
    idx=sorted(idx,key=lambda i:-y[i]); keep=[]
    for i in idx:
        if all(abs(i-j)>=distance for j in keep): keep.append(i)
    return np.array(sorted(keep)),None
