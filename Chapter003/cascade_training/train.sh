#!/bin/sh

vec=binary_description
info=positive_description.txt
bg=negative_description.txt

# Uncomment the next 4 variables for LBP training.
#featureType=LBP
#data=lbpcascade_frontalcatface/
#dst=../cascades/lbpcascade_frontalcatface.xml
#mode=BASIC

# Uncomment the next 4 variables for Haar training with basic
# features.
featureType=HAAR
data=haarcascade_frontalcatface/
dst=../cascades/haarcascade_frontalcatface.xml
mode=BASIC

# Uncomment the next 4 variables for Haar training with
# extended features.
#featureType=HAAR
#data=haarcascade_frontalcatface_extended/
#dst=../cascades/haarcascade_frontalcatface_extended.xml
#mode=ALL

# Set numPosTotal to be the line count of info.
numPosTotal=`wc -l < $info`

# Set numNegTotal to be the line count of bg.
numNegTotal=`wc -l < $bg`

numPosPerStage=$(($numPosTotal*9/10))
numNegPerStage=$(($numNegTotal*9/10))
numStages=20
minHitRate=0.995
maxFalseAlarmRate=0.5

# Ensure that the data directory exists and is empty.
if [ ! -d "$data" ]; then
    mkdir "$data"
else
    rm "$data/*.xml"
fi

opencv_createsamples -vec "$vec" -info "$info" -bg "$bg" \
        -num "$numPosTotal"
opencv_traincascade -data "$data" -vec "$vec" -bg "$bg" \
        -numPos "$numPosPerStage" -numNeg "$numNegPerStage" \
        -numStages "$numStages" -minHitRate "$minHitRate" \
        -maxFalseAlarmRate "$maxFalseAlarmRate" \
        -featureType "$featureType" -mode "$mode"

cp "$data/cascade.xml" "$dst"