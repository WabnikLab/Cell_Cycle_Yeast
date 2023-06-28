#Once selected the positions and the rois, run this code to obtain the csv files, which will be analysed posteriorly in the python script

#Import libraries
import sys  
reload(sys)

sys.setdefaultencoding('utf8')

from ij import IJ, ImagePlus
from ij.io import FileSaver
import os 
import re
from ij.process import ImageStatistics as IS
from ij.gui import Roi, OvalRoi, Toolbar 
from ij.plugin.frame import RoiManager
from ij.measure import Measurements
from ij import WindowManager
from ij.measure import Measurements
import csv
from ij.gui import Overlay
from java.awt import Font
from ij.gui import TextRoi
from java.awt import Color
from array import zeros
from ij.process import FloatProcessor

#--- FUNCTIONS ---#
def getRoilist(roi):

	IJ.run("ROI Manager...")
	rm = RoiManager.getInstance()
	rm.reset()

	rm.runCommand("Open",roi)

	roi_list = rm.getRoisAsArray()

	return(roi_list)

def getIntensities(imp , roi_list):

	n_slice = imp.getNFrames()
	if n_slice == 1:
		n_slice = imp.getNSlices()

	#Select the image
	stack = imp.getImageStack()
	calibration = imp.getCalibration()
	
	Intensities = []
	
	#Iteration over the frames
	for i in range(0 , n_slice):
		
		ip = stack.getProcessor(i + 1)
		
		frame = []
		
		#Iteration over the rois in each frame to take the mean
		for roi in roi_list:
			
			ip.setRoi(roi)
			
			stats = IS.getStatistics(ip , Measurements.MEAN , calibration)
			mean = stats.mean
			
			frame.append(mean)
		
		Intensities.append(frame)
	
	return Intensities

def WriteCsvFile(printfile , title , folder, channel):

	with open(folder+"\\"+title+channel+".csv" , 'w') as csvfile:
		writer = csv.writer(csvfile,delimiter=",")
		writer.writerows(printfile)

#Here there are the folder we are gonna need
folder = "D:\Mariam\CDC2_RP_v2" #Folder were time-lapse data is found
dataFolder = "C:\Users\maria\Desktop\TFM\Scripts\CDC2_4H_PERIOD_v2\Data" #Folder were the csv generated data is saved
optionsFile = "C:\Users\maria\Desktop\TFM\Scripts\CDC2_4H_PERIOD_v2\options.csv" #File with options desired such as number of channels, start and end point, etc

#Take the options from the Csv file
options = []

#if there is no options folder program will stop
try:
	with open(optionsFile , "rb") as csvfile:
		spamreader = csv.reader(csvfile , delimiter = "," ,)
		for row in spamreader:
			options.append(row[1])

	channels = []
	for i in range(3,2+int(options[1])):
		channels.append(options[i]) # 0 for DIC, 1 for green and 2 for red

	backGround = options[10+int(options[1])]
	start = int(options[4+int(options[1])])
	end = int(options[5+int(options[1])]) - int(options[4+int(options[1])])
	
except:
	#os.mkdir("E\ImageAnalisys\FijiAn\options.csv")
	sys.exit("Options file must be in the folowing path: " + optionsFile)

#if there is no folder for images program will stop
if os.path.exists(folder):
	pass
else:
	os.mkdir(folder)
	sys.exit("folder "+folder+" has been created. Your images shold be here")

if os.path.exists(dataFolder):
	pass
else:
	os.mkdir(dataFolder)


positions = os.listdir(folder)


for position in os.listdir(folder):

	for filename in os.listdir(folder+'\\'+position):
		if filename.find("RoiSet.zip") >= 0: #Check that a roi file exists
			roiname = folder+'\\'+position+'\\'+filename
			print roiname
			rois = getRoilist(roiname) #Open and obtain rois
	
	#Error control to check that rois exists
	"""try:
		rois	
	except:
		sys.exit("Folder "+position+" does not have any roi.zip file")"""
		
	for channel in channels: #iterate over the green and red channels
		IJ.run("Image Sequence...", "open="+folder+"/"+position+"/img_channel00"+channel+"_position000_time000000000_z000.tif number="+str(end)+" starting="+str(start)+" file=channel00"+channel+ " sort")
		image = IJ.getImage()
		
		#get the intensities in the different channels
		if int(channel) == int(channels[0]):
			greenResults = getIntensities(image,rois)
			#print greenResults
			
		elif int(channel) == int(channels[1]):
			redResults = getIntensities(image,rois)
			#print (redResults)
			
		IJ.selectWindow(image.title)
		IJ.run("Close")

	header = ["Frame"]
	
	for i in range(0,len(greenResults[i])):
		header.append(position+"_"+str(i))
	#print header
	results_green = [header]

	#Normalize the results to the red channel
	for i in range(0,len(greenResults)):
		aux_green = [i+start]
		for j in range(0,len(greenResults[i])):

			if redResults[i][j] < int(backGround):
				aux_green.append(0)
			else: 
				aux_green.append(greenResults[i][j] / (greenResults[i][j] + redResults[i][j]))
		
		results_green.append(aux_green)


	WriteCsvFile(results_green,position,dataFolder, 'GFP')

print "Finished"
