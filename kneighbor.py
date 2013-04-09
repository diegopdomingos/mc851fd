# K-NEIGHBOR

from debug import *
from time import time
import numpy

KN = 10

def neighborDist(neighbor, imgVector):
	tempDist = 0
	for value in range(256):
		tempDist = tempDist + (neighbor[1][value] - imgVector[value])**2
	return float(tempDist)**(1.0/255)
	
def nearNeighbor(imgVector, records):
	
	nearNeigh = []

	for neighbor in records:
		nearNeigh.append((neighbor[0],neighbor[1],neighborDist(neighbor, imgVector),neighbor[2]))

	nearNeigh = sorted(nearNeigh, key=lambda nearNeigh: nearNeigh[2])

	return nearNeigh[0]

def kneighborCalc(imgVector, model):

	distances = []
	
	#print model
	for i in range(KN):
		distances.append((0,9999999999))
	
	#	print model

	#t=0
	# Distance of neighborhood
	#ft = time()
        for neighbor in model:
                #DBG("neighborDist ="+str(neighborDist(neighbor, imgVector)))
		thisDist = neighborDist(neighbor, imgVector)
                distances.append((neighbor[0],thisDist))
		#print "Weight of image:"+str(neighbor[2])
		#Added to support weight model
		#for i in range(neighbor[2]+1):
		#distances.sort()
		#distances[k] = (neighbor[0],thisDist)
		#distances = distances + tuple((neighbor[0],thisDist))
		#k=k+1
		#print "Distance calculated, sorting..."
		distances = sorted(distances, key=lambda distances: distances[1])
		#print distances
		distances.remove(distances[KN])
		#print "Sorting ended"
		#t=t+1
	#print "Time to each neighbor="+str(time()-ft)
	
	#print "Vou sortar"
	#x = raw_input("s")
        # Sorting
        #distances = sorted(distances, key=lambda distances: distances[1])
	#print "IUPI!"	
	#print distances	
	#distances.sort(axis=1)
        #DBG("Printing distances object...")
        #DBG(distances)

        score = 0.0
        for n in range(1,KN):
                score = score + distances[n][0]

        return float(score)/KN
