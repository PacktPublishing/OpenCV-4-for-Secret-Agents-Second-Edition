# OpenCV 4 for Secret Agents - Second Edition

<a href="https://www.packtpub.com/application-development/opencv-4-secret-agents-second-edition?utm_source=github&utm_medium=repository&utm_campaign=9781789345360 "><img src="https://d1ldz4te4covpm.cloudfront.net/sites/default/files/imagecache/ppv4_main_book_cover/9781788998086cover.png" alt="OpenCV 4 for Secret Agents - Second Edition" height="256px" align="right"></a>

This is the code repository for [OpenCV 4 for Secret Agents - Second Edition](https://www.packtpub.com/application-development/opencv-4-secret-agents-second-edition?utm_source=github&utm_medium=repository&utm_campaign=9781789345360 ), published by Packt.

**Use OpenCV 4 in secret projects to classify cats, reveal the unseen, and react to rogue drivers.**

## What is this book about?

OpenCV 4 is a grand collection of image processing functions and computer vision algorithms. It is open source, it supports many programming languages and platforms, and it is fast enough for many real-time applications. What a lot of gadgets we can build with such a handy library! OpenCV 4 for Secret Agents is a broad selection of projects based on computer vision, machine learning, and several application frameworks. To target diverse desktop systems and Raspberry Pi, the book supports multiple Python versions (from 2.7 to 3.7). To target Android, the book supports Java in Android Studio, as well as C# in the Unity game engine.

This book covers the following exciting features:

* Detect motion and recognize gestures to control a smartphone game 
* Detect car headlights and estimate distances to them 
* Detect and recognize human and cat faces to trigger an alarm 
* Amplify motion in real-time video to show heartbeats and breaths 
* Make a physics simulation that detects shapes in a real-world drawing 
* Build OpenCV 4 projects in Python 3 for desktops and Raspberry Pi 
* Build OpenCV 4 Android applications in Android Studio and Unity 

If you feel this book is for you, get your [copy](https://www.amazon.com/dp/1789345367) today!

<a href="https://www.packtpub.com/?utm_source=github&utm_medium=banner&utm_campaign=GitHubBanner"><img src="https://raw.githubusercontent.com/PacktPublishing/GitHub/master/GitHub.png" 
alt="https://www.packtpub.com/" border="5" /></a>

## Who should read this book?

If you are an experienced software developer who is new to computer vision or machine learning, and wants to study these topics through creative projects, then this book is for you. The book will also help existing OpenCV users who want upgrade their projects to OpenCV 4 and new versions of other libraries, languages, tools, and operating systems. General familiarity with object-oriented programming, application development, and usage of operating systems (OS), developer tools, and the command line is required.	

## Instructions and navigation

The code is organized into folders, such as `Chapter002`, each corresponding to a chapter in the book. The following list shows the software dependencies for each chapter's code.

### Software list

| Chapter| Software required                                                                                                                 | OS required                       |
| ------ | --------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| 2      | OpenCV or 4.x*, Python 2.7 or 3.x, NumPy, SciPy, Requests, WxPython, PyInstaller (optional)                                       | Windows, Mac OS X, or Linux (Any) |
| 3      | OpenCV or 4.x* (plus optional cascade training tools from OpenCV 3.4), Python 2.7 or 3.x, NumPy, WxPython, PyInstaller (optional) | Windows, Mac OS X, or Linux (Any)|
| 4      | Android Studio, OpenCV 4.x* for Android | Windows, Mac OS X, and Linux (Any)                                                      | Windows, Mac OS X, or Linux (Any)|
| 5      | OpenCV 4.x*, Python 2.7 or 3.x, NumPy, WxPython | Windows, Mac OS X, and Linux (Any)                                              | Windows, Mac OS X, or Linux (Any)|
| 6      | Unity, OpenCV 4.x* for Unity  | Windows, Mac OS X, and Linux (Any)                                                                | Windows, Mac OS X, or Linux (Any)|
| 7      | OpenCV 4.x*, Python 2.7 or 3.x, NumPy, SciPy, WxPython, PyFFTW | Windows, Mac OS X, and Linux (Any)                               | Windows, Mac OS X, or Linux (Any)|
| 8      | OpenCV 4.x*, Python 2.7 or 3.x, NumPy, SciPy, WxPython, PyFFTW, Spinnaker SDK (optional) plus PySpin (optional)                   | Windows, Mac OS X, or Linux (Any)|

&ast; Most of the book's code should also work with OpenCV 3.4.

### External datasets and tools to train Haar and LBP cascades

The cascade-training script at `Chapter003/cascade_training/train.bat` (for Windows) or `Chapter003/cascade_training/train.sh` (for Mac or Linux) depends on tools that are not yet part of OpenCV 4, and on datasets that are not part of this repository.

OpenCV 3 contains tools for training Haar and LBP cascades. These tools are command-line executables called `opencv_createsamples.exe` and `opencv_traincascades.exe` (on Windows), or `opencv_createsamples` and `opencv_traincascades` (on Mac or Linux). The source code for these tools has not yet been updated to become part of OpenCV 4. Fortunately, though, the OpenCV 3 tools produce cascades that are forward-compatible with OpenCV 4. For the timebeing, the recommended way to train cascades for OpenCV 4 is to use the tools from an OpenCV 3 build. These tools can be obtained in any of the following ways:

* For Windows, find the tools in this repository under the `OpenCVTools/Windows/x64` folder (for 64-bit Windows) or `OpenCVTools/Windows/x86` (for 32-bit Windows). Append the relevant folder's absolute path to the system's `Path` variable so that our cascade-training script can find the tools.
* For Mac, install OpenCV 3 with MacPorts. The tools will be installed to `/opt/local/bin`, which should already be in the system's `PATH` variable.
* For Mac, install OpenCV 3 with Homebrew. The tools will be installed to `/opt/local/bin` or `opt/local/sbin`, which should already be in the system's `PATH` variable.
* For Linux, install OpenCV 3 with your system's package manager. The tools will be installed to `/usr/bin` or `/usr/local/bin`, which should already be in the system's `PATH` variable.
* For any system, build OpenCV 3 from source, find the tools among the built binary files, and add their folder to the system's `Path` variable (on Windows) or `PATH` variable (on Mac or Linux).

Soon, this README will be updated with details about obtaining the datasets.

### Third-party content in this repository

* Icons by Tatyana Suhodolska (www.artdesigncat.com)
* Images from various sources, to train and test classifiers

### Color images

We also provide a PDF file that has color images of the screenshots/diagrams used in this book. [Click here to download it](https://www.packtpub.com/sites/default/files/downloads/9781789345360_ColorImages.pdf).

## Related products

* Learn OpenCV 4 By Building Projects - Second Edition [[Packt]](https://www.packtpub.com/application-development/learn-opencv-4-building-projects-second-edition?utm_source=github&utm_medium=repository&utm_campaign=9781789341225 ) [[Amazon]](https://www.amazon.com/dp/1789341221)
* Mastering OpenCV 4 - Third Edition [[Packt]](https://www.packtpub.com/application-development/mastering-opencv-4-third-edition?utm_source=github&utm_medium=repository&utm_campaign=9781789533576 ) [[Amazon]](https://www.amazon.com/dp/1789533570)

## Get to know the author

**Joseph Howse** lives in a Canadian fishing village with four cats; the cats like fish, but they prefer chicken.

Joseph provides computer vision expertise through his company, [Nummist Media](https://nummist.com). His books include OpenCV 4 for Secret Agents, OpenCV 3 Blueprints, Android Application Programming with OpenCV 3, iOS Application Development with OpenCV 3, Learning OpenCV 3 Computer Vision with Python, and Python Game Programming by Example, published by Packt.

## Other books by the author

Joseph Howse is the author or co-author of the following **books on OpenCV 3**:

* [Learning OpenCV 3 Computer Vision with Python](https://www.packtpub.com/application-development/learning-opencv-3-computer-vision-python-second-edition)
* [Android Application Programming with OpenCV 3](https://www.packtpub.com/application-development/android-application-programming-opencv-3?utm_source=github&utm_medium=repository&utm_campaign=9781785285387)
* [iOS Application Development with OpenCV 3](https://www.packtpub.com/application-development/ios-application-development-opencv)
* [OpenCV 3 Blueprints](https://www.packtpub.com/application-development/opencv-3-blueprints)

He is also the author or co-author of the following **books on OpenCV 2**:

* [OpenCV Computer Vision with Python](https://www.packtpub.com/application-development/opencv-computer-vision-python?utm_source=github&utm_medium=repository&utm_campaign=9781782163923)
* [Android Application Programming with OpenCV](https://www.packtpub.com/application-development/android-application-programming-opencv?utm_source=github&utm_medium=repository&utm_campaign=9781849695206)
* [OpenCV for Secret Agents](https://www.packtpub.com/application-development/opencv-secret-agents?utm_source=github&utm_medium=repository&utm_campaign=9781783287376)
* [Python Game Programming By Example](https://www.packtpub.com/game-development/python-game-programming-example?utm_source=github&utm_medium=repository&utm_campaign=9781785281532)

## Suggestions and Feedback

[Click here](https://docs.google.com/forms/d/e/1FAIpQLSdy7dATC6QmEL81FIUuymZ0Wy9vH1jHkvpY57OiMeKGqib_Ow/viewform) if you have any feedback or suggestions.
