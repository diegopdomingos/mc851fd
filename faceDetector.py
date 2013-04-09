import Image
import sys
import kneighbor
from hoc import hoc
from debug import *
from os import listdir
import os
import copy
from hog import hog
from skimage import data
from time import time
from random import choice

INITIAL_IMAGE_SIZE = 90
MAX_IMAGE_SIZE = 250
THRESHOLD_TO_WEIGHT_RECORD = 1.065
DEFAULT_THRESHOLD_TO_FACE = 0.89
RECORDS_GROUPS = 20.0	# Must be a float!
WINDOW_SIZE = 64

first_time = time()

def makeSquare(img, initPoint, winSize):
	pix = img.load()
	for t in range(winSize):
		pix[initPoint[0]+t, initPoint[1]] = 255
		pix[initPoint[0], initPoint[1]+t] = 255
		pix[initPoint[0]+winSize-1, initPoint[1]+t] = 255
		pix[initPoint[0]+t, initPoint[1]+winSize] = 255


class Model:
	
	def __init__(self):
		self.records = []

	def record(self, value, descriptor):
		weight = 0
		#if len(self.records) > 0:
		#	near = kneighbor.nearNeighbor(descriptor, self.records)
		#	#print "Distance of nearest neighbor = "+str(near[2])
		#	if near[2] < THRESHOLD_TO_WEIGHT_RECORD and near[0] == value:
		#		#print "Weighting the existing image..."
		#		weight = near[3] + 1
		#		descriptor = near[1]
		#		self.records.remove((near[0],near[1],near[3]))
		self.records.append((value, tuple(descriptor),weight))

	def recordLearn(self, value, descriptor, weight):
		self.records.append((value, tuple(descriptor), weight))

class FaceDetector(object):
	classifier = None
	descriptor = None

	def callClassifier(self, imgVector, records):
		return self.classifier(imgVector, records)

	def callDescriptor(self, img):
		return self.descriptor(img)

	#isFace = 1 if image is a face
	#isFace = 0, otherwise
	def callTrain(self, imgVector, isFace):
		model = Model()

		for image in imgVector:
			model.record(isFace, self.callDescriptor(image))

		return model
	
	# Project faces to the same image size
	def normalizeFoundFaces(self, faces, img):
		normFaces = []
		for face in faces:
			normX = img.size[0]*(float(face[0][0])/face[1][0])
			normY = img.size[1]*(float(face[0][1])/face[1][1])
			normWinSize = 64*(float(img.size[0])/face[1][0])
			normFaces.append(((int(normX),int(normY)),normWinSize))

		return normFaces

	def drawFoundFaces(self, normFaces, img):
		img = img.copy()	
		for face in normFaces:
			makeSquare(img, face[0], int(face[1]))

		img.show()

	def callDetector(self, img, model, thresholdContinue = 0.2, thresholdFace = DEFAULT_THRESHOLD_TO_FACE):
		# Faces list
		faces = []

		#xmask = [0] * img.size[1]
		#mask = [xmask] * img.size[0]

		# Dividing the record group in 3 groups (NEW)
		print "Criando grupos de aprendizado..."
		recordGroup = []
		for i in range(int(RECORDS_GROUPS)):
			recordGroup.append([])

		for group in recordGroup:
			for i in range(int(len(model.records)/RECORDS_GROUPS)):
				x = choice(model.records)
				group.append(x)
				model.records.remove(x)

		imgo = img
		imgs = []

		# Create != imgs sizes	
		if img.size[0]>img.size[1] and img.size[0]>INITIAL_IMAGE_SIZE:

			for t in range(INITIAL_IMAGE_SIZE,MAX_IMAGE_SIZE,40): #was imgo.size[1]
				tt = float(t)/imgo.size[1]
				#print str(tt)
				img = copy.copy(imgo)
				img.thumbnail((int(imgo.size[0]*tt),int(imgo.size[1]*tt)), Image.ANTIALIAS)
				imgs.append(img)
				

		windowSize = WINDOW_SIZE
		tupleRecords = tuple(model.records)

		print "Quantidade de imgs="+str(len(imgs))		
		
		for tupleRecords in recordGroup:
			tupleRecords = tuple(tupleRecords)
			for img in imgs:
				#img.show()
                		print "Analisando imagem de tamanho="+str(img.size)
				# Sliding window
				for i in range(0,img.size[1]-windowSize + 1,20):
					for j in range(0, img.size[0]-windowSize + 1, 20):
						#os.system("killall display")
						#print "Analisando pixel="+str(j)+","+str(i)
						#tempShow = img.copy()	
						#makeSquare(tempShow, (j, i), windowSize)
						#tempShow.show()
						#print "Starting pixel"
						#print str(time()-first_time)
						#print "Starting crop..."
						# Crop the image with window
						temp = img.crop((j,i,j+windowSize,i+windowSize))
						#print str(time()-first_time)

						#print "Calculate the prob..."
		
						# Calculate the prob of face
						#ft = time()
						prob = self.callClassifier(tuple(self.callDescriptor(temp)), tupleRecords)
						#print str(time()-ft)
					
						# Compare with threshold
						#print "Probabilidade="+str(prob)
						if prob < thresholdContinue:
							print "Anulando pixels..."
			
						# If is a face
						elif prob > thresholdFace:
							print "uhul, its a faceee!!!!!!!!!!!!!"
							print "at i="+str(i)+" and j="+str(j)
							temp.show()
							faces.append(((j,i,j+windowSize,i+windowSize),(img.size[0],img.size[1])))

		self.drawFoundFaces(self.normalizeFoundFaces(faces, imgo),imgo)
		raw_input("Pause...")
		return faces

	def readImagesInDir(self, path, isFace):
		#files = listdir(path)       
		
		
		model = Model()
		t=0
		
		for dirname, dirnames, files in os.walk(path):
			for f in files:
				#t=t+1
				#if t%100 == 0:
					#print "Trained so far: "+str(t)
					#print "Total vectors in database: "+str(len(model.records))
				#img = data.load(os.getcwd()+"/"+str(os.path.join(dirname, f)))
				img = Image.open(str(os.path.join(dirname, f)))
				model.record(isFace, self.callDescriptor(img))
				del img
		print " Round="+str(len(model.records))
		return model

	def saveTrainedToDisk(self, path, trainedInstances):
		myFile = open(path, "a")
		for el in trainedInstances:
			myFile.write(str(el[0]) + ":" + str(el[1]) + ":" + str(el[2]) + "\n")
		myFile.close()

	def loadTrainedFromDisk(self, path):
		print "Abrindo arquivo de memoria..."
		myFile = open(path)

 		mdl = Model()
		face = 0
		t=0
		for el in myFile:
			hist = []
			face = int(el[0])
			weight = int(el[-2])
			for i in el[3:-4].split(','):
				hist.append(int(i.strip(']')))
			mdl.recordLearn(face, hist, weight)
			t=t+1
		myFile.close()

		print "Terminado com "+str(t)+" imagens aprendidas!"

		return mdl

def naiveBayes(imageVector, model, dist = 15):
	nFace = 0
	nNFace = 0
	total = 0

	# Calculates the number of faces and
	# the number of images
	for i in model.records:
		total += 1
		if i[0] == 1:
			nFace += 1
    
	# Prior probability
	priorFace = float(nFace)/total
	priorNFace = float(total-nFace)/total

	distance = 0
    

def learn(path_nofaces = "imgs/nofaces/", path_faces = "imgs/faces/", path_learn = "acquired.ml"):
	fd = FaceDetector()
	fd.descriptor = hoc

	faces = fd.readImagesInDir(path_faces, 1)
	nfaces = fd.readImagesInDir(path_nofaces, 0)

	#trained = fd.callTrain(faces[0], faces[1])
	#trained2 = fd.callTrain(nfaces[0], nfaces[1])

	fd.saveTrainedToDisk(path_learn, faces.records)
	fd.saveTrainedToDisk(path_learn, nfaces.records)


	print "Faces records="+str(len(faces.records))
	print "No faces records="+str(len(nfaces.records))
	print "Treinamento terminado com "+str(len(faces.records)+len(nfaces.records))+" imagens!"

def match(path_img, path_learn = "acquired.ml"):
	fd = FaceDetector()
	fd.classifier = kneighbor.kneighborCalc
	fd.descriptor = hoc

	model = fd.loadTrainedFromDisk(path_learn)

	for i in fd.callDetector(Image.open(path_img), model):
		i.show()

#    classifier(hoc(Image.open("imgs/faces/1.jpg")), train(imgs, imgg))	

# Parametros ideais:  

if sys.argv[1] == "learn":

	if len(sys.argv) > 2:
		learn(sys.argv[2], sys.argv[3], sys.argv[4])
	else:
		learn()
else:
	if sys.argv[1] == "match":
		#argv[2] = path to image
		#argv[3] = path to learnt file
		if len(sys.argv) > 3:
			match(sys.argv[2], sys.argv[3])
		else:
			match(sys.argv[2])
