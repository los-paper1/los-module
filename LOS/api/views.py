import csv,io
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.views import APIView
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
#from inicu1.response import JSONResponse
#from .function import load_data, NegBi_model, refgrid
from math import sqrt
import json
import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime
import datetime
from api.models import *
from .function import load_data
import itertools

import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
# Create your views here.
def index(request):
    return render(request,'api/index.html')

def home(request):
    return HttpResponse('<h1>Home Blog</h1>')

def about(request):
    return HttpResponse('<h1>Home About</h1>')

def computeErrorLast(creationTime,cuurentDeficitLast, feed, uhid, dateofadmission,gestationWeek,gestationDays, energyMap, proteinMap, lengthStay, currentDiff,cur1):
    intakeEnergy = -1;
    intakeProtein = -1;

    recommendedEnergy = -1;
    recommendedProtein = -1;

    diffEnergy = -1;
    diffProtein = -1;

    resultEnergy = "";
    resultProtein = "";

    isEnergyCorrect = True;
    isProteinCorrect = True;

    startDate = creationTime;

    df = startDate
    weight = -1;

    cur1.execute("select currentdateweight from apollo.baby_visit where uhid ='" + uhid + "' and visitdate >='" +  str(df) + "'")
    currentBabyVisitList = cur1.fetchall()

    if len(currentBabyVisitList) > 0:
      if currentBabyVisitList[0][0] != None:
        weight = currentBabyVisitList[0][0];


    days = lengthStay - 1;

     
    currentGestationWeek = gestationWeek;
    currentGestationDays = gestationDays;
    currentGestationDays += days;
    if currentGestationDays > 6:
      currentGestationWeek = currentGestationWeek + (currentGestationDays / 7);
      currentGestationDays = currentGestationDays % 7;
    
    recommendationEnteral = currentDiff.get("Parenteral");

    #Energy
    if recommendationEnteral == float(1):
      if currentDiff.get("Energy") != None:
        intakeEnergy = ((currentDiff.get("Energy")) * cuurentDeficitLast.get("esphaganIntake").get("Energy")) / 100;
        recommendedEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
        diffEnergy = intakeEnergy - recommendedEnergy;
        if diffEnergy < 0:
          isEnergyCorrect = False;
     
      if currentDiff.get("Protein") != None:

        intakeProtein = ((currentDiff.get("Protein")) * cuurentDeficitLast.get("esphaganIntake").get("Protein")) / 100;
        recommendedProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
        diffProtein = intakeProtein - recommendedProtein;
        if diffProtein < 0:
          isProteinCorrect = False;
     
      
    else:
      if currentDiff.get("Energy") != None:

        intakeEnergy = ((currentDiff.get("Energy")) * cuurentDeficitLast.get("esphaganIntake").get("Energy")) / 100;
        recommendedEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
        diffEnergy = intakeEnergy - recommendedEnergy;
        if diffEnergy < 0:
          isEnergyCorrect = False;

    cur1.execute("Select birthweight from apollo.baby_detail obj where uhid = '"  + uhid  + "' order by creationtime")
    babyDetailList = cur1.fetchall()
    if intakeEnergy != -1:
      energyMap[days][0] = intakeEnergy
      energyMap[days][1] = recommendedEnergy    

      if (intakeEnergy < (90)) or (intakeEnergy > (120)) and intakeEnergy != 0:
        if intakeEnergy < 90:
          energyMap[days][2] = 90
          energyMap[days][3] = intakeEnergy - (90)

        else:
          energyMap[days][2] = 120
          energyMap[days][3] = intakeEnergy - (120)
        
        energyMap[days][4] = "Deviation"
      else:
        energyMap[days][2] = intakeEnergy
        energyMap[days][3] = 0
        energyMap[days][4] = "No Error"
    
    if weight != -1:
       energyMap[days][6] = weight

    

    if intakeProtein != -1:
      proteinMap[days][0] = intakeProtein
      proteinMap[days][1] = recommendedProtein   
      
      if babyDetailList[0][0] < 2500:
        if (intakeProtein < (3)) or (intakeProtein > (4)) and (diffProtein != 0):
          if intakeProtein < 3:
            proteinMap[days][2] = 3
            proteinMap[days][3] = intakeProtein - (3)
          else:
            proteinMap[days][2] = 4
            proteinMap[days][3] = intakeProtein - (4)
          proteinMap[days][4] = "Deviation"
        else:
          proteinMap[days][2] = intakeProtein
          proteinMap[days][3] = 0
          proteinMap[days][4] = "No Error"
        
      else:
        if (intakeProtein < (2)) or (intakeProtein > (3)) and (diffProtein != 0):
          if intakeProtein < 2:
            proteinMap[days][2] = 2
            proteinMap[days][3] = intakeProtein - (2)
          else:
            proteinMap[days][2] = 3
            proteinMap[days][3] = intakeProtein - (3)
          proteinMap[days][4] = "Deviation"

        else:
          proteinMap[days][2] = intakeProtein
          proteinMap[days][3] = 0
          proteinMap[days][4] = "No Error"
       
    if weight != -1:
      proteinMap[days][6] = weight
    


def computeError(creationTime,cuurentDeficitLast, feed, uhid, dateofadmission,gestationWeek,gestationDays,energyMap,proteinMap, lengthStay, fromDateOffsetTwentFourHour, toDateOffsetTwentFourHour, missedLos,cur1):
    intakeEnergy = -1;
    intakeProtein = -1;
   
    recommendedEnergy = -1;
    recommendedProtein = -1;
    
    diffEnergy = -1;
    diffProtein = -1;

    resultEnergy = "";
    resultProtein = "";

    isEnergyCorrect = True;
    isProteinCorrect = True;

    startDate = creationTime;

    df = startDate
    weight = -1;
    cur1.execute("select currentdateweight from apollo.baby_visit where uhid ='" + uhid + "' and visitdate >='" +  str(df) + "'")
    currentBabyVisitList = cur1.fetchall()

    if len(currentBabyVisitList) > 0:
      if currentBabyVisitList[0][0] != None:
        weight = currentBabyVisitList[0][0];
    


    days = lengthStay - 1;

     
    currentGestationWeek = gestationWeek;
    currentGestationDays = gestationDays;
    currentGestationDays = currentGestationDays + days;
    if currentGestationDays > 6:
      currentGestationWeek = currentGestationWeek + (currentGestationDays / 7);
      currentGestationDays = currentGestationDays % 7;

    isRecommendationEnteral = float(1);
    feedTypeEnergy = "";
    feedTypeProtein = "";
    
    duration = (toDateOffsetTwentFourHour.timestamp() - fromDateOffsetTwentFourHour.timestamp()) / (60 * 60);
    
    stay = duration / 24;

    if stay >= 1:
      stay = 1;
    
    #Energy
    if cuurentDeficitLast.get("enteralIntake") != None and cuurentDeficitLast.get("parenteralIntake")!= None and cuurentDeficitLast.get("enteralIntake").get("Energy") != None and cuurentDeficitLast.get("parenteralIntake").get("Energy") != None and cuurentDeficitLast.get("enteralIntake").get("Energy") > 0 and cuurentDeficitLast.get("parenteralIntake").get("Energy") > 0:
      if feed != None and feed[1] != None and "METHOD03" in feed[1]:
        diffEnergy = 0;
        intakeEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
        recommendedEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
  
        if diffEnergy < 0:
          isEnergyCorrect = False;
        
      else:
        diffEnergy = ((cuurentDeficitLast.get("enteralIntake").get("Energy") + cuurentDeficitLast.get("parenteralIntake").get("Energy")) / feed[2]) - cuurentDeficitLast.get("esphaganIntake").get("Energy");
        intakeEnergy = (cuurentDeficitLast.get("enteralIntake").get("Energy") + cuurentDeficitLast.get("parenteralIntake").get("Energy")) / feed[2];
        recommendedEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
        stay = 1;

        if diffEnergy < 0:
          isEnergyCorrect = False;

      feedTypeEnergy = "EN+PN";

    elif cuurentDeficitLast.get("enteralIntake") != None and cuurentDeficitLast.get("enteralIntake").get("Energy") != None and cuurentDeficitLast.get("enteralIntake").get("Energy") > 0:
      if feed != None and feed[1] != None and  "METHOD03" in feed[1]:
        diffEnergy = 0;
        intakeEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
        recommendedEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
  
        if diffEnergy < 0:
          isEnergyCorrect = False;
        
      else:
        diffEnergy = (cuurentDeficitLast.get("enteralIntake").get("Energy") / feed[2]) - cuurentDeficitLast.get("esphaganIntake").get("Energy");
  
        intakeEnergy = cuurentDeficitLast.get("enteralIntake").get("Energy") / feed[2];
        recommendedEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
  
        if diffEnergy < 0:
          isEnergyCorrect = False;
       
      feedTypeEnergy = "EN Only";
    elif cuurentDeficitLast.get("parenteralIntake") != None and cuurentDeficitLast.get("parenteralIntake").get("Energy") != None and cuurentDeficitLast.get("parenteralIntake").get("Energy") > 0:
      if feed != None and feed[1] != None and  "METHOD03" in feed[1]:
        diffEnergy = 0;
        intakeEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
        recommendedEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
        stay = 1;
        if diffEnergy < 0:
          isEnergyCorrect = False;
      
        isRecommendationEnteral = float(1);

      else:
        diffEnergy = (cuurentDeficitLast.get("parenteralIntake").get("Energy") / feed[2]) - cuurentDeficitLast.get("esphaganIntake").get("Energy");
        intakeEnergy = cuurentDeficitLast.get("parenteralIntake").get("Energy") / feed[2];
        recommendedEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
        stay = 1;
        isRecommendationEnteral = float(0);
        if diffEnergy < 0:
          isEnergyCorrect = False;
      
      feedTypeEnergy = "PN Only";
    else:
      if feed != None and feed[1] != None and  "METHOD03" in feed[1]:
        diffEnergy = 0;
        intakeEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
        recommendedEnergy = cuurentDeficitLast.get("esphaganIntake").get("Energy");
  
        if diffEnergy < 0:
          isEnergyCorrect = False;
        
        isRecommendationEnteral = float(0);
        feedTypeEnergy = "EN Only";
    

    #Protein
    if  cuurentDeficitLast.get("parenteralIntake") != None and cuurentDeficitLast.get("enteralIntake") != None and cuurentDeficitLast.get("enteralIntake").get("Protein") != None and cuurentDeficitLast.get("parenteralIntake").get("Protein") != None and cuurentDeficitLast.get("enteralIntake").get("Protein") > 0 and cuurentDeficitLast.get("parenteralIntake").get("Protein") > 0:
      if feed != None and feed[1] != None and  "METHOD03" in feed[1]:
        diffProtein = 0;
        intakeProtein = cuurentDeficitLast.get("enteralIntake").get("Protein");
        recommendedProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
  
        if diffProtein < 0:
          isProteinCorrect = False;

      else:
        diffProtein = ((cuurentDeficitLast.get("enteralIntake").get("Protein") + cuurentDeficitLast.get("parenteralIntake").get("Protein")) / feed[2]) - cuurentDeficitLast.get("esphaganIntake").get("Protein");

        intakeProtein = (cuurentDeficitLast.get("enteralIntake").get("Protein") + cuurentDeficitLast.get("parenteralIntake").get("Protein")) / feed[2];
        recommendedProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
  
        if diffProtein < 0:
          isProteinCorrect = False;
       
      feedTypeProtein = "EN+PN";
    elif cuurentDeficitLast.get("enteralIntake") != None and cuurentDeficitLast.get("enteralIntake").get("Protein") != None and cuurentDeficitLast.get("enteralIntake").get("Protein") > 0:
      if feed != None and feed[1] != None and  "METHOD03" in feed[1]:
        diffProtein = 0;
        intakeProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
        recommendedProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
  
        if diffProtein < 0:
          isProteinCorrect = False;

      else:
        diffProtein = (cuurentDeficitLast.get("enteralIntake").get("Protein") / feed[2]) - cuurentDeficitLast.get("esphaganIntake").get("Protein");
        intakeProtein = cuurentDeficitLast.get("enteralIntake").get("Protein") / feed[2];
        recommendedProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
  
        if diffProtein < 0:
          isProteinCorrect = False;
      
      feedTypeProtein = "EN Only";
    elif cuurentDeficitLast.get("parenteralIntake") != None and cuurentDeficitLast.get("parenteralIntake").get("Protein") != None and cuurentDeficitLast.get("parenteralIntake").get("Protein") > 0:
      if feed != None and feed[1] != None and  "METHOD03" in feed[1]:
        diffProtein = 0;
        intakeProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
        recommendedProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
  
        if diffProtein < 0:
          isProteinCorrect = False;
       
      else:
        diffProtein = (cuurentDeficitLast.get("parenteralIntake").get("Protein") / feed[2])  - cuurentDeficitLast.get("esphaganIntake").get("Protein");
  
        intakeProtein = cuurentDeficitLast.get("parenteralIntake").get("Protein") / feed[2];
        recommendedProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
        if diffProtein < 0:
          isProteinCorrect = False;
      
      feedTypeProtein = "PN Only";
    else:
      if feed != None and feed[1] != None and  "METHOD03" in feed[1]:
        diffProtein = 0;
        intakeProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
        recommendedProtein = cuurentDeficitLast.get("esphaganIntake").get("Protein");
  
        if diffProtein < 0:
          isProteinCorrect = False;
        
        feedTypeProtein = "EN Only";
    
    
    cur1.execute("Select birthweight from apollo.baby_detail obj where uhid = '"  + uhid  + "' order by creationtime")
    babyDetailList = cur1.fetchall()
    diffHashMap = {}
    previousStay = stay;
    if intakeEnergy != -1:
      if days==0 and stay < 1:
        if ((intakeEnergy < (90*stay)) or (intakeEnergy > (120*stay)) and (diffEnergy != 0)):
          if ((intakeEnergy - (90*stay) > 0) or (intakeEnergy - (120*stay) > 0)):
            stay = 1; 
            recommendedEnergy = 105;


      energyMap[days][0] = intakeEnergy
      energyMap[days][1] = recommendedEnergy

      if (intakeEnergy < (90*stay)) or (intakeEnergy > (120*stay)) and (diffEnergy != 0):
        if intakeEnergy < 90*stay:
          energyMap[days][2] = 90*stay
          energyMap[days][3] = intakeEnergy - (90*stay)
        else:
          energyMap[days][2] = 120*stay
          energyMap[days][3] = intakeEnergy - (120*stay)
        
        energyMap[days][4] = "Deviation"
      else:
        energyMap[days][2] = intakeEnergy
        energyMap[days][3] = 0
        energyMap[days][4] = "No Error"
      
      percentageEnergy = (intakeEnergy / recommendedEnergy) * 100;
      diffHashMap["Energy"] = percentageEnergy;
      energyMap[days][5] = feedTypeEnergy

    if weight != -1:
      energyMap[days][6] = weight
    
    

    

    if intakeProtein != -1:
      if days==0:
        
        if babyDetailList[0][0] < 2500:
          if (intakeProtein < (3*stay)) or (intakeProtein > (4*stay)) and (diffProtein != 0):
            if ((intakeProtein - (3*stay) > 0) or (intakeProtein - (4*stay) > 0)):
              stay = 1; 
              recommendedProtein = float(3.5);
        else:
          if (intakeProtein < (2*stay)) or (intakeProtein > (2*stay)) and (diffProtein != 0):
            if ((intakeProtein - (2*stay) > 0) or (intakeProtein - (3*stay) > 0)):
              stay = 1; 
              recommendedProtein = float(2.5);

      proteinMap[days][0] = intakeProtein
      proteinMap[days][1] = recommendedProtein
      
  
      
      if babyDetailList[0][0] < 2500:
        if (intakeProtein < (3*stay)) or (intakeProtein > (4*stay)) and (diffProtein != 0):
          if intakeProtein < 3*stay:
            proteinMap[days][2] = 3*stay
            proteinMap[days][3] = intakeProtein - (3*stay)
          else:
            proteinMap[days][2] = 4*stay
            proteinMap[days][3] = intakeProtein - (4*stay)
          
          proteinMap[days][4] = "Deviation"
        else:
          proteinMap[days][2] = intakeProtein
          proteinMap[days][3] = 0
          proteinMap[days][4] = "No Error"
        
      else:
        if (intakeProtein < (2*stay)) or (intakeProtein > (3*stay)) and (diffProtein != 0):
          if intakeProtein < 2*stay:
            proteinMap[days][2] = 2*stay
            proteinMap[days][3] = intakeProtein - (2*stay)
          else:
            proteinMap[days][2] = 3*stay
            proteinMap[days][3] = intakeProtein - (3*stay)
          proteinMap[days][4] = "Deviation"
        else:
          proteinMap[days][2] = intakeProtein
          proteinMap[days][3] = 0
          proteinMap[days][4] = "No Error"
  
      percentageProtein = (intakeProtein / recommendedProtein) * 100;
      diffHashMap["Protein"] = percentageProtein;
      proteinMap[days][5] = feedTypeProtein


    if weight != -1:
      proteinMap[days][6] = weight
  
    
    diffHashMap["Parenteral"]= isRecommendationEnteral;
    diffHashMap["stay"] = stay;
        
    #Impute previous missed LOS
    for i in range(len(missedLos)):
      days = missedLos[i] - 1;

      if intakeEnergy != -1:
        energyMap[days][0] = intakeEnergy
        energyMap[days][1] = recommendedEnergy
     

        if (intakeEnergy < (90*stay)) or (intakeEnergy > (120*stay)) and (diffEnergy != 0):
          if intakeEnergy < 90*stay:
            energyMap[days][2] = 90*stay
            energyMap[days][3] = intakeEnergy - (90*stay)
          else:
            energyMap[days][2] = 120*stay
            energyMap[days][3] = intakeEnergy - (120*stay)
          
          energyMap[days][4] = "Deviation"
        else:
          energyMap[days][2] = intakeEnergy
          energyMap[days][3] = 0
          energyMap[days][4] = "No Error"

      if weight != -1:
        energyMap[days][6] = weight

      if intakeProtein != -1:
        proteinMap[days][0] = intakeProtein
        proteinMap[days][1] = recommendedProtein
        

        if babyDetailList[0][0] < 2500:
          if (intakeProtein < (3*stay)) or (intakeProtein > (4*stay)) and (diffProtein != 0):
            if intakeProtein < 3*stay:
              proteinMap[days][2] = 3*stay
              proteinMap[days][3] = intakeProtein - (3*stay)
            else:
              proteinMap[days][2] = 4*stay
              proteinMap[days][3] = intakeProtein - (4*stay)
            
            proteinMap[days][4] = "Deviation"
          else:
            proteinMap[days][2] = intakeProtein
            proteinMap[days][3] = 0
            proteinMap[days][4] = "No Error"
          
        else:
          if (intakeProtein < (2*stay)) or (intakeProtein > (3*stay)) and (diffProtein != 0):
            if intakeProtein < 2*stay:
              proteinMap[days][2] = 2*stay
              proteinMap[days][3] = intakeProtein - (2*stay)
            else:
              proteinMap[days][2] = 3*stay
              proteinMap[days][3] = intakeProtein - (3*stay)
            proteinMap[days][4] = "Deviation"
          else:
            proteinMap[days][2] = intakeProtein
            proteinMap[days][3] = 0
            proteinMap[days][4] = "No Error"
        

      if weight != -1:
        proteinMap[days][6] = weight

    
    if intakeEnergy != -1:
      missedLos = []
    

    return diffHashMap;


def getDeficitFeedCalculatorOrder(uhid, feedList, nutritionList,  currentWeight, fromDateOffsetTwentFourHour, toDateOffsetTwentFourHour, type, gestationWeek, lengthStay,cur1):

    isEntryAvailable = False
    
   
    #CaclulatorDeficitPOJO calculator = new CaclulatorDeficitPOJO();

    cur1.execute("select entry_timestamp,primary_feed_type,primary_feed_value,formula_type,formula_value from apollo.nursing_intake_output obj where uhid = '"  + uhid  + "' and entry_timestamp >= '"  + str(fromDateOffsetTwentFourHour)  +
        "' and entry_timestamp < '"  + str(toDateOffsetTwentFourHour)  + "' order by entry_timestamp asc, creationtime asc")
    oralFeedList = cur1.fetchall()

    cur1.execute("Select birthweight from apollo.baby_detail obj where uhid = '"  + uhid  + "' order by creationtime")
    babyDetailList = cur1.fetchall()

    currentTimeNurse = datetime.datetime.now()
    pastTimeNurse = datetime.datetime.now()
    counter = 1
    calculator = {}
    if len(oralFeedList) > 0:
        isEntryAvailable = True
        enteral = {}
        for oral in oralFeedList:
            currentTimeNurse = oral[0]
            isEntryValid = False;
            if counter == 1:
                isEntryValid = True;
                pastTimeNurse = oral[0]
            else:
                if currentTimeNurse.timestamp() - pastTimeNurse.timestamp() < 0:
                    yu = 1;
          
                if currentTimeNurse.timestamp() - pastTimeNurse.timestamp() > (10*60):
                    isEntryValid = True;
        
        
        if isEntryValid == True:
            counter = counter + 1;
            pastTimeNurse = oral[0]

            for nutrition in nutritionList:
  
                if oral[1] != None and oral[1] == nutrition[0] and oral[2] != None:
  
                    if enteral.get("Energy") != None:
                        enteral["Energy"] = enteral.get("Energy") + ((oral[2] * nutrition[1]) / 100);
                    else:
                        enteral["Energy"] = oral[2] * nutrition[1] / 100;

                    if enteral.get("Protein") != None:
                        enteral["Protein"] = enteral.get("Protein") +  ((oral[2] * nutrition[2]) / 100);
                    else:
                        enteral["Protein"] = oral[2] * nutrition[2] / 100;
                
                if oral[3] != None and oral[3] == nutrition[0] and oral[4] != None:
                
                    if enteral.get("Energy") != None:
                        enteral["Energy"] = enteral.get("Energy") + ((oral[4] * nutrition[1]) / 100);
                    else:
                        enteral["Energy"] = oral[4] * nutrition[1] / 100;
              

                    if enteral.get("Protein") != None:
                        enteral["Protein"] = enteral.get("Protein") +  ((oral[4] * nutrition[2]) / 100);
                    else:
                        enteral["Protein"] = oral[4] * nutrition[2] / 100;
            
        calculator["enteralIntake"] =enteral
    
    energyNurseIntake = 0
    proteinNurseIntake = 0

    if calculator.get("enteralIntake") != None and calculator.get("enteralIntake").get("Energy") != None and calculator.get("enteralIntake").get("Energy") >0:
        energyNurseIntake = calculator.get("enteralIntake").get("Energy");
    
    if calculator.get("enteralIntake") != None and calculator.get("enteralIntake").get("Protein") != None and calculator.get("enteralIntake").get("Protein") >0:
        proteinNurseIntake = calculator.get("enteralIntake").get("Protein");

   
    
    calculator = {}

    duration = (toDateOffsetTwentFourHour.timestamp() - fromDateOffsetTwentFourHour.timestamp()) / (60 * 60);
    
    stay = duration / 24;
    
    if stay >= 1:
        stay = 1;
    #11749
  
    cur1.execute("select no_of_feed,feed_volume from apollo.en_feed_detail where uhid ='" + uhid + "' and babyfeedid ='" +  str(feedList[5]) + "' order by creationtime asc")
    enFeedList = cur1.fetchall()

    feedType = "";
    if feedList[6] != None:
        feedTypeArr = feedList[6].replace("[", "").replace("]", "").split(",");
        feedType = feedTypeArr[0].strip();
    if feedList[7] != None:
        feedTypeArr = feedList[7].replace("[", "").replace("]", "").split(",");
        feedType = feedTypeArr[0].strip();
      
    if feedList[8] != None and len(enFeedList) == 0 and feedType != None and feedList[9] != None and feedList[9] == True:
        enFeedNew = {}
        enFeedNew["no_feed"] = 1
        enFeedNew["feed_volume"] = feedList[8]
        enFeedList.append(enFeedNew);
      
    dol = lengthStay;
        
    if len(enFeedList) > 0 and feedType != None:
        enteral = {}
        for oral in enFeedList:
            for nutrition in nutritionList:
                if feedType == nutrition[0]:
  
                    if oral[0] != None and oral[1] != None:

                        if enteral.get("Energy") != None:
                            enteral["Energy"] = enteral.get("Energy") + ((oral[0] * oral[1] * nutrition[1]) / 100);
                        else:
                            enteral["Energy"] = oral[0] * oral[1] * nutrition[1] / 100;

                        if enteral.get("Protein") != None:
                            enteral["Protein"] = enteral.get("Protein") +  ((oral[0] * oral[1] * nutrition[2]) / 100);
                        else:
                            enteral["Protein"] = oral[0] * oral[1] * nutrition[2] / 100;

        calculator["enteralIntake"] = enteral;
    elif len(enFeedList) == 0 and feedType != None:
      
        enteral = {}
        for nutrition in nutritionList:
  
            if feedType == nutrition[0]:
  
                if feedList[10] != None and feedList[11] != None and feedList[12] and feedList[12] != "Continuous" and feedList[10] != "0":
                    duration1 = feedList[10]
                    noOfFeeds = feedList[12] / duration1;

                    if enteral.get("Energy") != None:
                        enteral["Energy"] = enteral.get("Energy") + ((feedList[11] * noOfFeeds * nutrition[1]) / 100);
                    else:
                        enteral["Energy"] = feedList[11] * noOfFeeds * nutrition[1] / 100;

                    if enteral.get("Protein") != None:
                        enteral["Protein"] = enteral.get("Protein") +  ((feedList[11] * noOfFeeds * nutrition[2]) / 100);
                    else:
                        enteral["Protein"] = feedList[11] * noOfFeeds * nutrition[2] / 100;
        calculator["enteralIntake"] = enteral;

    
    
    if calculator.get("enteralIntake") != None and calculator.get("enteralIntake").get("Energy") and calculator.get("enteralIntake").get("Energy") >= 0 and energyNurseIntake > 0:
        if calculator.get("enteralIntake").get("Energy") < energyNurseIntake:
            calculator.get("enteralIntake")["Energy"] = energyNurseIntake
      
    elif calculator.get("enteralIntake") != None and calculator.get("enteralIntake").get("Energy") == None and energyNurseIntake > 0:
            calculator.get("enteralIntake")["Energy"] = energyNurseIntake

    if calculator.get("enteralIntake") != None and calculator.get("enteralIntake").get("Protein") and calculator.get("enteralIntake").get("Protein") >= 0 and proteinNurseIntake > 0:
        if calculator.get("enteralIntake").get("Protein") < proteinNurseIntake:
            calculator.get("enteralIntake")["Protein"] = proteinNurseIntake
      
    elif calculator.get("enteralIntake") != None and calculator.get("enteralIntake").get("Protein") == None and proteinNurseIntake > 0:
            calculator.get("enteralIntake")["Protein"] = proteinNurseIntake

    #parental....
    if type == "order":
        parental = {}
        if (feedList != None):
            FeedParental = feedList;
            if currentWeight != None:
                workingWeight = float(currentWeight)
                energyParenteral = None;
                if FeedParental[13] != None:
                    energyParenteral = FeedParental[13] * 4 * workingWeight;
                
                if FeedParental[13] != None:
                    parental["Protein"] = FeedParental[13] * workingWeight;
                    stay = 1;
                
                if FeedParental[14] != None:
                    if energyParenteral != None:
                        energyParenteral = energyParenteral  + FeedParental[14] * 10 * workingWeight;
                    else:
                        energyParenteral = FeedParental[14] * 10 * workingWeight;
                
  
                if FeedParental[0] != None and FeedParental[0].strip() != None:
                    stay = 1;
                    gir = float(FeedParental[0])
                    if gir > 20:
                        if FeedParental[15] != None and FeedParental[15] == False and FeedParental[16] != None and FeedParental[17] != None:
                            gir = float(0.007 * FeedParental[16] * FeedParental[17]);
                        elif FeedParental[15] != None and FeedParental[15] == False and FeedParental[18] != None:
                            if FeedParental[19] != None:
                                gir = float(0.007 * FeedParental[19] * FeedParental[18]);
                        
                            elif FeedParental[20] != None:
                                if "D10" in FeedParental[20]:
                                    gir = float(0.007 * FeedParental[18] * 10);
                                elif "D25" in FeedParental[20]:
                                    gir = float(0.007 * FeedParental[18] * 25);
                                elif "D50" in FeedParental[20]:
                                    gir = float(0.007 * FeedParental[18] * 50);
                                else:
                                    gir = float(0.007 * FeedParental[18] * 5);

                        
                
                    if energyParenteral != None:
                        energyParenteral = float(energyParenteral + gir * 4.9 * workingWeight);
                    else:
                        energyParenteral = float(gir * 4.9 * workingWeight);
                if FeedParental[21] != None and FeedParental[22] != None and "dextrose" in FeedParental[22]:
                    girBolus = float(0.007 * FeedParental[21] * 10);
                    if energyParenteral != None:
                        energyParenteral = float(energyParenteral + girBolus * 4.9 * workingWeight);
                    else:
                        energyParenteral = Float.valueOf(girBolus * 4.9 * workingWeight);
                
                parental["Energy"] = energyParenteral;
                calculator["parenteralIntake"] = parental;
    
    
    if len(babyDetailList) > 0:
        eshphaganIntake = {}
        if babyDetailList[0][0] < 2500:
            eshphaganIntake["Energy"] = float(105*stay);
            eshphaganIntake["Protein"] = float(3.5*stay);
   
        else:
            eshphaganIntake["Energy"] = float(105*stay);
            eshphaganIntake["Protein"] = float(2.5*stay);
        calculator["esphaganIntake"] = eshphaganIntake;    

    return calculator;


def location(request,branchname,from_date,to_date):

    
    con = psycopg2.connect (user = 'postgres',
            password = 'postgres',
            port = '5432',
            database = 'inicudb')

    cur = con.cursor()
    cur.execute("SELECT t1.uhid, t1.gender, t1.dateofadmission, t1.birthweight, t1.inout_patient_status, t1.gestationweekbylmp, t1.gestationdaysbylmp,t1.dischargeddate, t1.admissionweight, t1.baby_type, t1.branchname ,t2.isantenatalsteroidgiven, t2.mode_of_delivery,t3.jaundicestatus, t4.infection_system_status, t5.resp_system_status, t6.apgar_onemin, t6.apgar_fivemin FROM apollo.baby_detail AS t1 LEFT JOIN apollo.antenatal_history_detail AS t2 ON t1.uhid = t2.uhid  LEFT JOIN apollo.sa_jaundice AS t3 ON t1.uhid = t3.uhid LEFT JOIN apollo.sa_infection_sepsis AS t4 ON t1.uhid = t4.uhid LEFT JOIN apollo.sa_resp_rds AS t5 ON t1.uhid = t5.uhid LEFT JOIN apollo.birth_to_nicu AS t6 on t1.uhid = t6.uhid where t1.branchname ='"+branchname+"';")
    rows = cur.fetchall()
    baby_detail=pd.DataFrame(rows)
    baby_detail.rename(columns={0:'uhid',
                      1:'Gender',2:'admission_date',
                      3:'birthweight',4:'inout_patient_status',5:'gestation_week',6:'gestation_days',7:'discharge_date',8:'admissionweight',9:'baby_type',
                       10:'Location',11:'ANTENATA_STEROIDS',12:'MODE_OF_DELIVERY',13:'JAUNDICE',14:'SEPSIS',15:'RDS',16:'ONEMIN_APGAR',17:'FIVEMIN_APGAR'},
             inplace=True)
    baby_detail['discharge_date'] = pd.to_datetime(baby_detail['discharge_date'])
    baby_detail['admission_date'] = pd.to_datetime(baby_detail['admission_date'])
    def d(x):
        return x.days
    baby_detail['los'] = (baby_detail['discharge_date'] - baby_detail['admission_date'])
    baby_detail['los'] = baby_detail['los'].apply(d)
    def tf(x):
        if x == 'yes' or x=='Yes':
            return True
        else:
            return False
    baby_detail['JAUNDICE'] = baby_detail['JAUNDICE'].apply(tf)
    baby_detail['SEPSIS'] = baby_detail['SEPSIS'].apply(tf)
    baby_detail['RDS'] = baby_detail['RDS'].apply(tf)
    baby_detail.drop_duplicates('uhid',keep='last',inplace=True)
    baby_detail['Gestation'] = baby_detail['gestation_week'] + baby_detail['gestation_days']/7
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)
    baby_detail = baby_detail[(baby_detail['admission_date']>=from_date) & (baby_detail['admission_date']<=to_date)]




    data = load_data(baby_detail)
    cur.close()
    con.close()
    print("in view ")
    response_data = {}
    #prediction = predict('RSHI.0000014313')
    #prediction, lastHMTime = predict(uhid)
    #response_data['result'] = prediction
    #response_data['hmTime'] = lastHMTime
    response_data = data
    #return JSONResponse(response_data)
    return JsonResponse(data, safe=False)






class FetchData(APIView):
    def get(self,request):
        con = psycopg2.connect (user = 'postgres',
                password = 'postgres',
                port = '5432',
                database = 'inicudb')

        cur = con.cursor()
        cur.execute('SELECT t1.uhid, t1.gender, t1.dateofadmission, t1.birthweight, t1.inout_patient_status, t1.gestationweekbylmp, t1.gestationdaysbylmp,t1.dischargeddate, t1.admissionweight, t1.baby_type, t1.branchname ,t2.isantenatalsteroidgiven, t2.mode_of_delivery,t3.jaundicestatus, t4.infection_system_status, t5.resp_system_status, t6.apgar_onemin, t6.apgar_fivemin FROM apollo.baby_detail AS t1 LEFT JOIN apollo.antenatal_history_detail AS t2 ON t1.uhid = t2.uhid  LEFT JOIN apollo.sa_jaundice AS t3 ON t1.uhid = t3.uhid LEFT JOIN apollo.sa_infection_sepsis AS t4 ON t1.uhid = t4.uhid LEFT JOIN apollo.sa_resp_rds AS t5 ON t1.uhid = t5.uhid LEFT JOIN apollo.birth_to_nicu AS t6 on t1.uhid = t6.uhid;')
        rows = cur.fetchall()
        baby_detail=pd.DataFrame(rows)
        baby_detail.rename(columns={0:'uhid',
                          1:'Gender',2:'admission_date',
                          3:'birthweight',4:'inout_patient_status',5:'gestation_week',6:'gestation_days',7:'discharge_date',8:'admissionweight',9:'baby_type',
                           10:'Location',11:'ANTENATA_STEROIDS',12:'MODE_OF_DELIVERY',13:'JAUNDICE',14:'SEPSIS',15:'RDS',16:'ONEMIN_APGAR',17:'FIVEMIN_APGAR'},
                 inplace=True)
        baby_detail['discharge_date'] = pd.to_datetime(baby_detail['discharge_date'])
        baby_detail['admission_date'] = pd.to_datetime(baby_detail['admission_date'])
        def d(x):
            return x.days
        baby_detail['los'] = (baby_detail['discharge_date'] - baby_detail['admission_date'])
        baby_detail['los'] = baby_detail['los'].apply(d)
        def tf(x):
            if x == 'yes' or x=='Yes':
                return True
            else:
                return False
        baby_detail['JAUNDICE'] = baby_detail['JAUNDICE'].apply(tf)
        baby_detail['SEPSIS'] = baby_detail['SEPSIS'].apply(tf)
        baby_detail['RDS'] = baby_detail['RDS'].apply(tf)
        baby_detail.drop_duplicates('uhid',keep='last',inplace=True)
        baby_detail['Gestation'] = baby_detail['gestation_week'] + baby_detail['gestation_days']/7




        data = load_data(baby_detail)
        cur.close()
        con.close()
        print("in view ")
        response_data = {}
        #prediction = predict('RSHI.0000014313')
        #prediction, lastHMTime = predict(uhid)
        #response_data['result'] = prediction
        #response_data['hmTime'] = lastHMTime
        response_data = data
        #return JSONResponse(response_data)
        return JsonResponse(data, safe=False)


class TestData(APIView):
    def get(self,request):

        print("in view ")

        con = psycopg2.connect (user = 'postgres',
                password = 'postgres',
                port = '5432',
                database = 'inicudb')

        cur = con.cursor()
        response_data = {}

        def tf(x):
            if x == null:
                return False
        cur.execute("select gender,birthweight,episodeid,uhid,babyname,dateofbirth,timeofbirth,gestationweekbylmp,gestationdaysbylmp,dischargeddate,dateofadmission,timeofadmission,baby_type,inout_patient_status from apollo.baby_detail where dateofadmission >= '2019-08-15' and (dischargestatus = 'Discharge') and dischargeddate is not null and DATE_PART('day',dischargeddate - dateofadmission) > 1 and admissionstatus is False and dischargestatus is not null and branchname ILIKE '%MOTI%' and (isreadmitted is null or isreadmitted is False) and uhid NOT IN ('RSHI.0000014177','RSHI.0000012200') and uhid IN (select uhid from apollo.babyfeed_detail) and gestationweekbylmp >= 26 order by dateofadmission")
        #cur.execute("select distinct(b.uhid),b.dateofadmission,b.dateofbirth,b.dischargeddate,b.timeofadmission,b.gestationweekbylmp,b.gestationdaysbylmp,b.birthweight,b.gender,b.inout_patient_status,b.baby_type,b.timeofbirth,b.episodeid from  apollo.baby_detail as b where b.uhid IN  (select a.uhid from apollo.babyfeed_detail as a where (b.dischargestatus = 'Discharge') and b.dischargeddate is not null and DATE_PART('day',b.dischargeddate - b.dateofadmission) > 1 and b.admissionstatus is False and b.dischargestatus is not null and b.branchname ILIKE '%MOTI%' and b.dateofadmission >= '2019-08-15' and (b.isreadmitted is null or b.isreadmitted is False) and b.uhid NOT IN ('RSHI.0000014177','RSHI.0000012200')) order by b.dateofadmission")
        rows = cur.fetchall()
        i = -1

        baby_detail = [[0 for x in range(100)] for x in range(len(rows))]
        baby_detail_cat1 = []
        baby_detail_cat2 = []
        baby_detail_cat3 = []
        baby_detail_cat4 = []

        for baby in rows:
            print(baby)
            isValidDataPN = True;
            cur.execute("select girvalue from apollo.babyfeed_detail where uhid ='" + baby[3] + "' order by entrydatetime desc")
            feedListObjTemp = cur.fetchall()
            dod = baby[9];
            if feedListObjTemp[-1] is None:
                isValidDataPN = False;
            if isValidDataPN == True:
                if (baby[6] is not None):
                    tob = baby[6];
                    dateofbirth = baby[5];
                    toaArr = tob.split(",");
                    dateofbirth = datetime.datetime(dateofbirth.year, dateofbirth.month, dateofbirth.day, 0, 0, 0)

                    if (toaArr[2].find("PM")) and (toaArr[0].find("12")):
                        dateofbirth = dateofbirth.replace(hour=(int(toaArr[0]) + 12))
                    elif (toaArr[2].find("AM")) and (toaArr[0].find("12")):
                        dateofbirth = dateofbirth.replace(hour=0)
                    else:
                        dateofbirth = dateofbirth.replace(hour=int(toaArr[0]))
                    dateofbirth = dateofbirth.replace(minute=int(toaArr[1]))

                if (baby[11] is not None):
                    toa = baby[11];
                    dateofadmission = baby[10];


                    if toa != None and "," in toa:
                      toaArr = toa.split(",");
                      dateofadmission = datetime.datetime(dateofadmission.year, dateofadmission.month, dateofadmission.day, 0, 0, 0)
                      
                      if (toaArr[2].find("PM")) and (toaArr[0].find("12")):
                          dateofadmission = dateofadmission.replace(hour=(int(toaArr[0]) + 12))
                      elif (toaArr[2].find("AM")) and (toaArr[0].find("12")):
                          dateofadmission = dateofadmission.replace(hour=0)
                      else:
                          dateofadmission = dateofadmission.replace(hour=int(toaArr[0]))
                      dateofadmission = dateofadmission.replace(minute=int(toaArr[1]))
                      creationTime = dateofadmission
                    elif toa != None and ":" in toa:
                      toaArr = toa.split(":");

                      dateofadmission = datetime.datetime(dateofadmission.year, dateofadmission.month, dateofadmission.day, 0, 0, 0)
                      
                      if ("PM" in toa) and (toaArr[0].find("12")):
                          dateofadmission = dateofadmission.replace(hour=(int(toaArr[0]) + 12))
                      elif ("AM" in toa) and (toaArr[0].find("12")):
                          dateofadmission = dateofadmission.replace(hour=0)
                      else:
                          dateofadmission = dateofadmission.replace(hour=int(toaArr[0]))
                      dateofadmission = dateofadmission.replace(minute=0)
                      creationTime = dateofadmission

                i = i + 1
                #Name

                los = int((dod.timestamp() - creationTime.timestamp()) / (60 * 60 * 24));

                nextTime = creationTime
                isTodayEntry = False;
                if creationTime.hour >= 8:

                    nextTime += datetime.timedelta(days=1)
                    nextTime.replace(hour=8)
                    nextTime.replace(minute=0)
                else:
                    isTodayEntry = True;
                    nextTime = creationTime
                    nextTime.replace(hour=8)
                    nextTime.replace(minute=0)
                

                #Name
                baby_detail[i][0] = baby[4];
                #Uhid
                baby_detail[i][1] = baby[3];
                #LOS
                baby_detail[i][2] = los

                #Gestation
                baby_detail[i][3] = baby[7];
                baby_detail[i][4] = baby[8];

                baby_detail[i][54] = baby[7] + (baby[8] / 7);
                #Weight
                if baby[1] < 5:
                  baby_detail[i][5] = baby[1] * 1000;
                elif baby[1] >= 5 and baby[1] < 50:
                  baby_detail[i][5] = baby[1] * 10;
                else:
                  baby_detail[i][5] = baby[1];
                
                #DOB
                baby_detail[i][6] = baby[5];
                #Gender
                baby_detail[i][7] = baby[0]
                # if baby[0] == "Male":
                #   baby_detail[i][7] = 1
                # else:
                #   baby_detail[i][7] = 0
                #Baby Type
                baby_detail[i][8] = baby[12];
                if baby_detail[i][8] == "Twins" or baby_detail[i][8] == "Triplets":
                  baby_detail[i][56] = "Multiple"
                else:
                  baby_detail[i][56] = "Single"
                #Inborn/outborn
                baby_detail[i][9] = baby[13]

                cur.execute("select apgar_onemin,apgar_fivemin,resuscitation,resuscitation_o2,initial_step,resuscitation_ppv,resuscitation_chesttube_compression from apollo.birth_to_nicu where uhid = '" + baby[3] + "' and episodeid = '" + baby[2] + "' order by creationtime desc")
                birthToNicuList = cur.fetchall()

                if len(birthToNicuList) > 0:
                    for p in range(7):
                        baby_detail[i][p+10] = birthToNicuList[0][p];
                    # #One APGAR
                    # baby_detail[i][2] = birthToNicuList[0][0];
                    # #Five APGAR
                    # baby_detail[i][3] = birthToNicuList[0][1];
                    # #resuscitation
                    # baby_detail[i][4] = birthToNicuList[0][2]
                    # #resuscitation_o2
                    # baby_detail[i][5] = birthToNicuList[0][3]
                    # #initial_step
                    # baby_detail[i][6] = birthToNicuList[0][4]
                    # #resuscitation_ppv
                    # baby_detail[i][7] = birthToNicuList[0][5]
                    # #resuscitation_chesttube_compression
                    # baby_detail[i][8] = birthToNicuList[0][6]

                if baby_detail[i][10] == None and baby_detail[i][11] == None:
                  baby_detail[i][57] = "Not available"
                elif ( (baby_detail[i][10] != None and baby_detail[i][10] <= 5) or (baby_detail[i][11] != None and baby_detail[i][11] <= 5)):
                  baby_detail[i][57] = "Less than 5"
                elif ( (baby_detail[i][10] != None and baby_detail[i][10] > 5) or (baby_detail[i][11] != None and baby_detail[i][11] > 5)):
                  baby_detail[i][57] = "Greater than 5"


                if baby_detail[i][14] != None and baby_detail[i][14] == True:
                  baby_detail[i][61] = "Initial Steps"

                if baby_detail[i][13] != None and baby_detail[i][13] == True:
                  baby_detail[i][61] = "O2"

                if baby_detail[i][16] != None and baby_detail[i][16] == True:
                  baby_detail[i][61] = "Chest compression"

                if baby_detail[i][15] != None and baby_detail[i][15] == True:
                  baby_detail[i][61] = "PPV"

                if baby_detail[i][61] == None:
                  baby_detail[i][61] = False


                cur.execute("select isantenatalsteroidgiven,mode_of_delivery,hypertension,gestational_hypertension,diabetes,gdm,chronic_kidney_disease,hypothyroidism,hyperthyroidism,nonedisease,fever,uti,history_of_infections,noneinfection,prom,pprom,prematurity,chorioamniotis,oligohydraminos,polyhydraminos,noneother,umbilical_doppler,abnormal_umbilical_doppler_type from apollo.antenatal_history_detail where uhid = '" + baby[3] + "' and episodeid = '" + baby[2] + "' order by creationtime desc")
                antenatalSteroidsList = cur.fetchall()

                if len(antenatalSteroidsList) > 0:
                    for p in range(23):
                        baby_detail[i][p+17] = antenatalSteroidsList[0][p];

                if baby_detail[i][18] == "Vaccum" or baby_detail[i][18] == "Forceps" or baby_detail[i][18] == "NVD":
                  baby_detail[i][55] = "NVD"
                else:
                  baby_detail[i][55] = "LSCS"

                
                if baby_detail[i][19] == True or baby_detail[i][20] == True or baby_detail[i][21] == True or baby_detail[i][22] == True or baby_detail[i][23] == True or baby_detail[i][24] == True or baby_detail[i][25] == True: 
                  baby_detail[i][58] = True
                else:
                  baby_detail[i][58] = False

                if baby_detail[i][26] == True or baby_detail[i][27] == True or baby_detail[i][28] == True:
                  baby_detail[i][59] = True
                else:
                  baby_detail[i][59] = False

                if baby_detail[i][30] == True or baby_detail[i][31] == True or baby_detail[i][33] == True or baby_detail[i][34] == True or baby_detail[i][35] == True:
                  baby_detail[i][60] = True
                else:
                  baby_detail[i][60] = False


                cur.execute("select causeofrds from apollo.sa_resp_rds where uhid = '" + baby[3] + "' and episode_number = 1 and eventstatus = 'Yes' order by assessment_time asc")
                rdsList = cur.fetchall()
                isRds = False
                isRdsMAS = False
                isRdsTTNB = False

                if len(rdsList) > 0:
                    isRds = True;

                if isRds == True:
                    for rdsObj in rdsList:
                        if "RDS0001" in rdsObj:
                             isRdsTTNB = True;
                             isRds = False;
                        if "RDS0003" in rdsObj:
                             isRdsMAS = True;
                             isRds = False;

                    cur.execute("select cause_value from apollo.reason_admission where uhid = '" + baby[3] + "'")
                    reasonList = cur.fetchall()
                    for reasonObj in reasonList:
                        if "TTNB" in reasonObj:
                             isRdsTTNB = True;
                             isRds = False;
                        if "MAS" in reasonObj:
                             isRdsMAS = True;
                             isRds = False;
                baby_detail[i][41] = isRds;
                baby_detail[i][42] = isRdsMAS;
                baby_detail[i][43] = isRdsTTNB;

                cur.execute("select jaundicestatus from apollo.sa_jaundice where uhid = '" + baby[3] + "' and episode_number = 1 and jaundicestatus = 'Yes' and phototherapyvalue='Start' order by assessment_time asc")
                jaundiceList = cur.fetchall()
                isJaundice = False

                if len(jaundiceList) > 0:
                    isJaundice = True;
                baby_detail[i][44] = isJaundice;

                isSepsis = False
                isProbableSepsis = False

                cur.execute("select episodeid from apollo.sa_infection_sepsis where uhid = '" + baby[3] + "' and eventstatus = 'yes' and episode_number = 1 order by assessment_time asc")
                sepsisList = cur.fetchall()

                if len(sepsisList) > 0:
                    isSepsis = True;
                baby_detail[i][45] = isSepsis;

                if isSepsis == True:
                    cur.execute("select uhid from apollo.vw_antibiotic_duration where uhid = '" + baby[3] + "' and antibiotic_duration >= 5 and medicationtype = 'TYPE0001'")
                    sepsisProbableList = cur.fetchall()
                    if len(sepsisProbableList) > 0:
                        isProbableSepsis = True;
                baby_detail[i][46] = isProbableSepsis;

                isAsphyxia = False

                cur.execute("select uhid from apollo.sa_cns_asphyxia where uhid = '" + baby[3] + "' and eventstatus = 'yes' and episode_number = 1 order by assessment_time asc")
                asphyxiaList = cur.fetchall()
                if len(asphyxiaList) > 0:
                    isAsphyxia = True;
                baby_detail[i][47] = isAsphyxia;


                isPneumothorax = False

                cur.execute("select uhid from apollo.sa_resp_pneumothorax where uhid = '" + baby[3] + "' and eventstatus = 'Yes' and episode_number = 1 order by assessment_time asc")
                pneumoList = cur.fetchall()
                if len(pneumoList) > 0:
                    isPneumothorax = True;
                baby_detail[i][48] = isPneumothorax;

                isPPHN = False

                cur.execute("select uhid from apollo.sa_resp_pphn where uhid = '" + baby[3] + "' and eventstatus = 'Yes' and episode_number = 1  order by assessment_time asc")
                pphnList = cur.fetchall()
                if len(pphnList) > 0:
                    isPPHN = True;
                baby_detail[i][49] = isPPHN;

                isInvasive = False

                cur.execute("select rs_vent_type from apollo.respsupport where uhid = '" + baby[3] + "' order by creationtime")
                invasiveList = cur.fetchall()
                if len(invasiveList) > 0:
                    for invasiveObj in invasiveList:
                        if ("HFO" in invasiveObj) or ("Mechanical Ventilation" in invasiveObj):
                            isInvasive = True;
                baby_detail[i][50] = isInvasive;

                neofaxStatus = -1;
                isDoseCorrectGlobal = True;
                currentGestationWeek = baby[7];
                currentGestationDays = baby[8];
                #NEOFAX
                cur.execute("select startdate,route,medicinename,dose,freq_type,bolus,inf_time,inf_volume,frequency,dose_unit_time,dose_unit from apollo.baby_prescription where uhid = '" + baby[3] + "' and medicinename IS not null and dose is not null order by startdate asc")
                babyPrescriptionList = cur.fetchall()
                for medicine in babyPrescriptionList:
                    isDoseError = False;
                    medname = "";
                    dose = -1;
                    orderedDose = -1;
                    route = "";
                    mode = "";
                    startDate = medicine[0];
                    days = (startDate.timestamp() - dateofbirth.timestamp()) / (60 * 60 * 24);
                    bolus = False;

                   
                    route = medicine[1];
                    medname = medicine[2];
                    frequency = medicine[8];
                    dose = medicine[3];
                    orderedDose = dose;
                    mode = medicine[4];
                    bolus = medicine[5];
                    time = medicine[6];
                    volume = medicine[7];
                    currentGestationDays += days;
                    if currentGestationDays > 6:
                        currentGestationWeek = currentGestationWeek + (currentGestationDays / 7);
                        currentGestationDays = currentGestationDays % 7;
                    

                    cur.execute("select route,mode,bolus,lower_dose,upper_dose,dose_unit,perday from apollo.ref_medicine where isactive='True' and medname = '"
                    + medname + "' and upper_dol >= " + str(days) + " and lower_dol <= " + str(days) + " and upper_gestation >= "
                    + str(currentGestationWeek) + " and lower_gestation <= " + str(currentGestationWeek))
                    neofaxList = cur.fetchall()

                    if len(neofaxList) > 0:
                        neofaxStatus = 0;
                        lower_dose = -1;
                        upper_dose = -1;
                        unit = "";
                        isDoseCorrect = False;
                        bolusRec = False;
                        doseUnit = -1;

                        for refMedicine in neofaxList:
                            dose = orderedDose;

                            if refMedicine[0] is not None:
                                if refMedicine[0] == route:
                                    p = 1;
                                else:
                                    continue;

                            if refMedicine[1] is not None:
                                if refMedicine[1] == mode:
                                    p = 1;
                                else:
                                    continue;


                            if refMedicine[2] is not None:
                                if refMedicine[2] == bolus:
                                    p = 1;
                                else:
                                    continue;

                            if refMedicine[2] is not None:
                                bolusRec = refMedicine[2];

                            if refMedicine[3] is not None:
                                lower_dose = refMedicine[3];

                            if refMedicine[4] is not None:
                                upper_dose = refMedicine[4];

                            if refMedicine[5] is not None:
                                unit = refMedicine[5];

                            #Handling per day per dose
                            if dose is not None and frequency is not None and refMedicine[6] is not None and medicine[9] is not None:
                                cur.execute("select freqvalue from apollo.ref_medfrequency obj where freqid= '" + frequency  + "'")
                                refMedFreqList = cur.fetchall()


                                if len(refMedFreqList) > 0:
                                    lowerFreqTypeDummy = refMedFreqList[0][0];
                                    freqListDummy = lowerFreqTypeDummy.split(" hr");
                                    lowerFreqValueDummy = int(freqListDummy[0]);
                                    value = 24 / lowerFreqValueDummy;
                                    if ("per dose" in refMedicine[6]) and ("day" in medicine[9]):
                                        dose = dose / value;
                                    elif ("per day" in refMedicine[6]) and ("dose" in medicine[9]):
                                        dose = dose * value;
                            isMedGiven = True;

                            if upper_dose != -1:
                                if refMedicine[6] is not None and medicine[10] is not None:
                                    if ("mg/kg" in refMedicine[6]) and ("mg/kg" in medicine[10]):
                                        lower_limit = lower_dose - ((10 * lower_dose) / 100);
                                        upper_limit = upper_dose + ((10 * upper_dose) / 100);
                                        if dose >= lower_limit and dose <= upper_limit:
                                            isDoseCorrect = True;
                                    elif ("μg/kg" in refMedicine[6]) and ("mg/kg" in medicine[10]):
                                        dose = dose*1000;
                                        lower_limit = lower_dose - ((10 * lower_dose) / 100);
                                        upper_limit = upper_dose + ((10 * upper_dose) / 100);
                                        if dose >= lower_limit and dose <= upper_limit:
                                            isDoseCorrect = True;
                                    elif ("mg/kg" in refMedicine[6]) and ("μg/kg" in medicine[10]):
                                        dose = dose/1000;
                                        lower_limit = lower_dose - ((10 * lower_dose) / 100);
                                        upper_limit = upper_dose + ((10 * upper_dose) / 100);
                                        if dose >= lower_limit and dose <= upper_limit:
                                            isDoseCorrect = True;
                                    else:
                                        lower_limit = lower_dose - ((10 * lower_dose) / 100);
                                        upper_limit = upper_dose + ((10 * upper_dose) / 100);
                                        if dose >= lower_limit and dose <= upper_limit:
                                            isDoseCorrect = True;
                                else:
                                    lower_limit = lower_dose - ((10 * lower_dose) / 100);
                                    upper_limit = upper_dose + ((10 * upper_dose) / 100);
                                    if dose >= lower_limit and dose <= upper_limit:
                                        isDoseCorrect = True;
                            else:
                                lower_limit = lower_dose - ((10 * lower_dose) / 100);
                                upper_limit = lower_dose + ((10 * lower_dose) / 100);
                                if dose >= lower_limit and dose <= upper_limit:
                                    isDoseCorrect = True;
                        if (isDoseError == False) and (isDoseCorrectGlobal == True):
                            isDoseCorrectGlobal = False;

                if isDoseCorrectGlobal == False:
                    neofaxStatus = 1
                baby_detail[i][51] = neofaxStatus;

                if neofaxStatus == 1:
                  baby_detail[i][66] = "Deviation"
                elif neofaxStatus == -1:
                  baby_detail[i][66] = "Med not given"
                elif neofaxStatus == 0:
                  baby_detail[i][66] = "No deviation"



                firstLoop = False;
                isNutritionOrdered = False;
                
                lastFeed = {}
                #HashMap<String, Float> lastDiff = new HashMap<String, Float>();
                cuurentDeficitLastLatest = {}

                counter = 1;
                lengthOfStay = 0;
                gotFirstOrder = False;
                missedLos = [];
                energyMap = [[0 for x in range(7)] for x in range(100)]
                proteinMap = [[0 for x in range(7)] for x in range(100)]


                while creationTime.timestamp() < dod.timestamp() and lengthOfStay < los:
                    lengthOfStay = lengthOfStay + 1
                    cuurentDeficitLast = {}
                    startingTime = creationTime
                    endingTime = nextTime

                    cur.execute("select girvalue,feedmethod,working_weight,entrydatetime,creationtime,babyfeedid, feedtype, feedTypeSecondary, totalenteralvolume, isenternalgiven, feedduration,feedvolume,duration,aminoacid_conc, lipid_conc, isReadymadeSolutionGiven, dextroseVolumemlperday, current_dextrose_concentration, readymadeFluidVolume, readymadeDextroseConcentration, readymadeFluidType, bolusVolume, bolusType  from apollo.babyfeed_detail where uhid ='" + baby[3] + "' and entrydatetime >= '" + str(startingTime) + "' and  entrydatetime <= '" + str(endingTime) + "' order by entrydatetime desc")
                    feedListObj = cur.fetchall()
                    isPNAndBreastMilkGiven = False;
                    if len(feedListObj) > 0:
                        feed = feedListObj[0];
                        if feed != None and feed[1] != None and "METHOD03" in feed[1] and feed[0] != None:
                            isPNAndBreastMilkGiven = True;
                        if feed != None and feed[1] != None and "METHOD03" in feed[1]:
                            isPNAndBreastMilkGiven = True;
                    
                    if isPNAndBreastMilkGiven == False:
                        if len(feedListObj) > 0:
                            feed = feedListObj[0];
                            gotFirstOrder = True;
                            cur.execute("select feedtype_id,energy,protein from apollo.ref_nutritioncalculator")
                            nutritionList = cur.fetchall()
                 
                            cuurentDeficitLast = getDeficitFeedCalculatorOrder(baby[3], feed, nutritionList, str(feed[2]), creationTime,nextTime,"order",currentGestationWeek,lengthOfStay,cur);
                            if feed[3] != None :
                                lastDiff = computeError(feed[3],cuurentDeficitLast,feed,baby[3],dateofadmission,currentGestationWeek,currentGestationDays,energyMap,proteinMap,lengthOfStay, creationTime,nextTime,missedLos,cur)
                            else:
                                lastDiff = computeError(feed[4],cuurentDeficitLast,feed,baby[3],dateofadmission,currentGestationWeek,currentGestationDays,energyMap,proteinMap,lengthOfStay, creationTime,nextTime,missedLos,cur)
                            lastFeed = feed;
                            cuurentDeficitLastLatest = cuurentDeficitLast;
                            if lastDiff.get("Energy") != None:
                                isNutritionOrdered = True;
                                missedLos = []
                            else:
                                missedLos.append(lengthOfStay)
                
  
                            counter = 1;
 
                        elif isNutritionOrdered == True:
                            cur.execute("select feedtype_id,energy,protein from apollo.ref_nutritioncalculator")
                            nutritionList = cur.fetchall()
                            cuurentDeficitLastNew = getDeficitFeedCalculatorOrder(baby[3], lastFeed, nutritionList, str(feed[2]), creationTime,nextTime,"order",currentGestationWeek,lengthOfStay,cur);
  
                            if lastFeed[3] != None:
                                creationTimeDummy = lastFeed[3]
                                creationTimeDummy += datetime.timedelta(days=counter)
                                newTime = creationTimeDummy
                                computeErrorLast(newTime,cuurentDeficitLastNew,lastFeed,baby[3],dateofadmission,currentGestationWeek,currentGestationDays,energyMap,proteinMap,lengthOfStay,lastDiff,cur);
                            
                            else:
                                creationTimeDummy = lastFeed[4]
                                creationTimeDummy += datetime.timedelta(days=counter)
                                newTime = creationTimeDummy
                                computeErrorLast(newTime,cuurentDeficitLastNew,lastFeed,baby[3],dateofadmission,currentGestationWeek,currentGestationDays,energyMap,proteinMap,lengthOfStay,lastDiff,cur); 
                            
                            counter = counter + 1;
                        else:
                            missedLos.append(lengthOfStay);
                        
                    
                    if firstLoop == False:
                        creationTime.replace(hour=8)
                        creationTime.replace(minute=0)
                        nextTime.replace(hour=8)
                        nextTime.replace(minute=0)
                    
                    if firstLoop == False:
                        if isTodayEntry == True:
                            creationTime = creationTime
                        else:
                            creationTime += datetime.timedelta(days=1)

                    else:
                        creationTime += datetime.timedelta(days=1)
                    nextTimeDummy = creationTime
                    firstLoop = True;
                    nextTimeDummy += datetime.timedelta(days=1)
                    nextTime = nextTimeDummy

                if creationTime.timestamp() < dod.timestamp() and lengthOfStay >= los:
                    cuurentDeficitLast = {}
                    startingTime = creationTime
                    endingTime = nextTime
                    cur.execute("select girvalue,feedmethod,working_weight,entrydatetime,creationtime,babyfeedid, feedtype, feedTypeSecondary, totalenteralvolume, isenternalgiven, feedduration,feedvolume,duration,aminoacid_conc, lipid_conc, isReadymadeSolutionGiven, dextroseVolumemlperday, current_dextrose_concentration, readymadeFluidVolume, readymadeDextroseConcentration, readymadeFluidType, bolusVolume, bolusType  from apollo.babyfeed_detail where uhid ='" + baby[3] + "' and entrydatetime >= '" + str(startingTime) + "' and  entrydatetime <= '" + str(endingTime) + "' order by entrydatetime desc")
                    feedListObj = cur.fetchall()
                    isPNAndBreastMilkGiven = False;
                    if len(feedListObj) > 0:
                        feed = feedListObj[0];
                        if feed != None and feed[1] != None and "METHOD03" in feed[1] and feed[0] != None:
                            isPNAndBreastMilkGiven = True;
                        if feed != None and feed[1] != None and "METHOD03" in feed[1]:
                            isPNAndBreastMilkGiven = True;
                    
                    if len(feedListObj) > 0 and isPNAndBreastMilkGiven == False:
                        for feed in feedListObj:
                            gotFirstOrder = True;
                            cur.execute("select feedtype_id,energy,protein from apollo.ref_nutritioncalculator")
                            nutritionList = cur.fetchall()
                            cuurentDeficitLast = getDeficitFeedCalculatorOrder(baby[3], feed, nutritionList, str(feed[2]), creationTime,nextTime,"order",currentGestationWeek,lengthOfStay,cur);
                            if feed[3] != None:
                                lastDiff = computeError(feed[3],cuurentDeficitLast,feed,baby[3],dateofadmission,currentGestationWeek,currentGestationDays,energyMap,proteinMap,lengthOfStay, creationTime,nextTime,missedLos,cur);
                            else:
                                lastDiff = computeError(feed[4],cuurentDeficitLast,feed,baby[3],dateofadmission,currentGestationWeek,currentGestationDays,energyMap,proteinMap,lengthOfStay, creationTime,nextTime,missedLos,cur);  
                            lastFeed = feed
                            cuurentDeficitLastLatest = cuurentDeficitLast
                            isNutritionOrdered = True
                            counter = 1
                            missedLos = []

                baby_detail[i][52] = energyMap;
                baby_detail[i][53] = proteinMap;

                num = 0
                for energyList in energyMap:
                  given_value = energyList[0]
                  recommend_value = energyList[1]
                  dummy = recommend_value - given_value
                  dummy = dummy * dummy
                  num = num + dummy

                baby_detail[i][62] = sqrt(num)

                num = 0
                for proteinList in proteinMap:
                  given_value = proteinList[0]
                  recommend_value = proteinList[1]
                  dummy = recommend_value - given_value
                  dummy = dummy * dummy
                  num = num + dummy
                baby_detail[i][63] = sqrt(num)

                

                if baby_detail[i][54] < 32:
                  baby_detail_cat1.append(baby_detail[i])

                elif baby_detail[i][54] >= 32 and baby_detail[i][54] <= 34:
                  baby_detail_cat2.append(baby_detail[i])

                elif baby_detail[i][54] > 34 and baby_detail[i][54] <= 37:
                  baby_detail_cat3.append(baby_detail[i])

                elif baby_detail[i][54] > 37:
                  baby_detail_cat4.append(baby_detail[i])

        #list_indices = [2,7,56,9,57,61,55,58,59,60,41,42,43,44,46,47,48,49,50,66,62,63,54]
        list_indices = [2,7,56,9,57,55,58,59,60,41,42,43,44,46,47,48,49,50,66,62,63,54]

        new_indices = []
        for i in range(100):
          if i in list_indices:
            p = 1
          else:
            new_indices.append(i)
        baby_detail_cat1 = np.delete(baby_detail_cat1,new_indices,1)
        baby_detail_cat2 = np.delete(baby_detail_cat2,new_indices,1)
        baby_detail_cat3 = np.delete(baby_detail_cat3,new_indices,1)
        baby_detail_cat4 = np.delete(baby_detail_cat4,new_indices,1)

        #col_names = ["LOS","Gender","Inborn/Outborn","RDS","MAS","TTNB","Jaundice","Sepsis","Asphyxia","Pneumothorax","PPHN","Invasive Support","Gestation","Mode of Delievery","Pregnancy Type","APGAR","Maternal Diseases","Maternal Infections","Maternal Risk Factors","Resusciation","Energy_Deviation","Protein_Deviation","Medication Deviation"]
        col_names = ["LOS","Gender","Inborn/Outborn","RDS","MAS","TTNB","Jaundice","Sepsis","Asphyxia","Pneumothorax","PPHN","Invasive Support","Gestation","Mode of Delievery","Pregnancy Type","APGAR","Maternal Diseases","Maternal Infections","Maternal Risk Factors","Energy_Deviation","Protein_Deviation","Medication Deviation"]

        df_cat1 = pd.DataFrame(baby_detail_cat1, columns=col_names)
        print(df_cat1.LOS)

        thirdQuartileEnergy = np.percentile(df_cat1.Energy_Deviation, [75])
        thirdQuartileProtein = np.percentile(df_cat1.Protein_Deviation, [75])
        thirdQuartileGestation = np.percentile(df_cat1.Gestation, [75])

        df_cat1.Energy_Deviation = [True if x >= thirdQuartileEnergy else False for x in df_cat1.Energy_Deviation]
        df_cat1.Protein_Deviation = [True if x >= thirdQuartileProtein else False for x in df_cat1.Protein_Deviation]
        df_cat1["Gestation_Final"] = [True if x >= thirdQuartileGestation else False for x in df_cat1.Gestation]

        df_cat2 = pd.DataFrame(baby_detail_cat2, columns=col_names)
        thirdQuartileEnergy = np.percentile(df_cat2.Energy_Deviation, [75])
        thirdQuartileProtein = np.percentile(df_cat2.Protein_Deviation, [75])
        thirdQuartileGestation = np.percentile(df_cat2.Gestation, [75])

        df_cat2.Energy_Deviation = [1 if x >= thirdQuartileEnergy else 0 for x in df_cat2.Energy_Deviation]
        df_cat2.Protein_Deviation = [1 if x >= thirdQuartileProtein else 0 for x in df_cat2.Protein_Deviation]
        df_cat2.Gestation = [1 if x >= thirdQuartileGestation else 0 for x in df_cat2.Gestation]

        df_cat3 = pd.DataFrame(baby_detail_cat3, columns=col_names)
        thirdQuartileEnergy = np.percentile(df_cat3.Energy_Deviation, [75])
        thirdQuartileProtein = np.percentile(df_cat3.Protein_Deviation, [75])
        thirdQuartileGestation = np.percentile(df_cat3.Gestation, [75])

        df_cat3.Energy_Deviation = [1 if x >= thirdQuartileEnergy else 0 for x in df_cat3.Energy_Deviation]
        df_cat3.Protein_Deviation = [1 if x >= thirdQuartileProtein else 0 for x in df_cat3.Protein_Deviation]
        df_cat3.Gestation = [1 if x >= thirdQuartileGestation else 0 for x in df_cat3.Gestation]

        df_cat4 = pd.DataFrame(baby_detail_cat4, columns=col_names)
        thirdQuartileEnergy = np.percentile(df_cat4.Energy_Deviation, [75])
        thirdQuartileProtein = np.percentile(df_cat4.Protein_Deviation, [75])
        thirdQuartileGestation = np.percentile(df_cat4.Gestation, [75])

        df_cat4.Energy_Deviation = [1 if x >= thirdQuartileEnergy else 0 for x in df_cat4.Energy_Deviation]
        df_cat4.Protein_Deviation = [1 if x >= thirdQuartileProtein else 0 for x in df_cat4.Protein_Deviation]
        df_cat4.Gestation = [1 if x >= thirdQuartileGestation else 0 for x in df_cat4.Gestation]

        print(df_cat1)

        def get_dum(x):
          for elem in df_cat1[x].unique():
              df_cat1[str(elem)] = df_cat1[x] == elem

        def conv(x):
          if x == True:
              return 1
          else:
              return 0


        def model(data):
          y = []
          for i in data.LOS:
            y.append(np.log(i))
          y = np.array(y)
          X = data.drop('LOS',axis=1)
          NegBi_model = sm.OLS(y.astype(float), X.astype(float))
          NegBi_results = NegBi_model.fit()

          results_as_html = NegBi_results.summary().tables[1].as_html()
          dt = pd.read_html(results_as_html, header=0, index_col=0)[0]

          return (NegBi_results.params, dt)

        def refgrid(x):

          Inborn_Outborn = [x[1],x[2]]
          Gestation = [x[0]]
          Energy_Deviation = [x[3],x[4]]
          Protein_Deviation = [x[5],x[6]]
          Maternal_Diseases = [x[7],x[8]]
          Maternal_Infections = [x[9],x[10]]
          Maternal_Risk_Factors = [x[11],x[12]]
          RDS = [x[13],x[14]]
          Jaundice = [x[15],x[16]]
          Sepsis = [x[17],x[18]]
          Mode_of_Delievery = [x[19],x[20]]
          Pregnancy_Type = [x[21],x[22]]
          Gender = [x[23],x[24]]
          Gestation_Final = [x[25],x[26]]
          APGAR = [x[27],x[28],x[29]]
          TTNB = [x[30],x[31]]
          Invasive_Support = [x[32],x[33]]
          Pneumothorax = [x[34],x[35]]
          Medication = [x[36],x[37]]

          los_combo = list(itertools.product(Inborn_Outborn,Gender,Energy_Deviation,Protein_Deviation,Maternal_Diseases,Maternal_Infections,Maternal_Risk_Factors,RDS,Jaundice,Sepsis,Mode_of_Delievery,Pregnancy_Type,Gestation,Gestation_Final,APGAR,TTNB,Invasive_Support,Pneumothorax,Medication))
          los_df = pd.DataFrame(los_combo)
          los_df = los_df.rename(columns={0: "Inborn_Outborn", 1:"Gender",2:"Energy_Deviation",3:"Protein_Deviation", 4:"Maternal_Diseases",5:"Maternal_Infections",6:"Maternal_Risk_Factors",7 : "RDS", 8:"Jaundice", 9:"Sepsis",10:"Mode_of_Delievery",11:"Pregnancy_Type",12:"Gestation",13:"Gestation_Final",14:"APGAR",15:"TTNB",16:"Invasive_Support",17:"Pneumothorax",18:"Medication"})
          return los_df
        
        def choiceless_than32(x):
          print(x,"variable")
          z, m = model(qs)
    
          d = []
          e = []
          a = refgrid(z)
          q ={"Inborn_Outborn":1,"Energy_Deviation":3,"Protein_Deviation":5, "Maternal_Diseases":7,"Maternal_Infections":9,"Maternal_Risk_Factors":11, "RDS":13, "Jaundice":15, "Sepsis":17, "Mode_of_Delievery":19,"Pregnancy_Type":21,"Gender":23,"Gestation_Final":25,"APGAR":27,"MAS":30,"Invasive_Support":32,"Pneumothorax":34,"Medication":36}
          #q = {18: "Male",19: "Female", 0: "Inborn_Outborn", 1 : "RDS", 2: "MAS", 3:"TTNB", 4:"Jaundice", 5:"Sepsis", 6:"Asphyxia", 7:"Pneumothorax",8:"PPHN",9:"Invasive_Support",10:"Gestation",11:"Mode_of_Delievery",12:"Pregnancy_Type",13:"Maternal_Diseases",14:"Maternal_Infections",15:"Maternal_Risk_Factors",16:"Energy_Deviation",17:"Protein_Deviation"}
        
          #q ={"inout":1, "NF":3, "Med_admin":5, "espghan":7, "nutri":9, "gender":11, "rds":13, "jaundice":15, "sepsis":17, "lscs_nvd":19, "birth_type":21,"ant_std":23}
          p = q[x]
          
          los = a
          los_new = a.drop(str(x),axis=1)
          los_1 = los_new.drop('Gestation',axis=1)
          los_1['sum'] = los_new.sum(axis=1)

          # print(m)
          # print(los_new)
          # print(los_1)
          # print(los)
          print("55555%)(*&((&*())")

          if x == "APGAR":
            print("3333333333333")
            if m['P>|t|'][p] < .05 and m['P>|t|'][p+1] < .05 and m['P>|t|'][p+2] < .05:
              print("first APGAR")
              for j in range(len(los_new)):
                  for i in np.arange(25.0,32.0,0.1):

                      d.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[0])
                      e.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[196608])
                      f.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[393215])

              print("tttttt")
              s = pd.DataFrame(d)
              t = pd.DataFrame(e)
              u = pd.DataFrame(f)

        
        
              return(round(np.exp(s.mean())[0]-qs.median()[1]),round(np.exp(t.mean())[0]-qs.median()[1]),round(np.exp(u.mean())[0]-qs.median()[1]))
            elif m['P>|t|'][p] < .05 and m['P>|t|'][p+1] > .05 and m['P>|t|'][p+2] > .05:
                print("second APGAR")
                for j in range(len(los_new)):
                    for i in np.arange(25.0,32.0,0.1):
                        d.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[0])
                        e.append(0)
                        f.append(0)
                s = pd.DataFrame(d)
                t = pd.DataFrame(e) 
                u = pd.DataFrame(f)
                
                return(round(np.exp(s.mean())[0]-qs.median()[1]),' ', ' ')
            elif m['P>|t|'][p] > .05 and m['P>|t|'][p+1] < .05 and m['P>|t|'][p+1] < .05:
                print("third APGAR")
                for j in range(len(los_new)):
                    for i in np.arange(25.0,32.0,0.1):
                        d.append(0)
                        e.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[196608])
                        f.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[393215])

                s = pd.DataFrame(d)
                t = pd.DataFrame(e) 
                u = pd.DataFrame(f)

                
                return(' ',round(np.exp(t.mean())[0]-qs.median()[1]),round(np.exp(u.mean())[0]-qs.median()[1]))
            
            elif m['P>|t|'][p] > .05 and m['P>|t|'][p+1] > .05 and m['P>|t|'][p+1] < .05:
                print("fourth APGAR")
                for j in range(len(los_new)):
                    for i in np.arange(25.0,32.0,0.1):
                        d.append(0)
                        e.append(0)
                        f.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[393215])

                s = pd.DataFrame(d)
                t = pd.DataFrame(e) 
                u = pd.DataFrame(f)

                
                return(' ',' ',round(np.exp(u.mean())[0]-qs.median()[1]))

            elif m['P>|t|'][p] < .05 and m['P>|t|'][p+1] > .05 and m['P>|t|'][p+1] < .05:
                print("fifth APGAR")
                for j in range(len(los_new)):
                    for i in np.arange(25.0,32.0,0.1):
                        d.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[0])
                        e.append(0)
                        f.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[393215])

                s = pd.DataFrame(d)
                t = pd.DataFrame(e) 
                u = pd.DataFrame(f)

                
                return(round(np.exp(s.mean())[0]-qs.median()[1]),' ',round(np.exp(u.mean())[0]-qs.median()[1]))
             
            elif m['P>|t|'][p] < .05 and m['P>|t|'][p+1] < .05 and m['P>|t|'][p+1] > .05:
              print("sixth APGAR")
              for j in range(len(los_new)):
                  for i in np.arange(25.0,32.0,0.1):
                      d.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[0])
                      e.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[196608])
                      f.append(0)

              s = pd.DataFrame(d)
              t = pd.DataFrame(e) 
              u = pd.DataFrame(f)

              return(round(np.exp(s.mean())[0]-qs.median()[1]),round(np.exp(t.mean())[0]-qs.median()[1]),' ')

            elif m['P>|t|'][p] > .05 and m['P>|t|'][p+1] < .05 and m['P>|t|'][p+1] > .05:
              print("seventh APGAR")
              for j in range(len(los_new)):
                  for i in np.arange(25.0,32.0,0.1):
                      d.append(0)
                      e.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[196608])
                      f.append(0)

              s = pd.DataFrame(d)
              t = pd.DataFrame(e) 
              u = pd.DataFrame(f)
              
              return(' ',round(np.exp(t.mean())[0]-qs.median()[1]),' ')
          
            else:
                print("eighth APGAR")
                return (' ', ' ',' ')
          else:

            if m['P>|t|'][p] < .05 and m['P>|t|'][p+1] < .05:
              print("first if")
              for j in range(len(los_new)):
                  for i in np.arange(25.0,32.0,0.1):

                      d.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[0])
                      e.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[4095])

              print("tttttt")
              s = pd.DataFrame(d)
              t = pd.DataFrame(e)

        
        
              return(round(np.exp(s.mean())[0]-qs.median()[1]),round(np.exp(t.mean())[0]-qs.median()[1]))
            elif m['P>|t|'][p] < .05 and m['P>|t|'][p+1] > .05:
                print("second if")
                for j in range(len(los_new)):
                    for i in np.arange(25.0,32.0,0.1):
                        d.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[0])
                        e.append(0)
                s = pd.DataFrame(d)
                t = pd.DataFrame(e) 
                
                return(round(np.exp(s.mean())[0]-qs.median()[1]),' ')
            elif m['P>|t|'][p] > .05 and m['P>|t|'][p+1] < .05:
                print("third if")
                for j in range(len(los_new)):
                    for i in np.arange(25.0,32.0,0.1):
                        e.append(los_1['sum'].iloc[j] + (los_new['Gestation'].iloc[j])*i + los[x].iloc[4095])
                        d.append(0)
                s = pd.DataFrame(d)
                t = pd.DataFrame(e) 
                
                return(' ',round(np.exp(t.mean())[0]-qs.median()[1]))
                
            else:
                print("fourth if")
                return (' ', ' ')

        def get_dum(x):
          for elem in qs[x].unique():
              qs[str(elem)] = qs[x] == elem



        qs = df_cat1[['Gender','Mode of Delievery','Inborn/Outborn','Gestation','LOS',"Energy_Deviation","Protein_Deviation",'RDS',
       'Jaundice', 'Sepsis','Pregnancy Type','Maternal Diseases',"Maternal Infections","Maternal Risk Factors","Gestation_Final","APGAR","MAS","TTNB","PPHN","Invasive Support","Pneumothorax","Asphyxia","Medication Deviation"]]
        print(qs)
        get_dum('Inborn/Outborn')
        #Deleting the Original column after the dummy variables were created
        qs.drop('Inborn/Outborn',axis=1,inplace=True)
       

        # get_dum('Gestation')
        # qs = qs.rename(columns={"False": "Gestation False", "True": "Gestation True"})

        get_dum('Energy_Deviation')
        qs = qs.rename(columns={"False": "Energy_Deviation False", "True": "Energy_Deviation True"})

        get_dum('Protein_Deviation')
        qs = qs.rename(columns={"False": "Protein_Deviation False", "True": "Protein_Deviation True"})

        get_dum('Maternal Diseases')
        qs = qs.rename(columns={"False": "Maternal Diseases False", "True": "Maternal Diseases True"})

        get_dum('Maternal Infections')
        qs = qs.rename(columns={"False": "Maternal Infections False", "True": "Maternal Infections True"})

        get_dum('Maternal Risk Factors')
        qs = qs.rename(columns={"False": "Maternal Risk Factors False", "True": "Maternal Risk Factors True"})


        get_dum('RDS')
        qs = qs.rename(columns={"False": "RDS False", "True": "RDS True"})
        get_dum('Jaundice')
        qs = qs.rename(columns={"False": "Jaundice False", "True": "Jaundice True"})
        get_dum('Sepsis')
        qs = qs.rename(columns={"False": "Sepsis False", "True": "Sepsis True"})
        get_dum('Mode of Delievery')
        get_dum('Pregnancy Type')
        get_dum('Gender')
        get_dum('Gestation_Final')
        qs = qs.rename(columns={"False": "Gestation Remaining False", "True": "Gestation Highest True"})

        get_dum('APGAR')
        qs = qs.rename(columns={"Not available": "Not available APGAR", "Less than 5": "Less than 5 APGAR", "Greater than 5": "Greater than 5 APGAR"})


        # get_dum('MAS')
        # qs = qs.rename(columns={"False": "MAS False", "True": "MAS True"})
        get_dum('TTNB')
        qs = qs.rename(columns={"False": "TTNB False", "True": "TTNB True"})
        # get_dum('PPHN')
        # qs = qs.rename(columns={"False": "PPHN False", "True": "PPHN True"})

        get_dum('Invasive Support')
        qs = qs.rename(columns={"False": "Invasive Support False", "True": "Invasive Support True"})
        get_dum('Pneumothorax')
        qs = qs.rename(columns={"False": "Pneumothorax False", "True": "Pneumothorax True"})
        # get_dum('Asphyxia')
        # qs = qs.rename(columns={"False": "Asphyxia False", "True": "Asphyxia True"})





        get_dum('Medication Deviation')
        qs = qs.rename(columns={"Deviation": "Med Deviation", "Med not given": "Med not given"})

        qs.drop('Mode of Delievery',axis=1,inplace=True)
        qs.drop('Pregnancy Type',axis=1,inplace=True)
        #qs.drop('nan',axis=1,inplace=True)
        qs.drop('RDS',axis=1,inplace=True)

        qs.drop('MAS',axis=1,inplace=True)
        qs.drop('TTNB',axis=1,inplace=True)
        qs.drop('PPHN',axis=1,inplace=True)
        qs.drop('Invasive Support',axis=1,inplace=True)
        qs.drop('Pneumothorax',axis=1,inplace=True)
        qs.drop('Asphyxia',axis=1,inplace=True)

        qs.drop('Jaundice',axis=1,inplace=True)
        qs.drop('Sepsis',axis=1,inplace=True)
        qs.drop('Energy_Deviation',axis=1,inplace=True)
        qs.drop('Protein_Deviation',axis=1,inplace=True)
        qs.drop('Maternal Diseases',axis=1,inplace=True)
        qs.drop('Maternal Infections',axis=1,inplace=True)
        qs.drop('Maternal Risk Factors',axis=1,inplace=True)

        qs.drop('Gender',axis=1,inplace=True)
        qs.drop('Gestation_Final',axis=1,inplace=True)
        qs.drop('APGAR',axis=1,inplace=True)
        qs.drop('Medication Deviation',axis=1,inplace=True)

        print(qs)

        l = ['In Born', 'Out Born','Male', 'Female',
             'Energy_Deviation False', 'Energy_Deviation True',
             'Protein_Deviation False', 'Protein_Deviation True', 'Maternal Diseases False',
             'Maternal Diseases True','Maternal Infections False','Maternal Infections True','Maternal Risk Factors False','Maternal Risk Factors True' , 'RDS False', 'RDS True',
             'Jaundice False', 'Jaundice True', 'Sepsis False', 'Sepsis True',
             'LSCS', 'NVD', 'Single', 'Multiple','Gestation Remaining False','Gestation Highest True','Not available APGAR','Less than 5 APGAR','Greater than 5 APGAR',
             'TTNB False','TTNB True','Invasive Support False','Invasive Support True','Pneumothorax False','Pneumothorax True','Med Deviation','Med not given']

        for i in l:
          qs[i] = qs[i].apply(conv)
          print(i,qs[i])
        thirdQuartileEnergy = np.percentile(qs.LOS, [75])
        print(thirdQuartileEnergy)
        firstQuartileEnergy = np.percentile(qs.LOS, [25])
        print(firstQuartileEnergy)

       

       
        print("result_2")
        final_json = {}
        less_than_32_weeks = {}
        less_than_32_weeks["Count"] = str(len(qs))
        cur.execute("update apollo.predict_los set total_count = '" + less_than_32_weeks["Count"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Median"] = str(qs.median()[1])
        cur.execute("update apollo.predict_los set median = '" + less_than_32_weeks["Median"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["IQR"] = str(thirdQuartileEnergy-firstQuartileEnergy)
        cur.execute("update apollo.predict_los set iqr = '" + less_than_32_weeks["IQR"] + "'  where gest_catid ='1' ")
        con.commit()
        # less_than_32_weeks["Gestation 4th Quartile"] = str(choiceless_than32('Gestation_Final')[1])
        # cur.execute("update apollo.predict_los set gestation_fourth_quartile_riskfactor = '" + less_than_32_weeks["Gestation 4th Quartile"] + "'  where gest_catid ='1' ")
        # con.commit()
        # less_than_32_weeks["Gestation Rem Quartile"] = str(choiceless_than32('Gestation_Final')[0])
        # cur.execute("update apollo.predict_los set gestation_rem_quartile_riskfactor = '" + less_than_32_weeks["Gestation Rem Quartile"] + "'  where gest_catid ='1' ")
        # con.commit()
        # less_than_32_weeks["Gender Male"] = str(choiceless_than32('Gender')[0])
        # cur.execute("update apollo.predict_los set gender_male_riskfactor = '" + less_than_32_weeks["Gender Male"] + "'  where gest_catid ='1' ")
        # con.commit()
        less_than_32_weeks["Gender Female"] = str(choiceless_than32('Gender')[1])
        cur.execute("update apollo.predict_los set gender_female_riskfactor = '" + less_than_32_weeks["Gender Female"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Single Pregnancy"] = str(choiceless_than32('Pregnancy_Type')[0])
        cur.execute("update apollo.predict_los set single_pregnancy_riskfactor = '" + less_than_32_weeks["Single Pregnancy"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Multiple Pregnancy"] = str(choiceless_than32('Pregnancy_Type')[1])
        cur.execute("update apollo.predict_los set multiple_pregnancy_riskfactor = '" + less_than_32_weeks["Multiple Pregnancy"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["In Born"] = str(choiceless_than32('Inborn_Outborn')[0])
        cur.execute("update apollo.predict_los set inborn_riskfactor = '" + less_than_32_weeks["In Born"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Out Born"] = str(choiceless_than32('Inborn_Outborn')[1])
        cur.execute("update apollo.predict_los set out_born_riskfactor = '" + less_than_32_weeks["Out Born"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Greater than 5"] = str(choiceless_than32('APGAR')[2])
        cur.execute("update apollo.predict_los set apgar_greater_than_five_riskfactor = '" + less_than_32_weeks["Greater than 5"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Less than 5"] = str(choiceless_than32('APGAR')[1])
        cur.execute("update apollo.predict_los set apgar_less_than_five_riskfactor = '" + less_than_32_weeks["Less than 5"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Not Available"] = str(choiceless_than32('APGAR')[0])
        cur.execute("update apollo.predict_los set apgar_not_available_riskfactor = '" + less_than_32_weeks["Not Available"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["PPV"] = "0"
        cur.execute("update apollo.predict_los set ppv_riskfactor = '" + less_than_32_weeks["PPV"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["NVD"] = str(choiceless_than32('Mode_of_Delievery')[1])
        cur.execute("update apollo.predict_los set nvd_riskfactor = '" + less_than_32_weeks["NVD"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["LSCS"] = str(choiceless_than32('Mode_of_Delievery')[0])
        cur.execute("update apollo.predict_los set lscs_riskfactor = '" + less_than_32_weeks["LSCS"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Maternal Diseases True"] = str(choiceless_than32('Maternal_Diseases')[1])
        cur.execute("update apollo.predict_los set maternal_diseases_true_riskfactor = '" + less_than_32_weeks["Maternal Diseases True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Maternal Diseases False"] = str(choiceless_than32('Maternal_Diseases')[0])
        cur.execute("update apollo.predict_los set maternal_diseases_false_riskfactor = '" + less_than_32_weeks["Maternal Diseases False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Maternal Infections True"] = str(choiceless_than32('Maternal_Infections')[1])
        cur.execute("update apollo.predict_los set maternal_infections_true_riskfactor = '" + less_than_32_weeks["Maternal Infections True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Maternal Infections False"] = str(choiceless_than32('Maternal_Infections')[0])
        cur.execute("update apollo.predict_los set maternal_infections_false_riskfactor = '" + less_than_32_weeks["Maternal Infections False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Maternal Risk Factors True"] = str(choiceless_than32('Maternal_Risk_Factors')[1])
        cur.execute("update apollo.predict_los set maternal_risk_factors_true_riskfactor = '" + less_than_32_weeks["Maternal Risk Factors True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Maternal Risk Factors False"] = str(choiceless_than32('Maternal_Risk_Factors')[0])
        cur.execute("update apollo.predict_los set maternal_risk_factors_false_riskfactor = '" + less_than_32_weeks["Maternal Risk Factors False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["RDS True"] = str(choiceless_than32('RDS')[1])
        cur.execute("update apollo.predict_los set rds_true_riskfactor = '" + less_than_32_weeks["RDS True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["RDS False"] = str(choiceless_than32('RDS')[0])
        cur.execute("update apollo.predict_los set rds_false_riskfactor = '" + less_than_32_weeks["RDS False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["MAS True"] = "0"
        cur.execute("update apollo.predict_los set mas_true_riskfactor = '" + less_than_32_weeks["MAS True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["MAS False"] = "0"
        cur.execute("update apollo.predict_los set mas_false_riskfactor = '" + less_than_32_weeks["MAS False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["TTNB True"] = str(choiceless_than32('TTNB')[1])
        cur.execute("update apollo.predict_los set ttnb_true_riskfactor = '" + less_than_32_weeks["TTNB True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["TTNB False"] = str(choiceless_than32('TTNB')[0])
        cur.execute("update apollo.predict_los set ttnb_false_riskfactor = '" + less_than_32_weeks["TTNB False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Jaundice True"] = str(choiceless_than32('Jaundice')[1])
        cur.execute("update apollo.predict_los set jaundice_true_riskfactor = '" + less_than_32_weeks["Jaundice True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Jaundice False"] = str(choiceless_than32('Jaundice')[0])
        cur.execute("update apollo.predict_los set jaundice_false_riskfactor = '" + less_than_32_weeks["Jaundice False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Sepsis True"] = str(choiceless_than32('Sepsis')[1])
        cur.execute("update apollo.predict_los set sepsis_true_riskfactor = '" + less_than_32_weeks["Sepsis True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Sepsis False"] = str(choiceless_than32('Sepsis')[0])
        cur.execute("update apollo.predict_los set sepsis_false_riskfactor = '" + less_than_32_weeks["Sepsis False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Asphyxia True"] = "0"
        cur.execute("update apollo.predict_los set asphyxia_true_riskfactor = '" + less_than_32_weeks["Asphyxia True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Asphyxia False"] = "0"
        cur.execute("update apollo.predict_los set asphyxia_false_riskfactor = '" + less_than_32_weeks["Asphyxia False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["PPHN True"] = "0"
        cur.execute("update apollo.predict_los set pphn_true_riskfactor = '" + less_than_32_weeks["PPHN True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["PPHN False"] = "0"
        cur.execute("update apollo.predict_los set pphn_false_riskfactor = '" + less_than_32_weeks["PPHN False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Pneumothorax True"] = str(choiceless_than32('Pneumothorax')[1])
        cur.execute("update apollo.predict_los set pneumothorax_true_riskfactor = '" + less_than_32_weeks["Pneumothorax True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Pneumothorax False"] = str(choiceless_than32('Pneumothorax')[0])
        cur.execute("update apollo.predict_los set pneumothorax_false_riskfactor = '" + less_than_32_weeks["Pneumothorax False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Invasive Support True"] = str(choiceless_than32('Invasive Support')[1])
        cur.execute("update apollo.predict_los set invasive_true_riskfactor = '" + less_than_32_weeks["Invasive Support True"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Invasive Support False"] = str(choiceless_than32('Invasive Support')[0])
        cur.execute("update apollo.predict_los set invasive_false_riskfactor = '" + less_than_32_weeks["Invasive Support False"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Medicine Not Required"] = str(choiceless_than32('Medication')[1])
        cur.execute("update apollo.predict_los set medicine_not_required_riskfactor = '" + less_than_32_weeks["Medicine Not Required"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Deviation"] = str(choiceless_than32('Medication')[0])
        cur.execute("update apollo.predict_los set deviation_riskfactor = '" + less_than_32_weeks["Deviation"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["No Deviation"] = "0"
        cur.execute("update apollo.predict_los set no_deviation_riskfactor = '" + less_than_32_weeks["No Deviation"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Energy 4th Quartile"] = str(choiceless_than32('Energy_Deviation')[1])
        cur.execute("update apollo.predict_los set energy_fourth_quartile_riskfactor = '" + less_than_32_weeks["Energy 4th Quartile"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Energy Rem Quartile"] = str(choiceless_than32('Energy_Deviation')[0])
        cur.execute("update apollo.predict_los set energy_rem_quartile_riskfactor = '" + less_than_32_weeks["Energy Rem Quartile"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Protein 4th Quartile"] = str(choiceless_than32('Protein_Deviation')[1])
        cur.execute("update apollo.predict_los set protein_fourth_quartile_riskfactor = '" + less_than_32_weeks["Protein 4th Quartile"] + "'  where gest_catid ='1' ")
        con.commit()
        less_than_32_weeks["Protein Rem Quartile"] = str(choiceless_than32('Protein_Deviation')[0])
        cur.execute("update apollo.predict_los set protein_rem_quartile_riskfactor = '" + less_than_32_weeks["Protein Rem Quartile"] + "'  where gest_catid ='1' ")
        con.commit()
        final_json["Less than 32"] = less_than_32_weeks;
        final_json["32 to 34"] = less_than_32_weeks;
        final_json["34 to 37"] = less_than_32_weeks;
        final_json["Greater than 37"] = less_than_32_weeks;
        print(final_json)


       



          


        return JsonResponse(final_json, safe=False)
