import pickle

import httplib2

from retrievalmodels.SystemVariables import database
from collections import OrderedDict


h= httplib2.Http('.cache')
response, content =h.request('http://fiji4.ccs.neu.edu/~zerg/lemurcgi/lemur.cgi?d=?')
contentString = content.decode('utf-8')
databaseProperties = contentString[contentString.find(str(database)+':'):].split(';')[:5]
print(databaseProperties)
documentMappingFile = open('doclist.txt','r')
documentMappingDict=dict()
for documentMapping in documentMappingFile:
    dm=documentMapping.split()
    documentMappingDict[int(dm[0])]= dm[1].strip()

queryFileName="desc.51-100.short"
stopWordFileName= "stoplist.txt"
h= httplib2.Http('.cache')
ave_doclen=int(databaseProperties[4].split('=')[1].strip())
unique_terms=int(databaseProperties[3].split('=')[1].strip())
total_terms = int(databaseProperties[2].split('=')[1].strip())
total_documents=int(databaseProperties[1].split('=')[1].strip())

def readFiles():
#     print("in func readFiles")
    queries=OrderedDict()
    stopWords=[]
    # read stop words
    try:
        stopWordObjFile= open('objects/stopWordObjFile','rb')
        stopWords=pickle.load(stopWordObjFile)
    except IOError:
        print('from file')
        stopWordFile=open(stopWordFileName,'r')
        for sw in stopWordFile:
            sw=sw.strip()
            if(sw==''):
                continue
            stopWords.append(sw)
        stopWordObjFile= open('objects/stopWordObjFile','wb')
        pickle.dump(stopWords,stopWordObjFile,None)
        
    # read queries from file or object
    try:
        queryObjFile =open('objects/queryObjFile', 'rb')
        queries=pickle.load(queryObjFile)        
    except IOError:
        print('from file')
        queryFile= open(queryFileName,"r")
        for query in queryFile:
            query=query.strip()
            if(query==''):
                continue
            ql=query.split('.',1)
            queryId= int(ql[0])
            queryString=ql[1]
            queryString=queryString.strip().rstrip('.').lower()
            queryString=queryTokenize(queryString,stopWords)
            queries[queryId]=queryString
        
        queryObjFile= open('objects/queryObjFile', 'wb')
        pickle.dump(queries, queryObjFile, None)
    return queries

def queryTokenize(queryString,stopWords):
    # the below 4 query string modifications were done 
    # for better precision results. Please see Table: 3 in
    # project report.
    queryString=queryString.replace("document",'')
    queryString=queryString.replace("will",'')
    queryString=queryString.replace("d'etat",'')
    queryString=queryString.replace('u.s.','america')
    queryString=queryString.replace('"','')
    queryString=queryString.replace(',','')
    queryString=queryString.replace('-',' ')
    queryString=queryString.replace("'",'')
    
    queryString=queryString.replace('(', '')
    queryString=queryString.replace(')','')
    query_terms= queryString.split()
# start remove for no stopping   
    for sw in stopWords:
        if sw in query_terms:
#             print(sw)
            while query_terms.count(sw):
                query_terms.remove(sw)
#     query_terms.remove(query_terms[0])
    queryString=' '.join(query_terms)
# end remove for no stopping
    return queryString;


def queryLenAndProcessing(queries):
    queryLen={}
    for query in queries:
        queryTermFreqMap={}
        queryId=query
        queryString=queries[queryId]
        for term in queryString.split():
            if term in queryTermFreqMap:
                queryTermFreqMap[term]=queryTermFreqMap[term]+1
            else:
                queryTermFreqMap[term]=1
        queryLen[queryId]=len(queryString.split())
        queries[queryId]=queryTermFreqMap
    ave_querylen=calculateAveQueryLen(queryLen)
    return queries,queryLen, ave_querylen
  
def calculateAveQueryLen(queryLen):
    sumQueryLen=0
    for ql in queryLen:
        sumQueryLen+=queryLen[ql]
    
    return float(sumQueryLen/len(queryLen))