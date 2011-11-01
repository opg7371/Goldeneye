"""
A set of algorithms that perform the iris segmentation.
"""

import Image
import cv
import ImageFilter
import threshold

class grayscaledImage:
	def __init__(self,inputImage):
		"""
		Test is image is 8-bit grayscale. If not, send it to doGrayscale
		"""
		if inputImage.format == 'L':
			self.grayImage = inputImage
		else:
			self.grayImage = self.doGrayscale(inputImage)

	def doGrayscale(self,img):
		"""
		Perform the grayscaling process. Returns a PIL image.
		"""
		return img.convert('L')

class blurredImage:
	#Implement flag structure to reprocess if blur isn't enough.
	#Make blur dependent on size of image and flag. Develop function to calculate.
	def __init__(self,inputImage):
		"""
		Uses ImageFilter's MedianFilter functions to blur the image.
		"""
		self.blurRadius = 9
		self.blurImage = inputImage.filter(ImageFilter.MedianFilter(self.blurRadius))


class thresholdedImage:
	# Will probably not need pixel objects. Just ignore thresholds <= the first Otsu result.
	# Fix variable names.
	def __init__(self,inputImage,tmin,tmax):
		"""
		Constructor for thresholdedImage. Performs Otsu thresholding.
		"""
		self.thresholdImageObject = threshold.otsuThresholder(inputImage,tmin,tmax)
		self.thresholdImage = self.thresholdImageObject.thresholdImage
		self.thr = self.thresholdImageObject.t

class CannyHough:
	# Write functions to intelligently tweak parameters. Create flag network to notify this function.
	# Throw exceptions for undetected circles
	def __init__(self, inputImage, radmin):
		"""
		Perform Canny edge detection, then a circular Hough transform
		to detect pupil and iris boudaries.
		"""
		#Hough transform variables
		cv_method = cv.CV_HOUGH_GRADIENT
		acc_res = 3
		dmin = 15
		canny = 50
		votes = 100
		#make these dependent on image size
		rmin = radmin
		rmax = 40
		
		cvImage = cv.CreateImageHeader(inputImage.size, cv.IPL_DEPTH_8U, 1)
		cv.SetData(cvImage, inputImage.tostring())
		self.cvSize = cv.GetSize(cvImage)


		# Create circle storage data structure
		self.storage = cv.CreateMat(50, 1, cv.CV_32FC3)
		print "test"

		circleList = []		

		# Main hough loop
		while 1:
			circles = cv.HoughCircles(cvImage,self.storage,cv_method,acc_res,dmin,canny,votes,rmin,rmax);
			print "Rows: ", self.storage.rows
			print "CircleList: ",circleList
			if self.storage.rows >= 1:
				for i in range(self.storage.rows):
					a = self.storage[i,0]
					(x,y,r)=a
					circleList.append([x,y,r])
			
			if len(circleList) < 4:
				self.storage = cv.CreateMat(50, 1, cv.CV_32FC3)
				rmin += 5
				rmax += 5
				if rmax >= inputImage.size[0]/4:
					rmin = 35
					rmax = 40
					if votes - 20 <= 0:
						break
					votes -= 20
				print "rmin - " + str(rmin)
				print "rmax - " + str(rmax)
				print "votes - " + str(votes)
				print "No circles found, retrying"
				continue
			else:
				break
		print "Storage"
		print self.storage.rows
		rad=0
		ind=0
		#Find largest (for iris, find closest to pupil center)
		for i in range(len(circleList)):
			a = circleList[i]
			if a[2] > rad:
				rad=a[2]
				ind=i
		circ = circleList[ind]
		(self.x,self.y,self.r) = (circ[0],circ[1],circ[2])
