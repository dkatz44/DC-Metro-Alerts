# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 20:40:49 2017

@author: dkatz44
"""

import os
import requests
import pandas as pd
import time as tm
from datetime import datetime, time
now = datetime.now()
now_time = now.time()

# 30 second sleep to make sure internet is connected
#tm.sleep(30)

# Run from start until 4:00PM
#while now_time <= time(16,00):

northOfCrystalCity = [
'C01',
'C02',
'C03',
'C04',
'C05',
'C06',
'C07',
'C08',
'D01',
'D02',
'D03',
'D04',
'D05',
'D08',
'G01',
'G02',
'G03',
'G04',
'G05',
'A01', 
'F03']

southOfRosslyn = [
'C06',
'C07',
'C08',
'C09',
'C10',
'C12',
'C13',
'D06',
'D07',
'J02',
'J03']

eastOfCourtHouse = [
'C01',
'C02',
'C03',
'C04',
'C05',
'D01',
'D02',
'D03',
'D04',
'D05',
'D06',
'D07',
'D08',
'D09',
'D10',
'D11',
'D12',
'D13',
'G01',
'G02',
'G03',
'G04',
'G05']

westOfRosslyn = [
'K01',
'K02',
'K03',
'K04',
'K05',
'K06',
'K07',
'K08',
'N01',
'N02',
'N03',
'N04',
'N06']


while now_time <= time(8,40) or (now_time >= time(16,35) and now_time <= time(17,30)):
    
    headers = {
        # Request headers
        'api_key': 'c0fc1d5bb8844776a7a9c68195193c10',
    }
    
    params = 'K01, C09, C05'
    
    
    query = "https://api.wmata.com/StationPrediction.svc/json/GetPrediction/" + params
    
    try:
        resp = requests.get(query, headers=headers)
        
    except requests.exceptions.ConnectionError as e:
        pass
    
    combinedData = pd.io.json.json_normalize(resp.json(), 'Trains')
    
    combinedData = combinedData[(combinedData['Line'] != 'YL') & (combinedData['Line'] != 'No')]
    
    combinedData['LocationName'] = combinedData['LocationName'].replace('Court House', 'CH')
    combinedData['LocationName'] = combinedData['LocationName'].replace('Crystal City', 'CC')
    combinedData['LocationName'] = combinedData['LocationName'].replace('Rosslyn', 'RS')
    
    if now_time <= time(8,40):
        combinedData = combinedData[
            ((combinedData['LocationName'] == 'CH') & (combinedData['DestinationCode'].isin(eastOfCourtHouse) == True)) |
            ((combinedData['LocationName'] == 'RS') & (combinedData['DestinationCode'].isin(southOfRosslyn) == True))]
    
    else:
        combinedData = combinedData[
            ((combinedData['LocationName'] == 'CC') & (combinedData['DestinationCode'].isin(northOfCrystalCity) == True)) |
            ((combinedData['LocationName'] == 'RS') & (combinedData['DestinationCode'].isin(westOfRosslyn) == True))]
    
    #combinedData.query("(LocationName == 'CH') & (Destination in ['Largo', 'NewCrltn', 'Rosslyn'])")
    
    combinedData = combinedData.drop(['DestinationCode', 'Group', 'DestinationName', 'LocationCode'], axis=1)
    
    combinedData['Min'] = combinedData['Min'].replace('','XX')
    combinedData['Min'] = combinedData['Min'].replace('BRD','-1')
    combinedData['Min'] = combinedData['Min'].replace('ARR','0')
    combinedData['Min'] = combinedData['Min'].replace('---', 'XX')
    combinedData['Line'] = combinedData['Line'].replace('--', 'XX')
    
    combinedData['Min'] = combinedData['Min'].map(lambda x: int(x) if x not in ['XX', 'ARR', 'BRD'] else x)
        
    # Sort by LocationName and Min
    combinedData = combinedData.sort_values(['LocationName', 'Min'], ascending=[True, True])
    
    # Reset the index with the new sorted order
    combinedData = combinedData.reset_index(drop=True)
    
    combinedData['Min'] = combinedData['Min'].replace(-1,'BD')
    combinedData['Min'] = combinedData['Min'].replace(0,'AR')
    
    combinedData['Min'] = combinedData['Min'].map(lambda x: '0' + str(x) if len(str(x)) == 1 else str(x))
    
    combinedData['combined'] = \
          combinedData['Min'].map(lambda x: x + ' ' if '1' in x else x) + \
          ' ' + combinedData['Line'].map(str) + \
          ' ' + combinedData['LocationName'].map(str) + \
          '->' + combinedData['Destination'].map(str) + \
          ' ' + combinedData['Car'].map(str) + \
          '\n'
         
    trainList = combinedData['combined'].tolist()
    
    trainList.insert(0, 'MN LN LOC DEST CAR \n')
    
    # Create the text message
    
    # Add the top 15 trains
    formattedTrainList = ''
    
    for x in range(len(trainList)): 
        if x <= 15:
            formattedTrainList += trainList[x]
        else: 
                break
    
    text = '"' + formattedTrainList + '"'
    
    # Insert the text into an AppleScript command (don't send blank texts)
    if len(trainList) > 0:
        cmd = "osascript<<END\n"
        cmd = cmd + """tell application "Messages" \n"""
        cmd = cmd + "activate --steal focus \n"
        cmd = cmd + "send " + text
        cmd = cmd + """ to buddy "dkatz44@gmail.com" of (service 1 whose service type is iMessage) \n"""
        cmd = cmd + "end tell\n" 
        cmd = cmd + "END"
    
    # Embed the command in a function
    def send_text():
        os.system(cmd)
    
    # Send the text!
    send_text()
        
        
# Sleep for 1 minute
    tm.sleep(60)
    
# Update the time variable
    now = datetime.now()
    now_time = now.time()
    print("Loop starting:", now_time)
#    print(now.time())
#    break

cmd = "osascript<<END\n"
cmd = cmd + """tell application "Messages" \n"""
cmd = cmd + "quit\n"
cmd = cmd + "end tell\n" 
cmd = cmd + "END"    

def quit_msgs():
    os.system(cmd)

quit_msgs()
print("Program Ended")

