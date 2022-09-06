import fitz, csv, re, os, glob
import pandas as pd
import numpy as np

def get_ident(file):
    a={}
    with open(file, encoding="utf8") as f:
        text=f.read()
        taj_pattern=r'\d{3}-\d{3}-\d{3}'
        dob_pattern=r'Szül.dátum:\s+\d{4}.\d{2}.\d{2}'
        adm_date_pattern=r'Felvételi dátum.:\s+\d{4}.\d{2}.\d{2}'
        sex_pattern=r'Születési név...:\s\S+'

        taj=re.findall(taj_pattern, text)
        taj=taj[0].replace("-","")
        
        dob=re.findall(dob_pattern, text)[0]
        dob=dob.split()[1]

        adm_date=re.findall(adm_date_pattern, text)[0]
        adm_date=adm_date.split()[2]

        a["Patient_ID"]=taj
        a["DOB"]=dob
        a["Admission_date"]=adm_date
        
        try:
            sex=re.findall(sex_pattern, text)[0]
            a["Sex"]="female"
        except IndexError:
            a["Sex"]="male"

    return a

def get_lab_param(file, lab_param):
    a={}
    for i in range(file.shape[0]):
        text=file.loc[i][0]
        if lab_param in text:
            pattern=r'\s{2,}'
            p=text#.replace(",",".")
            p=re.split(pattern,p)
            par=p[0]
            try:
                val=p[1]
            except IndexError: pass
            # return {i:p}
            # a["no"]=i
            # if "Tromboplasztin" in par:
            #     val=p[0].split(" ")[3]
            a[par]=val
            
    return a

params=[
"Glükóz",
"Szenzitív C-reaktív protein",
"Troponin T (high sensitive)",
"proBNP  ",
"Karbamid (Urea)",
"Kreatinin",
"eGFR-EPI  ",
"Fehérvérsejt szám",
"Protrombin INR",
"Akt.Parciális Tromboplasztin Idõ",
"Kvantitatív D-dimer",
"Haemoglobin A1C",
"Triglicerid",
"LDL-koleszterin"
]

if __name__ == "__main__":

    path = os.getcwd()
    for pdf in glob.glob(f"{path}/*.pdf"):
        os.system(f"python -m fitz gettext {pdf}")
    
    for txt in glob.glob(f"{path}/*.txt"):
        fname=txt.split("\\")[-1].split(".")[0]
        df = pd.read_fwf(txt)
        # print(df)
        result={}
        result.update(get_ident(txt))
        for param in params:
            result.update(get_lab_param(df, param))

        labs=pd.DataFrame(result, index=[0])
        labs.to_excel(f"{fname}.xlsx")