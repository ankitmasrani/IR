'''
Created on Oct 4, 2013

@author: Ankit
'''
from collections import OrderedDict
from test.test_iterlen import len

pages= {'A', 'B', 'C', 'D', 'E','F'}

linkGraphFile= open('LinkGraph', mode='r')
inLinks= OrderedDict()
outLinks=dict()
pageRank=dict()
sinkNodeSet=set()
d=0.85 # page rank damping or teleportation factor

# add number of outlinks for each page
def addOutLink(link):
    if(outLinks.__contains__(link)):
        outLinks[link]+=1
    else:
        outLinks[link]=1 
        
# check if a particular page is a sink node and 
# add it to the sink node set if it is
def checkAndAddSinkNode(page):
    if outLinks.__contains__(page):
        pass
    else:
        sinkNodeSet.add(page)

# initial values for page rank
def initializePageRank():
    for p in pages:
        pageRank[p]=1/len(pages) 

def pageRankInlinks(page):
    inLinkPageRank=0
    for inLink in inLinks[page]:
        inLinkPageRank+= d*pageRank[inLink]/outLinks[inLink]
    return inLinkPageRank

# foreach page p in P
#   PR(p) = 1/N                          /* initial value */
# 
# while PageRank has not converged do
#   sinkPR = 0
#   foreach page p in S                  /* calculate total sink PR */
#     sinkPR += PR(p)
#   foreach page p in P
#     newPR(p) = (1-d)/N                 /* teleportation */
#     newPR(p) += d*sinkPR/N             /* spread remaining sink PR evenly */
#     foreach page q in M(p)             /* pages pointing to p */
#       newPR(p) += d*PR(q)/L(q)         /* add share of PageRank from in-links */
#   foreach page p
#     PR(p) = newPR(p)
# 
# return PR
def pageRankComputation():
    initializePageRank()
#     newPageRank=dict()
    n=len(pages)
    flag=False
    while True:
        flag=False
        sinkPR=0
        for p in sinkNodeSet:
            sinkPR+=pageRank[p]
        for p in pages:
            newPR= (1-d)/n
            newPR+= d*sinkPR/n
            newPR+= pageRankInlinks(p)
            if(round(newPR,2) != round(pageRank[p],2)):
                flag=True
            pageRank[p]=newPR
        if (not flag):
            break
    
    sum=0
    for pr in pageRank.keys():
        print('Page Rank of '+ pr+ ' is '+ str(round(pageRank[pr],3)))
        sum+=pageRank[pr]
    print(sum)
        
    
def main(): 
    for line in linkGraphFile:
        listLinks= line.split(' ')
        tempList=[]
        for i in listLinks[1:]:
            i=i.rstrip()
            tempList.append(i)
            addOutLink(i)
        inLinks[listLinks[0]]=tempList
    linkGraphFile.close()
    for k in inLinks.keys():
        checkAndAddSinkNode(k)
    
    pageRankComputation()
   
#     for k,v in inLinks.items():
#         print(k + " inlinks: " + str(v))
#         
#     for k,v in outLinks.items():
#         print(k +" outlinks: " + str(v))
#         
#     print(sinkNodeSet)

        
if __name__ == "__main__":
    main()    