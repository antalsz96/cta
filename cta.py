import fitz, csv, re
import pandas as pd
import numpy as np

def get_lab_param(file, lab_param):
    a={}
    for i in range(file.shape[0]):
        if lab_param in file.loc[i][0] and "dializált" not in file.loc[i][0]:
            pattern=r'\s{2,}'
            p=file.loc[i][0].replace(",",".")
            p=re.split(pattern,p)
            par=p[0]
            val=p[1]
            # return {i:p}
            # a["no"]=i
            a[par]=val
    return a

# if __name__ == "__main__":
