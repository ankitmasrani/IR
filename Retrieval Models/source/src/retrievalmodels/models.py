'''
Created on Oct 26, 2013

@author: Ankit
'''




from collections import OrderedDict
import math
import pickle

from retrievalmodels import ave_doclen, unique_terms, documentMappingDict, h, \
    queryLenAndProcessing, readFiles, total_documents, total_terms
from retrievalmodels.retrievalclasses import DocumentForTerm
from retrievalmodels.SystemVariables import database


collectionTermStats={}
queries=OrderedDict()
queryLen=dict()
ave_querylen=0
queryTermDocStats= {}
db=str(database)

def initialize():
    global queryTermDocStats,queries,collectionTermStats
    try:
        queryTermDocStatsFile= open('objects/queryTermDocStats','rb')
        queryTermDocStats=pickle.load(queryTermDocStatsFile)
    except IOError:
        queryTermDocStatsFile= open('objects/queryTermDocStats','wb')
        for query in queries:
            queryTermStats= getDocStatsForQuery(queries[query].keys())
            queryTermDocStats[query]= queryTermStats
        pickle.dump(queryTermDocStats,queryTermDocStatsFile,None)
    
    try:
        collectionTermStatsFile=open('objects/collectionTermStats','rb')
        collectionTermStats= pickle.load(collectionTermStatsFile)
    except IOError:
        collectionTermStatsFile=open('objects/collectionTermStats','wb')
        pickle.dump(collectionTermStats, collectionTermStatsFile, None)
    
    
def getDocStatsForQuery(queryTerms):
    global queryTermDocStats
    queryTermDict=dict()
    for qt in queryTerms:
        if qt in queryTermDocStats:
            queryTermDict[qt]=queryTermDocStats[qt]
        else:
            queryTermDict[qt]=getQueryTermInformation(qt)
    return queryTermDict

def getQueryTermInformation(queryTerm):
    global db
    docList=[]
    response, content =h.request('http://fiji5.ccs.neu.edu/~zerg/lemurcgi/lemur.cgi?d='+db+'&g=p&v='+queryTerm)
    response.fromcache
    contentString=content.decode('utf-8')
    contentString= contentString[contentString.find("<BODY>")+len("<BODY>"):contentString.find("<",contentString.find("<BODY>")+1)]
    cl=contentString.split('\n')
    while(cl.count('')):
        cl.remove('')
    temp=cl[0].split()
    collectionTermStats[queryTerm]=[int(temp[0]),int(temp[1])]
    for record in cl[1:]:
        rl=record.split()
        docList.append(DocumentForTerm(int(rl[0]), int(rl[1]), int(rl[2])))
    return  docList
    

def okapitf():
    global queries,queryLen,ave_querylen,queryTermDocStats
    docScoreFile = open('okapitf-results-20131119-d3', 'w')
    docScore=dict()
    for query in sorted(queries):
        queryTermStats= queryTermDocStats[query]
        docScore=dict()
        rank=0
        for qt in queryTermStats:
            qtf= queries[query][qt]
            
            oktfquery=qtf/(qtf+0.5+1.5*queryLen[query]/ave_querylen)
            for doc in queryTermStats[qt]:
                oktfdoc=doc.tf/(doc.tf + 0.5 + 1.5*doc.doclen/ave_doclen)
                innerProduct= oktfdoc*oktfquery
                #raw tf
#                 innerProduct=doc.tf*qtf
                if doc.docid in docScore:
                    docScore[doc.docid]=docScore[doc.docid]+innerProduct
                else:
                    docScore[doc.docid]=innerProduct
        for d in sorted(docScore,key = lambda k: docScore[k],reverse=True):
            rank=rank+1
            docScoreFile.write(str(query)+ ' Q0 '+ str(documentMappingDict[d]) + ' '+ str(rank)+' '+ str(docScore[d])+' Exp\n')    
            if (rank == 1000):
                break    
                
    print("finished processing okapi tf")
     

def okapitfidf():
    global queryLen,ave_querylen,queryTermDocStats,queries,collectionTermStats
    docScoreFile = open('okapitfidf-results-20131119-d3', 'w')
    docScore=dict()
    
    for query in sorted(queries):
        queryTermStats= queryTermDocStats[query]
        docScore=dict()
        rank=0
        
        for qt in queryTermStats:
            df=collectionTermStats[qt][1]
            qtf= queries[query][qt]
            oktfquery=qtf/(qtf+0.5+1.5*queryLen[query]/ave_querylen)
            idfWeight= math.log(total_documents/df)
            for doc in queryTermStats[qt]:
                oktfdoc=doc.tf/(doc.tf + 0.5 + 1.5*doc.doclen/ave_doclen)
                innerProduct= oktfdoc*oktfquery*idfWeight
                if doc.docid in docScore:
                    docScore[doc.docid]=docScore[doc.docid]+innerProduct
                else:
                    docScore[doc.docid]=innerProduct
        for d in sorted(docScore,key = lambda k: docScore[k],reverse=True):
            rank=rank+1
            docScoreFile.write(str(query)+ ' Q0 '+ str(documentMappingDict[d]) + ' '+ str(rank)+' '+ str(docScore[d])+' Exp\n')    
            if (rank == 1000):
                break    
                
    print("finished processing okapi tf-idf")

def languageModelLaplaceSmoothing():
    global  queryTermDocStats,queries
    docScoreFile = open('LMLaplace-results-20131119-d3', 'w')
    docNoQueryTermScore=dict()
    for query in sorted(queries):
        listOfTerms= queries[query].keys()
        queryTermStats= queryTermDocStats[query]
        docScore=dict()
        rank=0
        for qt in queryTermStats:
            for doc in queryTermStats[qt]:
                if not (doc.docid in docNoQueryTermScore):
                    docNoQueryTermScore[doc.docid] = 1/(doc.doclen + unique_terms)
                p= queries[query][qt]*math.log((doc.tf + 1)/(doc.doclen+ unique_terms))
                if doc.docid in docScore:
                    docScore[doc.docid][qt]=p
                else:
                    docScore[doc.docid] = {qt:p}

        # smoothing for query terms not contained in the document.
        for d in docScore:
            termScores = docScore[d]
            termsNotPresent= set(listOfTerms)-set(termScores.keys())
            score=0
            for term in docScore[d]:
                score=score+docScore[d][term]
            for t in termsNotPresent:
                tempScore= queries[query][t]*math.log(docNoQueryTermScore[d])
                score=score+tempScore
            docScore[d]=score
        for d in sorted(docScore,key = lambda k: docScore[k],reverse=True):
            rank=rank+1
            docScoreFile.write(str(query)+ ' Q0 '+ str(documentMappingDict[d]) + ' '+ str(rank)+' '+ str(docScore[d])+' Exp\n')    
            if (rank == 1000):
                break 
        
    docScoreFile.close()
    print("finished processing language modeling using Laplace Smoothing only.")                
        
def languageModelingJM():
    global queries, queryTermDocStats,collectionTermStats
    param=0.2
    docScoreFile = open('LM-JelinekMercer-results-20131119-d3', 'w')
    for query in sorted(queries):
        queryTermStats= queryTermDocStats[query]
        listOfTerms= queries[query].keys()
        docScore=dict()
        termCTF={}
        rank=0
        for qt in queryTermStats:
            ctf=collectionTermStats[qt][0]
            termCTF[qt]=ctf
            part2= (1-param)*(ctf/total_terms)
            for doc in queryTermStats[qt]:
                p= queries[query][qt]*math.log((param * (doc.tf/doc.doclen)) + part2)
                if doc.docid in docScore:
                    docScore[doc.docid][qt]=p
                else:
                    docScore[doc.docid] = {qt:p}

        for d in docScore:
            termScores = docScore[d]
            termsNotPresent= set(listOfTerms)-set(termScores.keys())
            score=0
            for term in docScore[d]:
                score=score+docScore[d][term]
            for t in termsNotPresent:
                tempScore= queries[query][t]*math.log((1-param)*(termCTF[t]/total_terms))
                score=score+tempScore
            docScore[d]=score
                     
        for d in sorted(docScore,key = lambda k: docScore[k],reverse=True):
            rank=rank+1
            docScoreFile.write(str(query)+ ' Q0 '+ str(documentMappingDict[d]) + ' '+ str(rank)+' '+ str(docScore[d])+' Exp\n')    
            if (rank == 1000):
                break
    docScoreFile.close()
    print("finished processing language modeling using Jelinek Mercer Smoothing only.")
    
def bm25():
    global queries, queryTermDocStats,collectionTermStats
    k1=1.2
    b=0.75
    k2=100
    docScoreFile = open('bm25-results-20131119-d3', 'w')
    docScore=dict()
    for query in sorted(queries):
        queryTermStats= queryTermDocStats[query]
        docScore=dict()
        rank=0
        for qt in queryTermStats:
            df=collectionTermStats[qt][1]
            qtf= queries[query][qt]
            for doc in queryTermStats[qt]:
                K=k1*((1.0-b)+(b*doc.doclen/ave_doclen))
                term1=(total_documents-df+0.5)/(df+0.5)
                term2= ((k1+1)*doc.tf)/(K+doc.tf)
                term3=(k2+1)*qtf/(k2+qtf)
                score=math.log(term1)*term2*term3
                if doc.docid in docScore:
                    docScore[doc.docid]=docScore[doc.docid]+score
                else:
                    docScore[doc.docid]=score
        for d in sorted(docScore,key = lambda k: docScore[k],reverse=True):
            rank=rank+1
            docScoreFile.write(str(query)+ ' Q0 '+ str(documentMappingDict[d]) + ' '+ str(rank)+' '+ str(docScore[d])+' Exp\n')    
            if (rank == 1000):
                break
    docScoreFile.close()
    print("finished processing BM25")
                    

def main():
    global queries,queryLen,ave_querylen
    print('start')
    queries=readFiles()
    queries,queryLen,ave_querylen=queryLenAndProcessing(queries)
    initialize()
    print('Initialization Completed')
    okapitf()
    okapitfidf()
    languageModelLaplaceSmoothing()
    languageModelingJM()
    bm25()
    print('Program Ends')


if __name__ == "__main__":
    main()