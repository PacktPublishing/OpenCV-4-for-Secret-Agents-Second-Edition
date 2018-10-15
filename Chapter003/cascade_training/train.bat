set vec=binary_description
set info=positive_description.txt
set bg=negative_description.txt

REM Uncomment the next 4 variables for LBP training.
REM set featureType=LBP
REM set data=lbpcascade_frontalcatface\
REM set dst=..\cascades\lbpcascade_frontalcatface.xml
REM set mode=BASIC

REM Uncomment the next 4 variables for Haar training with basic
REM features.
set featureType=HAAR
set data=haarcascade_frontalcatface\
set dst=..\cascades\haarcascade_frontalcatface.xml
set mode=BASIC

REM Uncomment the next 4 variables for Haar training with
REM extended features.
REM set featureType=HAAR
REM set data=haarcascade_frontalcatface_extended\
REM set dst=..\cascades\haarcascade_frontalcatface_extended.xml
REM set mode=ALL

REM Set numPosTotal to be the line count of info.
for /f %c in ('find /c /v "" ^< "%info%"') do set numPosTotal=%c

REM Set numNegTotal to be the line count of bg.
for /f %c in ('find /c /v "" ^< "%bg%"') do set numNegTotal=%c

set /a numPosPerStage=%numPosTotal%*9/10
set /a numNegPerStage=%numNegTotal%*9/10
set numStages=20
set minHitRate=0.995
set maxFalseAlarmRate=0.5

REM Ensure that the data directory exists and is empty.
if not exist "%data%" (mkdir "%data%") else del /f /q "%data%\*.xml"

opencv_createsamples -vec "%vec%" -info "%info%" -bg "%bg%" ^
        -num "%numPosTotal%"
opencv_traincascade -data "%data%" -vec "%vec%" -bg "%bg%" ^
        -numPos "%numPosPerStage%" -numNeg "%numNegPerStage%" ^
        -numStages "%numStages%" -minHitRate "%minHitRate%" ^
        -maxFalseAlarmRate "%maxFalseAlarmRate%" ^
        -featureType "%featureType%" -mode "%mode%"

cp "%data%\cascade.xml" "%dst%"