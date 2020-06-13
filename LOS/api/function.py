import pandas as pd
import statsmodels.api as sm
import itertools
#from django_pandas.io import read_frame




def get_dum(x):
    for elem in df1[x].unique():
        df1[str(elem)] = df1[x] == elem

def conv(x):
    if x == True:
        return 1
    else:
        return 0



def load_data(x):
    x_R = pd.DataFrame(x)


    def mean_std(x):
        w = (str(round(pd.DataFrame(x).mean(),1)[0]))
        e = (str(round(pd.DataFrame(x).std(),1)[0]))
        t = w + "(" + e +")"
        return t

    def inout_count(x):
        a = []
        b = []
        for i in x:

            if i == 'Out Born':
                b.append(x)
            else:
                a.append(x)

        inborn = str(len(a))
        outborn = str(len(b))
        return (inborn,outborn)

    def median_IQR(x):
        q1 = str(pd.DataFrame(x).quantile(.25)[0])
        q2 = str(pd.DataFrame(x).quantile(.75)[0])
        q3 = str(pd.DataFrame(x).median()[0])
        q4 = q3 + "(" +q1 +"-" + q2 + ")"



        return q4

    def gender_count(x):
        a = []
        b = []
        for i in x:

            if i == 'Male':
                a.append(x)
            else:
                b.append(x)

        male = str(len(a))
        female = str(len(b))
        return (male,female)

    def MOD_count(x):
        a = []
        b = []
        for i in x:

            if i == 'LSCS':
                b.append(x)
            else:
                a.append(x)

        nvd = str(len(a))
        lscs = str(len(b))
        return (nvd,lscs)


    def single_count1(x):

        a = []
        b = []
        for i in x:

            if i == 'Twins' or i == 'Triplets':
                a.append(x)
            else:
                b.append(x)

        multiple = str(len(a))
        single = str(len(b))
        return (single,multiple)

    def neofax_count(x):
        a = []
        b = []
        c=[]
        for i in x:

            if i == 'No_err':
                a.append(x)
            elif i == 'ERROR':
                b.append(x)
            else:
                c.append(x)

        no_error = str(len(a))
        error = str(len(b))
        NE = str(len(c))

        return (no_error,error,NE)

    def medadmin_count(x):
        a = []
        b = []
        c=[]
        for i in x:

            if i == 'No_err':
                a.append(x)
            elif i == 'ERROR':
                b.append(x)
            else:
                c.append(x)

        no_error = str(len(a))
        error = str(len(b))
        NE = str(len(c))
        return (no_error,error,NE)

    def espgan_count(x):
        a = []
        b = []
        c=[]
        for i in x:

            if i == 'No_err':
                a.append(x)
            elif i == 'ERROR':
                b.append(x)
            else:
                c.append(x)

        no_error = str(len(a))
        error = str(len(b))
        NE = str(len(c))
        return (no_error,error,NE)

    def nutri_count(x):
        a = []
        b = []
        c=[]
        for i in x:

            if i == 'No_err':
                a.append(x)
            elif i == 'ERROR':
                b.append(x)
            else:
                c.append(x)

        no_error = str(len(a))
        error = str(len(b))
        NE = str(len(c))
        return (no_error,error,NE)

    def RDS_count(x):
        a = []
        b = []
        c=[]
        for i in x:

            if i == True:
                a.append(x)
            else:
                b.append(x)


        t = str(len(a))
        f = str(len(b))
        return (t,f)

    def jaundice_count(x):
        a = []
        b = []
        c=[]
        for i in x:

            if i == True:
                a.append(x)
            else:
                b.append(x)


        t = str(len(a))
        f = str(len(b))
        return (t,f)

    def spesis_count(x):
        a = []
        b = []
        c=[]
        for i in x:

            if i == True:
                a.append(x)
            else:
                b.append(x)


        t = str(len(a))
        f = str(len(b))
        return (t,f)

    def spesis_count1(x):
        a = []
        b = []
        c=[]
        for i in x:

            if i == 'true':
                a.append(x)
            else:
                b.append(x)


        t = str(len(a))
        f = str(len(b))
        return (t,f)

    Dict = {'Count': str(x_R.count()[0]), 'Gestation(Weeks)': mean_std(x_R['Gestation']),'Birth Weight(gms)': mean_std(x_R['birthweight']),'LOS*(Days)':median_IQR(x_R['los']),'Admission Weight(gms)' : mean_std(x_R['admissionweight']),'Male': gender_count(x_R['Gender'])[0],'Female' : gender_count(x_R['Gender'])[1],'One Min APGAR' : mean_std(x_R['ONEMIN_APGAR']),'Five Min APGAR' : mean_std(x_R['FIVEMIN_APGAR']),'NVD' : MOD_count(x_R['MODE_OF_DELIVERY'])[0],'LSCS' : MOD_count(x_R['MODE_OF_DELIVERY'])[1],'In Born' : inout_count(x_R['inout_patient_status'])[0],'Out Born' : inout_count(x_R['inout_patient_status'])[1],'Jaundice True' : jaundice_count(x_R['JAUNDICE'])[0],'Jaundice False' : jaundice_count(x_R['JAUNDICE'])[1],'Sepsis True' : spesis_count(x_R['SEPSIS'])[0],'Sepsis False' : spesis_count(x_R['SEPSIS'])[1],'RDS True' : RDS_count(x_R['RDS'])[0],'RDS False' : RDS_count(x_R['RDS'])[1],'Single' : single_count1(x_R['baby_type'])[0],'Multiple' : single_count1(x_R['baby_type'])[1],'Antenatal Steroids True' : spesis_count1(x_R['ANTENATA_STEROIDS'])[0],'Antenatal Steroids False' : spesis_count1(x_R['ANTENATA_STEROIDS'])[1]}





    d1 = Dict
    return d1
