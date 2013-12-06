'''
Created on Oct 4, 2013

@author: Ankit
'''
import math

pages=set()
linkGraphFileName= 'LinkGraph'
linkGraphFileName_wt2g= 'wt2g_inlinks.txt'
inLinks= dict()
outLinks=dict()
pageRank=dict()
sinkNodeSet=set()
d=0.85 # page rank damping or teleportation factor

# count the number of out links
def addOutLink(link):
    if(outLinks.__contains__(link)):
        outLinks[link]+=1
    else:
        outLinks[link]=1   

# initial values for page rank
def initializePageRank(n):
    for p in pages:
        pageRank[p]=1/n 

# calculate the page rank for the in links to the given page
def pageRankInlinks(page):
    inLinkPageRank=0
    try:
        for inLink in inLinks[page]:
            inLinkPageRank+= d*pageRank[inLink]/outLinks[inLink]
    except KeyError:
        pass
    return inLinkPageRank

# calculate the perplexity for the page ranks
def calculatePerplexity(pageRank):
    temp=0
    for p in pageRank:
        rank= pageRank[p]
        temp+=rank*math.log2(rank)
    return pow(2,-temp)

# Used to check for the number of iterations we get the
# same unit's place for perplexity
uniformPerplexityIteration=1

# check if the the perplexity has converged to the unit's
# place
def isConverged(newPerplexity,oldPerplexity):
    global uniformPerplexityIteration
    val1= int(math.modf(newPerplexity)[1])%10
    val2= int(math.modf(oldPerplexity)[1])%10
    if val1 == val2:
        uniformPerplexityIteration= uniformPerplexityIteration+1
    else:
        uniformPerplexityIteration=1
    if uniformPerplexityIteration==4:
        return True
    else: 
        return False
    
# page rank computation for wt2g_inlinks
def pageRankComputationPerplexityConvergence():
    perplexityValuesFile= open('perplexity_values', 'w')
    global pageRank,sinkNodeSet,pages
    n=len(pages)
    initializePageRank(n)
    oldPerplexity=0
    newPerplexity=calculatePerplexity(pageRank)
    count=1
    while not isConverged(newPerplexity, oldPerplexity):
        count+=1
        sinkPR=0
        newpagerank={}
        for s in sinkNodeSet:
            sinkPR+=pageRank[s]
        for p in pages:
            newPR= (1-d)/n
            newPR+= d*sinkPR/n
            newPR+= pageRankInlinks(p)
            newpagerank[p]=newPR     
        pageRank=newpagerank
        perplexityValuesFile.write(str(newPerplexity)+'\n')
        oldPerplexity=newPerplexity
        newPerplexity= calculatePerplexity(pageRank)
    perplexityValuesFile.write(str(newPerplexity)+'\n')    
    perplexityValuesFile.write('Total Number of Iterations: '+str(count))
    perplexityValuesFile.close()

# write page rank and in link results to file
def writeResults():
    prWT2g= open('PageRankWT2g','w')
    count=0
    prWT2g.write('Top 50 pages with high page ranks: \n')
    for pr in  sorted(pageRank, key=pageRank.get, reverse=True):
        prWT2g.write('Page Rank of '+ pr.ljust(10) + ':'.ljust(2)+ str(round(pageRank[pr],8)).ljust(10)+'\n')
        count+=1
        if count==50:
            break
    
    prWT2g.close()
    topInlinks= open('Top_inlinks_count', 'w')
    topInlinks.write('Top 50 pages with high in-links: \n')
    count=0
    for i in sorted(inLinks,key=lambda k:len(inLinks[k]), reverse=True):
        topInlinks.write('Page: '+i.ljust(10)+ " has "+ str(len(inLinks[i])) + ' in-links\n')
        count+=1
        if count==50:
            break
    topInlinks.close()

# page rank computation for the six node graph
def pageRankComputation():
    global pageRank,sinkNodeSet,pages
    n=len(pages)
    initializePageRank(n)
    count=0
    prSixNodeGraph= open('PageRankSixNodes','w')
    while count<100:
        count+=1
        sinkPR=0
        newpagerank={}
        for p in sinkNodeSet:
            sinkPR+=pageRank[p]
        for p in pages:
            newPR= (1-d)/n
            newPR+= d*sinkPR/n
            newPR+= pageRankInlinks(p)
            newpagerank[p]=newPR
        pageRank= newpagerank
        if(count in [1,10,100]):
            prSixNodeGraph.write('count: '+ str(count)+'\n')
            for pr in pageRank.keys():
                prSixNodeGraph.write('Page Rank of '+ pr+ ' is '+ str(round(pageRank[pr],8))+'\n')
    prSixNodeGraph.close()
   
# process the the give link graph file name and populate in links and out links     
def processLinkGraphFile(linkGraphFileName):
    linkGraphFile=open(linkGraphFileName,'r')
    for line in linkGraphFile:
        line=line.strip()
        listLinks= line.split(' ')
        newPage=listLinks[0]
        pages.add(newPage)
        tempList=list()
        for i in listLinks[1:]:
            tempList.append(i)
            addOutLink(i)
        inLinks[newPage]=tempList
    linkGraphFile.close()
    for p in pages:
        if(p not in outLinks):
            sinkNodeSet.add(p)
        
# clear all data structures
def clearAllDataStructures():
    inLinks.clear()
    outLinks.clear()
    pageRank.clear();
    sinkNodeSet.clear()
    pages.clear()
    
# main    
def main(): 
    print("Running...")
    processLinkGraphFile(linkGraphFileName)
    pageRankComputation()
    clearAllDataStructures()
    processLinkGraphFile(linkGraphFileName_wt2g)
    pageRankComputationPerplexityConvergence()
    writeResults()
    print('program ends')
        
if __name__ == "__main__":
    main()    