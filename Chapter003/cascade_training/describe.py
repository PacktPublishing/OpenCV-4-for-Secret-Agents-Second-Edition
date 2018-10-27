#!/usr/bin/env python


import cv2
import glob
import math
import sys

from __future__ import print_function


outputImageExtension = '.out.jpg'

def equalizedGray(image):
    return cv2.equalizeHist(cv2.cvtColor(
            image, cv2.COLOR_BGR2GRAY))

def describeNegativeHelper(imagePath, output):
    outputImagePath = '%s%s' % (imagePath, outputImageExtension)
    image = cv2.imread(imagePath)
    # Save an equalized version of the image.
    cv2.imwrite(outputImagePath, equalizedGray(image))
    # Append the equalized image to the negative description.
    print(outputImagePath, file=output)

def describeNegative():
    output = open('negative_description.txt', 'w')
    # Append all images from Caltech Faces 1999, since all are
    # non-cats.
    for imagePath in glob.glob('faces/*.jpg'):
        if imagePath.endswith(outputImageExtension):
            # This file is equalized, saved on a previous run.
            # Skip it.
            continue
        describeNegativeHelper(imagePath, output)
    # Append all images from the Urtho negative training set,
    # since all are non-cats.
    for imagePath in glob.glob('urtho_negatives/*.jpg'):
        if imagePath.endswith(outputImageExtension):
            # This file is equalized, saved on a previous run.
            # Skip it.
            continue
        describeNegativeHelper(imagePath, output)
    # Append non-cat images from VOC2007.
    input = open('VOC2007/ImageSets/Main/cat_test.txt', 'r')
    while True:
        line = input.readline().rstrip()
        if not line:
            break
        imageNumber, flag = line.split()
        if int(flag) < 0:
            # There is no cat in this image.
            imagePath = 'VOC2007/JPEGImages/%s.jpg' % imageNumber
            describeNegativeHelper(imagePath, output)

def rotateCoords(coords, center, angleRadians):
    # Positive y is down so reverse the angle, too.
    angleRadians = -angleRadians
    xs, ys = coords[::2], coords[1::2]
    newCoords = []
    n = min(len(xs), len(ys))
    i = 0
    centerX = center[0]
    centerY = center[1]
    cosAngle = math.cos(angleRadians)
    sinAngle = math.sin(angleRadians)
    while i < n:
        xOffset = xs[i] - centerX
        yOffset = ys[i] - centerY
        newX = xOffset * cosAngle - yOffset * sinAngle + centerX
        newY = xOffset * sinAngle + yOffset * cosAngle + centerY
        newCoords += [newX, newY]
        i += 1
    return newCoords

def preprocessCatFace(coords, image):
    
    leftEyeX, leftEyeY = coords[0], coords[1]
    rightEyeX, rightEyeY = coords[2], coords[3]
    mouthX = coords[4]
    if leftEyeX > rightEyeX and leftEyeY < rightEyeY and \
            mouthX > rightEyeX:
        # The "right eye" is in the second quadrant of the face,
        # while the "left eye" is in the fourth quadrant (from the
        # viewer's perspective.) Swap the eyes' labels in order to
        # simplify the rotation logic.
        leftEyeX, rightEyeX = rightEyeX, leftEyeX
        leftEyeY, rightEyeY = rightEyeY, leftEyeY

    eyesCenter = (0.5 * (leftEyeX + rightEyeX),
                  0.5 * (leftEyeY + rightEyeY))
    
    eyesDeltaX = rightEyeX - leftEyeX
    eyesDeltaY = rightEyeY - leftEyeY
    eyesAngleRadians = math.atan2(eyesDeltaY, eyesDeltaX)
    eyesAngleDegrees = eyesAngleRadians * 180.0 / math.pi
    
    # Straighten the image and fill in gray for blank borders.
    rotation = cv2.getRotationMatrix2D(
            eyesCenter, eyesAngleDegrees, 1.0)
    imageSize = image.shape[1::-1]
    straight = cv2.warpAffine(image, rotation, imageSize,
                              borderValue=(128, 128, 128))
    
    # Straighten the coordinates of the features.
    newCoords = rotateCoords(
            coords, eyesCenter, eyesAngleRadians)
    
    # Make the face as wide as the space between the ear bases.
    # (The ear base positions are specified in the reference
    # coordinates.)
    w = abs(newCoords[16] - newCoords[6])
    # Make the face square.
    h = w
    # Put the center point between the eyes at (0.5, 0.4) in
    # proportion to the entire face.
    minX = eyesCenter[0] - w/2
    if minX < 0:
        w += minX
        minX = 0
    minY = eyesCenter[1] - h*2/5
    if minY < 0:
        h += minY
        minY = 0
    
    # Crop the face.
    crop = straight[minY:minY+h, minX:minX+w]
    # Convert the crop to equalized grayscale.
    crop = equalizedGray(crop)
    # Return the crop.
    return crop

def describePositive():
    output = open('positive_description.txt', 'w')
    dirs = ['CAT_DATASET_01/CAT_00',
            'CAT_DATASET_01/CAT_01',
            'CAT_DATASET_01/CAT_02',
            'CAT_DATASET_02/CAT_03',
            'CAT_DATASET_02/CAT_04',
            'CAT_DATASET_02/CAT_05',
            'CAT_DATASET_02/CAT_06']
    for dir in dirs:
        for imagePath in glob.glob('%s/*.jpg' % dir):
            if imagePath.endswith(outputImageExtension):
                # This file is a crop, saved on a previous run.
                # Skip it.
                continue
            # Open the '.cat' annotation file associated with this
            # image.
            input = open('%s.cat' % imagePath, 'r')
            # Read the coordinates of the cat features from the
            # file. Discard the first number, which is the number
            # of features.
            coords = [int(i) for i in input.readline().split()[1:]]
            # Read the image.
            image = cv2.imread(imagePath)
            # Straighten and crop the cat face.
            crop = preprocessCatFace(coords, image)
            if crop is None:
                sys.stderr.write(
                        'Failed to preprocess image at %s.\n' % \
                        imagePath)
                continue
            # Save the crop.
            cropPath = '%s%s' % (imagePath, outputImageExtension)
            cv2.imwrite(cropPath, crop)
            # Append the cropped face and its bounds to the
            # positive description.
            h, w = crop.shape[:2]
            print('%s 1 0 0 %d %d' % (cropPath, w, h), file=output)


def main():    
    describeNegative()
    describePositive()

if __name__ == '__main__':
    main()
