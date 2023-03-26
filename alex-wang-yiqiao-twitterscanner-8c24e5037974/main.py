#!/usr/bin/env python
# coding: utf-8

# In[10]:


import json
import ijson
import re
import datetime
import pandas as pd

class TwitterScanner:
    def __init__ (self, twitterFile, salFile):     
        # Read sal.json
        salDict = json.load(open(salFile))
        greatCity = ['1gsyd','2gmel','3gbri','4gade','5gper','6ghob','7gdar','8acte','9oter']
        for key in list(salDict):
            if salDict[key]['gcc'] not in greatCity: salDict.pop(key)
        # Assume twitter json file does not fit in memory
        # Parse the file iteratively using ijson
        twitterColumns = ['twitterId', 'authorId', 'place', 'gcc']
        twitterObjects = ijson.items(open(twitterFile, 'r', encoding = 'utf-8'), 'item')
        twitterList = []
        for item in twitterObjects:
            rowTemp = []
            rowTemp.append(item['_id'])
            rowTemp.append(item['data']['author_id'])
            rowTemp.append(item['includes']['places'][0]['full_name'])
            # Attach gcc to twitter data
            for key in salDict:
                if (re.search(key, rowTemp[2], re.IGNORECASE) is not None):
                    rowTemp.append(salDict[key]['gcc'])
                    twitterList.append(rowTemp)
                    break # Exit the iteration once a match location found
        self.twitterData = pd.DataFrame(twitterList, columns = twitterColumns)
        
    def getTwitterData (self):
        return self.twitterData
    
    def pivotCity (self):
        tempList = []
        tempList.append(['1gsyd', '1gsyd(Greater Sydney)'])
        tempList.append(['2gmel', '2gmel(Greater Melbourne)'])
        tempList.append(['3gbri', '3gbri(Greater Brisbane)'])
        tempList.append(['4gade', '4gade(Greater Adelaide)'])
        tempList.append(['5gper', '5gper(Greater Perth)'])
        tempList.append(['6ghob', '6ghob(Greater Hobart)'])
        tempList.append(['7gdar', '7gdar(Greater Darwin)'])
        tempList.append(['8acte', '8acte(Australian Capital Territory)'])
        tempList.append(['9oter', '9oter(Other Territories)'])
        tempTable = pd.DataFrame(tempList, columns = ['gcc', 'Greater Capital City'])
        tempTable = tempTable.set_index('gcc')
        
        pivot = pd.pivot_table(self.twitterData, index = ['gcc'], values = ['twitterId'], aggfunc = 'count')
        pivotCity = pd.concat([tempTable, pivot], axis = 1)
        pivotCity['twitterId'] = pivotCity['twitterId'].fillna(0)
        pivotCity['twitterId'] = pivotCity['twitterId'].astype(int)
        pivotCity = pivotCity.reset_index(drop = True)
        pivotCity.rename(columns = {'twitterId':'Number of Tweets Made'}, inplace = True)
        return pivotCity
    
    def pivotUser (self):
        pivot = pd.pivot_table(self.twitterData, index = ['authorId'], values = ['twitterId'], aggfunc = 'count')
        pivot = pivot.sort_values(by = ['twitterId'], ascending = False)
        pivotUser = pivot.head(10)
        pivotUser = pivotUser.reset_index(drop = False)
        rank = ['#1','#2','#3','#4','#5','#6','#7','#8','#9','#10']
        pivotUser.insert(0, "Rank", rank)
        pivotUser.rename(columns = {'authorId':'Author Id', 'twitterId':'Number of Tweets Made'}, inplace = True)
        return pivotUser
    
    def pivotUserCity (self):
        pivotCity = pd.pivot_table(self.twitterData, values='twitterId', index='authorId', columns='gcc', aggfunc = pd.Series.nunique)
        pivotCity = pivotCity.fillna(0)
        pivotCity = pivotCity[pivotCity.columns].astype(int)
        pivotCity = pd.concat([pivotCity,pd.DataFrame(pivotCity.sum(axis=1),columns=['total'])],axis=1)
        
        pivotGcc = pd.pivot_table(self.twitterData, values='gcc', index='authorId', aggfunc = pd.Series.nunique)
        pivot = pd.concat([pivotCity, pivotGcc], axis = 1)
        pivot.sort_values(by=['gcc','total'], inplace=True, ascending = [False, False])
        
        pivotUserCity = pivot.head(10)
        recordList = pivotUserCity.values.tolist()
        columnList = pivotUserCity.columns.tolist()
        
        textList = []
        for record in recordList:
            textTemp = ''
            for i in range(len(columnList) - 2):
                if record[i] != 0: textTemp = textTemp + str(record[i]) + columnList[i][1:] + ', '
            textTemp = textTemp[:len(textTemp) - 2]
            text = str(record[-1]) + '(#' + str(record[-2]) + ' tweets - ' + textTemp + ')'
            textList.append(text)
            
        pivotUserCity = pivotUserCity.reset_index(drop = False)
        rank = ['#1','#2','#3','#4','#5','#6','#7','#8','#9','#10']
        pivotUserCity.insert(0, "Rank", rank)
        pivotUserCity.insert(2, "Number of Unique City Locations and #Tweets", textList)
        pivotUserCity = pivotUserCity.iloc[:, 0:3]
        pivotUserCity.rename(columns = {'authorId':'Author Id'}, inplace = True)
        return pivotUserCity

a = datetime.datetime.now()
x = TwitterScanner("twitter-data-small.json", "sal.json")
gcc = x.getTwitterData ()
print(str(gcc))
users = x.pivotCity()
print(str(users))
userCity = x.pivotUserCity ()
print (str(userCity))
b = datetime.datetime.now()
print(str(b-a))