import re, os, glob, sys
import pandas as pd

def get_ident(file):
    a={}
    with open(file, encoding="utf8") as f:
        text=f.read()
        taj_pattern=r'\d{3}-\d{3}-\d{3}'
        dob_pattern=r'Születési dátum\.*:\s*\d{4}\.\d{2}\.\d{2}'
        dob_pattern2=r'Szül.dátum:\s*\d{4}\.\d{2}\.\d{2}'
        adm_date_pattern=r'Felvételi dátum\.*:\s+\d{4}.\d{2}.\d{2}'
        sex_pattern=r'Születési név...:\s\S+'
        bno_pattern=r'[A-Z]\d{2,}[A-Z]?\d*'
        beav_pattern=r' \d{5} '
        nihss_pattern=r'NI?HSS: \d+'
        mrs_pattern=r'mRS: \d+'
        rr_pattern=r'RR:\s*\d+/\d+'
        pulse_pattern=r'P:\s*\d+'

        taj=re.findall(taj_pattern, text)
        taj=taj[0].replace("-","")
        
        try:
            dob=re.findall(dob_pattern, text)[0]
            # print(dob)
            dob=dob.split(":")[1]
        except IndexError:
            try:
                dob=re.findall(dob_pattern2, text)[0]
                # print(dob)
                dob=dob.split(":")[1]
            except IndexError:
                dob=None

        try:
            adm_date=re.findall(adm_date_pattern, text)[0]
            adm_date=adm_date.split(":")[1]
        except IndexError:
            adm_date=None

        bno_list=re.findall(bno_pattern, text)

        beav_list=re.findall(beav_pattern, text)
        for i in range(len(beav_list)):
            new_item=beav_list[i].replace(" ","")
            beav_list[i]=new_item
                    
        try:
            nihss=re.findall(nihss_pattern, text)[0]
            nihss=nihss.split()[1]
        except IndexError:
            nihss=None

        try:
            mrs=re.findall(mrs_pattern, text)[0]
            mrs=mrs.split()[1]
        except IndexError:
            mrs=None

        try:
            rr=re.findall(rr_pattern, text)[0]
            rr=rr.split()[1]
        except IndexError:
            rr=None

        try:
            pulse=re.findall(pulse_pattern, text)[0]
            pulse=pulse.split()[1]
        except IndexError:
            pulse=None

        a["Patient_ID"]=taj
        a["DOB"]=dob
        a["Admission_date"]=adm_date
        try:
            sex=re.findall(sex_pattern, text)[0]
            a["Sex"]="female"
        except IndexError:
            a["Sex"]="male"

        if "I48H0" not in bno_list:
            a["AF"]="no"
        else:
            a["AF"]="known/recent"

        if "06042" in beav_list:
            a["Alteplase"]="yes"
        
        if "I10H0" in bno_list:
            a["HT"]="yes"

        if rr:
            a["RR sys"]=rr.split("/")[0]
            a["RR dia"]=rr.split("/")[1]
        a["P"]=pulse
        a["NIHSS"]=nihss
        a["mRS"]=mrs

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
            except IndexError: 
                val=None
            # return {i:p}
            # a["no"]=i
            if "Tromboplasztin" in par:
                try:
                    # val=p[0].split(" ")[3]
                    vals=re.findall(r'\d*[,.]?\d*', par)
                    for i in vals:
                        if i != "":
                            val=i
                except IndexError: pass
            a[f"{i}_{par}"]=val
            
    return a

def get_echo(file):
    regs=[
        r"Echo\w+\s?\(?\d{4}\.?\d{2}?\.?\d{2}?\.?.*",
        r"Ao\w*:?\s+\d*-?\d*-?\d*-?",
        r"B\w+\s?\w*:\s+\d+\s*\w+",
        r"EDD:\s+\d+",
        r"ESD:\s+\d+",
        r"EDV:\s+\d+",
        r"ESV:\s+\d+",
        r"EF:\s+\d+",
        r"IVS:\s+\d+",
        r"PW:\s+\d+",
        r"TAPSE:\s+\d+",
        r"E/?A: \d+/\d+"
    ]
    a={}
    for reg in regs:
        with open(file, encoding="utf8") as f:
            text=f.read()
            try:
                match=re.findall(reg, text)[0]
                # print(match)

                dates=re.findall(r'\d{4}\.?\d{2}?\.?\d{2}?',match)
                if dates:
                    a["date"]=dates[0]

                # if "Ao" in match:
                #     a["Aorta"]=re.split(r'\s+', match)[1]

                if not "Echo" in match:
                    par=match.split(":")[0]
                    val=match.split(" ")[-1]
                    a[par]=val
            except IndexError:
                pass

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
"Akt.Parciális Tromboplasztin",
"Kvantitatív D-dimer",
"Haemoglobin A1C",
"Triglicerid",
"LDL-koleszterin"
]

if __name__ == "__main__":

    if len(sys.argv)>1:
        path=os.path.abspath(sys.argv[1])
    else:
        path = os.getcwd()
    

    for pdf in glob.glob(f"{path}/*.pdf"):
        os.system(f"python -m fitz gettext {pdf}")
    
    for txt in glob.glob(f"{path}/*.txt"):
        orig_fname=txt.split("\\")[-1].split(".")[0]
        df = pd.read_fwf(txt)
        # print(df)
        result={}
        result.update(get_ident(txt))
        result.update(get_echo(txt))
        for param in params:
            result.update(get_lab_param(df, param))

        output_fname=result["Patient_ID"]
        labs=pd.DataFrame(result, index=[0])
        labs.to_excel(f"{path}/{output_fname}.xlsx")

        os.system(f"ren {path}\{orig_fname}.pdf {output_fname}.pdf")
        os.system(f"erase {path}\{orig_fname}.txt")
        
        