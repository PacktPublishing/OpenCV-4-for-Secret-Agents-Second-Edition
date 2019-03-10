using UnityEngine;
using System.Collections;
using System.Collections.Generic;

using OpenCVForUnity.CoreModule;
using OpenCVForUnity.ImgprocModule;
using OpenCVForUnity.UnityUtils;


namespace com.nummist.rollingball {

    [RequireComponent (typeof(Camera))]
    public sealed class DetectAndSimulate : MonoBehaviour {

        struct Circle {

            public Vector2 screenPosition;
            public float screenDiameter;
            public Vector3 worldPosition;

            public Circle(Vector2 screenPosition,
                          float screenDiameter,
                          Vector3 worldPosition) {
                this.screenPosition = screenPosition;
                this.screenDiameter = screenDiameter;
                this.worldPosition = worldPosition;
            }
        }

        struct Line {
            
            public Vector2 screenPoint0;
            public Vector2 screenPoint1;
            public Vector3 worldPoint0;
            public Vector3 worldPoint1;
            
            public Line(Vector2 screenPoint0,
                        Vector2 screenPoint1,
                        Vector3 worldPoint0,
                        Vector3 worldPoint1) {
                this.screenPoint0 = screenPoint0;
                this.screenPoint1 = screenPoint1;
                this.worldPoint0 = worldPoint0;
                this.worldPoint1 = worldPoint1;
            }
        }

        [SerializeField] bool useFrontFacingCamera = false;
        [SerializeField] int preferredCaptureWidth = 640;
        [SerializeField] int preferredCaptureHeight = 480;
        [SerializeField] int preferredFPS = 15;

        [SerializeField] Renderer videoRenderer;

        [SerializeField] Material drawPreviewMaterial;

        [SerializeField] float gravityScale = 8f;

        [SerializeField] GameObject simulatedCirclePrefab;
        [SerializeField] GameObject simulatedLinePrefab;

        [SerializeField] int buttonFontSize = 24;

        Camera _camera;

        WebCamTexture webCamTexture;
        Color32[] colors;
        Mat rgbaMat;
        Mat grayMat;
        Mat cannyMat;

        float screenWidth;
        float screenHeight;
        float screenPixelsPerImagePixel;
        float screenPixelsYOffset;

        float raycastDistance;
        float lineThickness;
        UnityEngine.Rect buttonRect;

        Mat houghCircles;
        List<Circle> circles = new List<Circle>();

        Mat houghLines;
        List<Line> lines = new List<Line>();

        Gyroscope gyro;
        float gravityMagnitude;

        List<GameObject> simulatedObjects =
                new List<GameObject>();
        bool simulating {
            get {
                return simulatedObjects.Count > 0;
            }
        }

        void Start() {

            // Cache the reference to the game world's
            // camera.
            _camera = GetComponent<Camera>();

            houghCircles = new Mat();
            houghLines = new Mat();

            gyro = Input.gyro;
            gravityMagnitude = Physics.gravity.magnitude *
                               gravityScale;

#if UNITY_EDITOR
            useFrontFacingCamera = true;
#endif

            // Try to find a (physical) camera that faces
            // the required direction.
            WebCamDevice[] devices = WebCamTexture.devices;
            int numDevices = devices.Length;
            for (int i = 0; i < numDevices; i++) {
                WebCamDevice device = devices[i];
                if (device.isFrontFacing ==
                            useFrontFacingCamera) {
                    string name = device.name;
                    Debug.Log("Selecting camera with " +
                              "index " + i + " and name " +
                              name);
                    webCamTexture = new WebCamTexture(
                            name, preferredCaptureWidth,
                            preferredCaptureHeight,
                            preferredFPS);
                    break;
                }
            }

            if (webCamTexture == null) {
                // No camera faces the required direction.
                // Give up.
                Debug.LogError("No suitable camera found");
                Destroy(this);
                return;
            }

            // Ask the camera to start capturing.
            webCamTexture.Play();

            if (gyro != null) {
                gyro.enabled = true;
            }

            // Wait for the camera to start capturing.
            // Then, initialize everything else.
            StartCoroutine(Init());
        }

        IEnumerator Init() {
            
            // Wait for the camera to start capturing.
            while (!webCamTexture.didUpdateThisFrame) {
                yield return null;
            }
            
            int captureWidth = webCamTexture.width;
            int captureHeight = webCamTexture.height;
            float captureDiagonal = Mathf.Sqrt(
                    captureWidth * captureWidth +
                    captureHeight * captureHeight);
            Debug.Log("Started capturing frames at " +
                      captureWidth + "x" + captureHeight);
            
            colors = new Color32[
                    captureWidth * captureHeight];
            
            rgbaMat = new Mat(captureHeight, captureWidth,
                              CvType.CV_8UC4);
            grayMat = new Mat(captureHeight, captureWidth,
                              CvType.CV_8UC1);
            cannyMat = new Mat(captureHeight, captureWidth,
                               CvType.CV_8UC1);

            transform.localPosition =
                    new Vector3(0f, 0f, -captureWidth);
            _camera.nearClipPlane = 1;
            _camera.farClipPlane = captureWidth + 1;
            _camera.orthographicSize =
                    0.5f * captureDiagonal;
            raycastDistance = 0.5f * captureWidth;

            Transform videoRendererTransform =
                    videoRenderer.transform;
            videoRendererTransform.localPosition =
                    new Vector3(captureWidth / 2,
                                -captureHeight / 2, 0f);
            videoRendererTransform.localScale =
                    new Vector3(captureWidth,
                                captureHeight, 1f);

            videoRenderer.material.mainTexture =
                    webCamTexture;

            // Calculate the conversion factors between
            // image and screen coordinates.
            // Note that the image is landscape but the
            // screen is portrait.
            screenWidth = (float)Screen.width;
            screenHeight = (float)Screen.height;
            screenPixelsPerImagePixel =
                    screenWidth / captureHeight;
            screenPixelsYOffset =
                    0.5f * (screenHeight - (screenWidth *
                    captureWidth / captureHeight));

            lineThickness = 0.01f * screenWidth;

            buttonRect = new UnityEngine.Rect(
                    0.4f * screenWidth,
                    0.75f * screenHeight,
                    0.2f * screenWidth,
                    0.1f * screenHeight);
        }

        void Update() {

            if (rgbaMat == null) {
                // Initialization is not yet complete.
                return;
            }

            if (gyro != null) {
                // Align the game-world gravity to real-world
                // gravity.
                Vector3 gravity = gyro.gravity;
                gravity.z = 0f;
                gravity = gravityMagnitude *
                          gravity.normalized;
                Physics.gravity = gravity;
            }

            if (!webCamTexture.didUpdateThisFrame) {
                // No new frame is ready.
                return;
            }

            if (simulating) {
                // No new detection results are needed.
                return;
            }

            // Convert the RGBA image to OpenCV's format using
            // a utility function from OpenCV for Unity.
            Utils.webCamTextureToMat(webCamTexture,
                                     rgbaMat, colors);

            // Convert the OpenCV image to gray and
            // equalize it.
            Imgproc.cvtColor(rgbaMat, grayMat,
                             Imgproc.COLOR_RGBA2GRAY);
            Imgproc.Canny(grayMat, cannyMat, 50.0, 200.0);

            UpdateCircles();
            UpdateLines();
        }

        void UpdateCircles() {

            // Detect blobs.
            Imgproc.HoughCircles(grayMat, houghCircles,
                                 Imgproc.HOUGH_GRADIENT, 2.0,
                                 10.0, 200.0, 150.0, 5, 60);

            //
            // Calculate the circles' screen coordinates
            // and world coordinates.
            //

            // Clear the previous coordinates.
            circles.Clear();

            // Iterate over the circles.
            int numHoughCircles = houghCircles.cols() *
                                  houghCircles.rows() *
                                  houghCircles.channels();
            if (numHoughCircles == 0)
            {
                return;
            }
            float[] houghCirclesArray = new float[numHoughCircles];
            houghCircles.get(0, 0, houghCirclesArray);
            for (int i = 0; i < numHoughCircles; i += 3) {

                // Convert circles' image coordinates to
                // screen coordinates.
                Vector2 screenPosition =
                        ConvertToScreenPosition(
                                houghCirclesArray[i],
                                houghCirclesArray[i + 1]);
                float screenDiameter =
                        houghCirclesArray[i + 2] *
                        screenPixelsPerImagePixel;

                // Convert screen coordinates to world
                // coordinates based on raycasting.
                Vector3 worldPosition =
                        ConvertToWorldPosition(
                                screenPosition);

                Circle circle = new Circle(
                        screenPosition, screenDiameter,
                        worldPosition);
                circles.Add(circle);
            }
        }

        void UpdateLines() {

            // Detect lines.
            Imgproc.HoughLinesP(cannyMat, houghLines, 1.0,
                                Mathf.PI / 180.0, 50,
                                50.0, 10.0);

            //
            // Calculate the lines' screen coordinates and
            // world coordinates.
            //

            // Clear the previous coordinates.
            lines.Clear();

            // Iterate over the lines.
            int numHoughLines = houghLines.cols() *
                                houghLines.rows() *
                                houghLines.channels();
            if (numHoughLines == 0)
            {
                return;
            }
            int[] houghLinesArray = new int[numHoughLines];
            houghLines.get(0, 0, houghLinesArray);
            for (int i = 0; i < numHoughLines; i += 4) {

                // Convert lines' image coordinates to
                // screen coordinates.
                Vector2 screenPoint0 =
                        ConvertToScreenPosition(
                                houghLinesArray[i],
                                houghLinesArray[i + 1]);
                Vector2 screenPoint1 =
                        ConvertToScreenPosition(
                                houghLinesArray[i + 2],
                                houghLinesArray[i + 3]);
                
                // Convert screen coordinates to world
                // coordinates based on raycasting.
                Vector3 worldPoint0 =
                        ConvertToWorldPosition(
                                screenPoint0);
                Vector3 worldPoint1 =
                        ConvertToWorldPosition(
                                screenPoint1);

                Line line = new Line(
                        screenPoint0, screenPoint1,
                        worldPoint0, worldPoint1);
                lines.Add(line);
            }
        }

        Vector2 ConvertToScreenPosition(float imageX,
                                        float imageY) {
            float screenX = screenWidth - imageY *
                            screenPixelsPerImagePixel;
            float screenY = screenHeight - imageX *
                            screenPixelsPerImagePixel -
                            screenPixelsYOffset;
            return new Vector2(screenX, screenY);
        }

        Vector3 ConvertToWorldPosition(
                Vector2 screenPosition) {
            Ray ray = _camera.ScreenPointToRay(
                    screenPosition);
            return ray.GetPoint(raycastDistance);
        }

        void OnPostRender() {
            if (!simulating) {
                DrawPreview();
            }
        }
        
        void DrawPreview() {

            // Draw 2D representations of the detected
            // circles and lines, if any.

            int numCircles = circles.Count;
            int numLines = lines.Count;
            if (numCircles < 1 && numLines < 1) {
                return;
            }
            
            GL.PushMatrix();
            if (drawPreviewMaterial != null) {
                drawPreviewMaterial.SetPass(0);
            }
            GL.LoadPixelMatrix();

            if (numCircles > 0) {
                // Draw the circles.
                GL.Begin(GL.QUADS);
                for (int i = 0; i < numCircles; i++) {
                    Circle circle = circles[i];
                    float centerX =
                            circle.screenPosition.x;
                    float centerY =
                            circle.screenPosition.y;
                    float radius =
                            0.5f * circle.screenDiameter;
                    float minX = centerX - radius;
                    float maxX = centerX + radius;
                    float minY = centerY - radius;
                    float maxY = centerY + radius;
                    GL.Vertex3(minX, minY, 0f);
                    GL.Vertex3(minX, maxY, 0f);
                    GL.Vertex3(maxX, maxY, 0f);
                    GL.Vertex3(maxX, minY, 0f);
                }
                GL.End();
            }

            if (numLines > 0) {
                // Draw the lines.
                GL.Begin(GL.LINES);
                for (int i = 0; i < numLines; i++) {
                    Line line = lines[i];
                    GL.Vertex(line.screenPoint0);
                    GL.Vertex(line.screenPoint1);
                }
                GL.End();
            }

            GL.PopMatrix();
        }

        void OnGUI() {
            GUI.skin.button.fontSize = buttonFontSize;
            if (simulating) {
                if (GUI.Button(buttonRect,
                               "Stop Simulation")) {
                    StopSimulation();
                }
            } else if (circles.Count > 0 || lines.Count > 0) {
                if (GUI.Button(buttonRect,
                               "Start Simulation")) {
                    StartSimulation();
                }
            }
        }
        
        void StartSimulation() {

            // Freeze the video background
            webCamTexture.Pause();

            // Create the circles' representation in the
            // physics simulation.
            int numCircles = circles.Count;
            for (int i = 0; i < numCircles; i++) {
                Circle circle = circles[i];
                GameObject simulatedCircle =
                        (GameObject)Instantiate(
                                simulatedCirclePrefab);
                Transform simulatedCircleTransform =
                        simulatedCircle.transform;
                simulatedCircleTransform.position =
                        circle.worldPosition;
                simulatedCircleTransform.localScale =
                        circle.screenDiameter *
                        Vector3.one;
                simulatedObjects.Add(simulatedCircle);
            }

            // Create the lines' representation in the
            // physics simulation.
            int numLines = lines.Count;
            for (int i = 0; i < numLines; i++) {
                Line line = lines[i];
                GameObject simulatedLine =
                        (GameObject)Instantiate(
                                simulatedLinePrefab);
                Transform simulatedLineTransform =
                        simulatedLine.transform;
                float angle = -Vector2.Angle(
                        Vector2.right, line.screenPoint1 -
                                line.screenPoint0);
                Vector3 worldPoint0 = line.worldPoint0;
                Vector3 worldPoint1 = line.worldPoint1;
                simulatedLineTransform.position =
                        0.5f * (worldPoint0 + worldPoint1);
                simulatedLineTransform.eulerAngles =
                        new Vector3(0f, 0f, angle);
                simulatedLineTransform.localScale =
                        new Vector3(
                                Vector3.Distance(
                                        worldPoint0,
                                        worldPoint1),
                                lineThickness,
                                lineThickness);
                simulatedObjects.Add(simulatedLine);
            }
        }

        void StopSimulation() {

            // Unfreeze the video background.
            webCamTexture.Play();

            // Destroy all objects in the physics simulation.
            int numSimulatedObjects =
                    simulatedObjects.Count;
            for (int i = 0; i < numSimulatedObjects; i++) {
                GameObject simulatedObject =
                        simulatedObjects[i];
                Destroy(simulatedObject);
            }
            simulatedObjects.Clear();
        }
        
        void OnDestroy() {
            if (webCamTexture != null) {
                webCamTexture.Stop();
            }
            if (gyro != null) {
                gyro.enabled = false;
            }
        }
    }
}
