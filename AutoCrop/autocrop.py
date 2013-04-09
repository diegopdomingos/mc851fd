import Image
import sys
import os

def autocrop(image,name,x,y):
	i = Image.open(image)
	c = i.crop((x, y, x+64, y+64))
	c.save(str(x)+str(y)+name)

def main():
	imPath = sys.argv[1]
	destPath = sys.argv[2]
	files = os.listdir(imPath)

	for f in files:
		fp = str(imPath+"/"+f)
		print "Attempting to open file: "+fp
		image = Image.open(fp) 
		
		for i in range(0,image.size[1]-64,20):
			for j in range(0,image.size[0]-64,20):
				autocrop(fp, f, j, i)

main()	
