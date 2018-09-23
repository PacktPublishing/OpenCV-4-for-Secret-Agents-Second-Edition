#!/bin/sh

wget https://web.archive.org/web/20150520175645/http://137.189.35.203/WebUI/CatDatabase/Data/CAT_DATASET_01.zip
wget https://web.archive.org/web/20150520175645/http://137.189.35.203/WebUI/CatDatabase/Data/CAT_DATASET_02.zip
wget http://www.vision.caltech.edu/Image_Datasets/faces/faces.tar
wget -r --no-parent --reject "index.html*" http://vision.cs.utexas.edu/voc/VOC2007_test/
svn export https://github.com/sonots/tutorial-haartraining/trunk/data/negatives urtho_negatives

unzip CAT_DATASET_01.zip -d CAT_DATASET_01
unzip CAT_DATASET_02.zip -d CAT_DATASET_02

mkdir faces
tar -xvf faces.tar -C faces

mv vision.cs.utexas.edu/voc/VOC2007_test VOC2007
rm -rf vision.cs.utexas.edu
