package com.nummist.goldgesture;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.LinkedList;
import java.util.List;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.util.Log;
import android.view.Window;
import android.view.WindowManager;
import android.widget.Toast;

import org.opencv.android.CameraBridgeViewBase;
import org.opencv.android.CameraBridgeViewBase.CvCameraViewFrame;
import org.opencv.android.CameraBridgeViewBase.CvCameraViewListener2;
import org.opencv.android.OpenCVLoader;
import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.MatOfByte;
import org.opencv.core.MatOfFloat;
import org.opencv.core.MatOfPoint;
import org.opencv.core.MatOfPoint2f;
import org.opencv.core.MatOfRect;
import org.opencv.core.Point;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.opencv.objdetect.CascadeClassifier;
import org.opencv.objdetect.Objdetect;
import org.opencv.video.Video;

public final class CameraActivity extends Activity
        implements CvCameraViewListener2 {

    // A tag for log output.
    private static final String TAG = "CameraActivity";

    // An identifier for the camera permissions request.
    private static final int PERMISSIONS_REQUEST_CAMERA = 0;

    // Parameters for face detection.
    private static final double SCALE_FACTOR = 1.2;
    private static final int MIN_NEIGHBORS = 3;
    private static final int FLAGS = Objdetect.CASCADE_SCALE_IMAGE;
    private static final double MIN_SIZE_PROPORTIONAL = 0.25;
    private static final double MAX_SIZE_PROPORTIONAL = 1.0;

    // The portion of the face that is excluded from feature
    // selection on each side.
    // (We want to exclude boundary regions containing background.)
    private static final double MASK_PADDING_PROPORTIONAL = 0.15;

    // Parameters for face tracking.
    private static final int MIN_FEATURES = 10;
    private static final int MAX_FEATURES = 80;
    private static final double MIN_FEATURE_QUALITY = 0.05;
    private static final double MIN_FEATURE_DISTANCE = 4.0;
    private static final float MAX_FEATURE_ERROR = 200f;

    // Parameters for gesture detection
    private static final double MIN_SHAKE_DIST_PROPORTIONAL = 0.01;
    private static final double MIN_NOD_DIST_PROPORTIONAL = 0.0025;
    private static final double MIN_BACK_AND_FORTH_COUNT = 2;

    // The camera view.
    private CameraBridgeViewBase mCameraView;

    // The dimensions of the image before orientation.
    private double mImageWidth;
    private double mImageHeight;

    // The current gray image before orientation.
    private Mat mGrayUnoriented;

    // The current and previous equalized gray images.
    private Mat mEqualizedGray;
    private Mat mLastEqualizedGray;

    // The mask, in which the face region is white and the
    // background is black.
    private Mat mMask;
    private Scalar mMaskForegroundColor;
    private Scalar mMaskBackgroundColor;

    // The face detector, more detection parameters, and
    // detected faces.
    private CascadeClassifier mFaceDetector;
    private Size mMinSize;
    private Size mMaxSize;
    private MatOfRect mFaces;

    // The initial features before tracking.
    private MatOfPoint mInitialFeatures;

    // The current and previous features being tracked.
    private MatOfPoint2f mFeatures;
    private MatOfPoint2f mLastFeatures;

    // The status codes and errors for the tracking.
    private MatOfByte mFeatureStatuses;
    private MatOfFloat mFeatureErrors;

    // Whether a face was being tracked last frame.
    private boolean mWasTrackingFace;

    // Colors for drawing.
    private Scalar mFaceRectColor;
    private Scalar mFeatureColor;

    // Gesture detectors.
    private BackAndForthGesture mNodHeadGesture;
    private BackAndForthGesture mShakeHeadGesture;

    // The audio tree for the 20 questions game.
    private YesNoAudioTree mAudioTree;

    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (OpenCVLoader.initDebug()) {
            Log.i(TAG, "Initialized OpenCV");
        } else {
            Log.e(TAG, "Failed to initialize OpenCV");
            finish();
        }

        final Window window = getWindow();
        window.addFlags(
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        setContentView(R.layout.activity_camera);
        mCameraView = (CameraBridgeViewBase)
                findViewById(R.id.camera_view);
        //mCameraView.enableFpsMeter();
        mCameraView.setCvCameraViewListener(this);
    }

    @Override
    public void onPause() {
        if (mCameraView != null) {
            mCameraView.disableView();
        }
        if (mAudioTree != null) {
            mAudioTree.stop();
        }
        resetGestures();
        super.onPause();
    }

    @Override
    public void onResume() {
        super.onResume();
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                    Manifest.permission.CAMERA)) {
                showRequestPermissionRationale();
            } else {
                ActivityCompat.requestPermissions(this,
                        new String[] { Manifest.permission.CAMERA },
                        PERMISSIONS_REQUEST_CAMERA);
            }
        } else {
            Log.i(TAG, "Camera permissions were already granted");

            // Start the camera.
            mCameraView.enableView();
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (mCameraView != null) {
            // Stop the camera.
            mCameraView.disableView();
        }
        if (mAudioTree != null) {
            mAudioTree.stop();
        }
        resetGestures();
    }

    void showRequestPermissionRationale() {
        AlertDialog dialog = new AlertDialog.Builder(this).create();
        dialog.setTitle("Camera, please");
        dialog.setMessage(
                "Goldgesture uses the camera to see you nod or shake " +
                "your head. You will be asked for camera access.");
        dialog.setButton(AlertDialog.BUTTON_NEUTRAL, "OK",
                new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.dismiss();
                        ActivityCompat.requestPermissions(
                                CameraActivity.this,
                                new String[] {
                                        Manifest.permission.CAMERA },
                                PERMISSIONS_REQUEST_CAMERA);
                    }
                });
        dialog.show();
    }

    @Override
    public void onRequestPermissionsResult(final int requestCode,
            final String permissions[], final int[] grantResults) {
        switch (requestCode) {
            case PERMISSIONS_REQUEST_CAMERA: {
                if (grantResults.length > 0 &&
                        grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Log.i(TAG, "Camera permissions were granted just now");

                    // Start the camera.
                    mCameraView.enableView();
                } else {
                    Log.e(TAG, "Camera permissions were denied");
                    finish();
                }
                break;
            }
        }
    }

    @Override
    public void onCameraViewStarted(final int width,
                                    final int height) {

        mImageWidth = width;
        mImageHeight = height;

        initFaceDetector();
        mFaces = new MatOfRect();

        final int smallerSide;
        if (height < width) {
            smallerSide = height;
        } else {
            smallerSide = width;
        }

        final double minSizeSide =
                MIN_SIZE_PROPORTIONAL * smallerSide;
        mMinSize = new Size(minSizeSide, minSizeSide);

        final double maxSizeSide =
                MAX_SIZE_PROPORTIONAL * smallerSide;
        mMaxSize = new Size(maxSizeSide, maxSizeSide);

        mInitialFeatures = new MatOfPoint();
        mFeatures = new MatOfPoint2f(new Point());
        mLastFeatures = new MatOfPoint2f(new Point());
        mFeatureStatuses = new MatOfByte();
        mFeatureErrors = new MatOfFloat();

        mFaceRectColor = new Scalar(0.0, 0.0, 255.0);
        mFeatureColor = new Scalar(0.0, 255.0, 0.0);

        final double minShakeDist =
                smallerSide * MIN_SHAKE_DIST_PROPORTIONAL;
        mShakeHeadGesture = new BackAndForthGesture(minShakeDist);

        final double minNodDist =
                smallerSide * MIN_NOD_DIST_PROPORTIONAL;
        mNodHeadGesture = new BackAndForthGesture(minNodDist);

        mAudioTree = new YesNoAudioTree(this);
        mAudioTree.start();

        mGrayUnoriented = new Mat(height, width, CvType.CV_8UC1);

        // The rest of the matrices are transposed.

        mEqualizedGray = new Mat(width, height, CvType.CV_8UC1);
        mLastEqualizedGray = new Mat(width, height, CvType.CV_8UC1);

        mMask = new Mat(width, height, CvType.CV_8UC1);
        mMaskForegroundColor = new Scalar(255.0);
        mMaskBackgroundColor = new Scalar(0.0);
    }

    @Override
    public void onCameraViewStopped() {
    }

    @Override
    public Mat onCameraFrame(final CvCameraViewFrame inputFrame) {
        final Mat rgba = inputFrame.rgba();

        // For processing, orient the image to portrait and equalize
        // it.
        Imgproc.cvtColor(rgba, mGrayUnoriented,
                Imgproc.COLOR_RGBA2GRAY);
        Core.transpose(mGrayUnoriented, mEqualizedGray);
        Core.flip(mEqualizedGray, mEqualizedGray, 0);
        Imgproc.equalizeHist(mEqualizedGray, mEqualizedGray);

        final List<Point> featuresList;

        mFaceDetector.detectMultiScale(
                mEqualizedGray, mFaces, SCALE_FACTOR, MIN_NEIGHBORS,
                FLAGS, mMinSize, mMaxSize);

        if (mFaces.rows() > 0) { // Detected at least one face

            // Get the first detected face.
            final double[] face = mFaces.get(0, 0);

            double minX = face[0];
            double minY = face[1];
            double width = face[2];
            double height = face[3];
            double maxX = minX + width;
            double maxY = minY + height;

            // Draw the face.
            Imgproc.rectangle(
                    rgba, new Point(mImageWidth - maxY, minX),
                    new Point(mImageWidth - minY, maxX),
                    mFaceRectColor);

            // Create a mask for the face region.
            double smallerSide;
            if (height < width) {
                smallerSide = height;
            } else {
                smallerSide = width;
            }
            double maskPadding =
                    smallerSide * MASK_PADDING_PROPORTIONAL;
            mMask.setTo(mMaskBackgroundColor);
            Imgproc.rectangle(
                    mMask,
                    new Point(minX + maskPadding,
                            minY + maskPadding),
                    new Point(maxX - maskPadding,
                            maxY - maskPadding),
                    mMaskForegroundColor, -1);

            // Find features in the face region.
            Imgproc.goodFeaturesToTrack(
                    mEqualizedGray, mInitialFeatures, MAX_FEATURES,
                    MIN_FEATURE_QUALITY, MIN_FEATURE_DISTANCE,
                    mMask, 3, false, 0.04);
            mFeatures.fromArray(mInitialFeatures.toArray());
            featuresList = mFeatures.toList();

            if (mWasTrackingFace) {
                updateGestureDetection();
            } else {
                startGestureDetection();
            }
            mWasTrackingFace = true;

        } else { // Did not detect any face
            Video.calcOpticalFlowPyrLK(
                    mLastEqualizedGray, mEqualizedGray, mLastFeatures,
                    mFeatures, mFeatureStatuses, mFeatureErrors);

            // Filter out features that are not found or have high
            // error.
            featuresList = new LinkedList<Point>(mFeatures.toList());
            final LinkedList<Byte> featureStatusesList =
                    new LinkedList<Byte>(mFeatureStatuses.toList());
            final LinkedList<Float> featureErrorsList =
                    new LinkedList<Float>(mFeatureErrors.toList());
            for (int i = 0; i < featuresList.size();) {
                if (featureStatusesList.get(i) == 0 ||
                        featureErrorsList.get(i) > MAX_FEATURE_ERROR) {
                    featuresList.remove(i);
                    featureStatusesList.remove(i);
                    featureErrorsList.remove(i);
                } else {
                    i++;
                }
            }
            if (featuresList.size() < MIN_FEATURES) {
                // The number of remaining features is too low; we have
                // probably lost the target completely.

                // Discard the remaining features.
                featuresList.clear();
                mFeatures.fromList(featuresList);

                mWasTrackingFace = false;
            } else {
                mFeatures.fromList(featuresList);
                updateGestureDetection();
            }
        }

        // Draw the current features.
        for (int i = 0; i< featuresList.size(); i++) {
            final Point p = featuresList.get(i);
            final Point pTrans = new Point(
                    mImageWidth - p.y,
                    p.x);
            Imgproc.circle(rgba, pTrans, 8, mFeatureColor);
        }

        // Swap the references to the current and previous images.
        final Mat swapEqualizedGray = mLastEqualizedGray;
        mLastEqualizedGray = mEqualizedGray;
        mEqualizedGray = swapEqualizedGray;

        // Swap the references to the current and previous features.
        final MatOfPoint2f swapFeatures = mLastFeatures;
        mLastFeatures = mFeatures;
        mFeatures = swapFeatures;

        // Mirror (horizontally flip) the preview.
        Core.flip(rgba, rgba, 1);

        return rgba;
    }

    private void startGestureDetection() {

        double[] featuresCenter = Core.mean(mFeatures).val;

        // Motion in x may indicate a shake of the head.
        mShakeHeadGesture.start(featuresCenter[0]);

        // Motion in y may indicate a nod of the head.
        mNodHeadGesture.start(featuresCenter[1]);
    }

    private void updateGestureDetection() {

        final double[] featuresCenter = Core.mean(mFeatures).val;

        // Motion in x may indicate a shake of the head.
        mShakeHeadGesture.update(featuresCenter[0]);
        final int shakeBackAndForthCount =
                mShakeHeadGesture.getBackAndForthCount();
        //Log.i(TAG, "shakeBackAndForthCount=" +
        //        shakeBackAndForthCount);
        final boolean shakingHead =
                (shakeBackAndForthCount >=
                        MIN_BACK_AND_FORTH_COUNT);

        // Motion in y may indicate a nod of the head.
        mNodHeadGesture.update(featuresCenter[1]);
        final int nodBackAndForthCount =
                mNodHeadGesture.getBackAndForthCount();
        //Log.i(TAG, "nodBackAndForthCount=" +
        //        nodBackAndForthCount);
        final boolean noddingHead =
                (nodBackAndForthCount >=
                        MIN_BACK_AND_FORTH_COUNT);

        if (shakingHead && noddingHead) {
            // The gesture is ambiguous. Ignore it.
            resetGestures();
        } else if (shakingHead) {
            mAudioTree.takeNoBranch();
            resetGestures();
        } else if (noddingHead) {
            mAudioTree.takeYesBranch();
            resetGestures();
        }
    }

    private void resetGestures() {
        if (mNodHeadGesture != null) {
            mNodHeadGesture.resetCounts();
        }
        if (mShakeHeadGesture != null) {
            mShakeHeadGesture.resetCounts();
        }
    }

    private void initFaceDetector() {
        try {
            // Load cascade file from application resources.

            InputStream is = getResources().openRawResource(
                    R.raw.lbpcascade_frontalface);
            File cascadeDir = getDir(
                    "cascade", Context.MODE_PRIVATE);
            File cascadeFile = new File(
                    cascadeDir, "lbpcascade_frontalface.xml");
            FileOutputStream os = new FileOutputStream(cascadeFile);

            byte[] buffer = new byte[4096];
            int bytesRead;
            while ((bytesRead = is.read(buffer)) != -1) {
                os.write(buffer, 0, bytesRead);
            }
            is.close();
            os.close();

            mFaceDetector = new CascadeClassifier(
                    cascadeFile.getAbsolutePath());
            if (mFaceDetector.empty()) {
                Log.e(TAG, "Failed to load cascade");
                finish();
            } else {
                Log.i(TAG, "Loaded cascade from " +
                        cascadeFile.getAbsolutePath());
            }

            cascadeDir.delete();

        } catch (IOException e) {
            e.printStackTrace();
            Log.e(TAG, "Failed to load cascade. Exception caught: "
                    + e);
            finish();
        }
    }
}
