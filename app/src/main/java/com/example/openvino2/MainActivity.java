package com.example.openvino2;

import androidx.appcompat.app.AppCompatActivity;
import androidx.annotation.NonNull;
import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.os.Build;
import android.view.View;
import android.view.Window;

import androidx.core.content.ContextCompat;

import android.widget.Toast;
import org.opencv.core.Rect;
import org.opencv.android.CameraActivity;
import org.opencv.android.CameraBridgeViewBase;
import org.opencv.android.CameraBridgeViewBase.CvCameraViewFrame;
import org.opencv.android.CameraBridgeViewBase.CvCameraViewListener2;
import org.opencv.android.OpenCVLoader;
import org.opencv.core.Core;
import org.opencv.objdetect.CascadeClassifier;
import org.opencv.core.Mat;
import org.opencv.core.MatOfRect;
import org.opencv.core.Point;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.intel.openvino.*;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;


public class MainActivity extends CameraActivity implements CvCameraViewListener2   {
    private void copyFiles() {
        String[] fileNames = {MODEL_BIN, MODEL_XML,LEYE_XML,REYE_XML,POSE_BIN,POSE_XML,GAZE_XML,GAZE_BIN, PLUGINS_XML};
        for (String fileName: fileNames) {
            String outputFilePath = modelDir + "/" + fileName;
            File outputFile = new File(outputFilePath);
            if (!outputFile.exists()) {
                try {
                    InputStream inputStream = getApplicationContext().getAssets().open(fileName);
                    OutputStream outputStream = new FileOutputStream(outputFilePath);
                    byte[] buffer = new byte[5120];
                    int length = inputStream.read(buffer);
                    while (length > 0) {
                        outputStream.write(buffer, 0, length);
                        length = inputStream.read(buffer);
                    }
                    outputStream.flush();
                    outputStream.close();
                    inputStream.close();
                } catch (Exception e) {
                    Log.e("CopyError", "Copying model has failed.");
                    System.exit(1);
                }
            }
        }
    }

    private void processNetwork() {
        // Set up camera listener.
        mOpenCvCameraView = (CameraBridgeViewBase) findViewById(R.id.CameraView);
        mOpenCvCameraView.setVisibility(CameraBridgeViewBase.VISIBLE);
        mOpenCvCameraView.setCvCameraViewListener(this);
        mOpenCvCameraView.setCameraIndex(1);
        mOpenCvCameraView.setCameraPermissionGranted();
        // Initialize model
        copyFiles();
        IECore core = new IECore(modelDir + "/" + PLUGINS_XML);
        CNNNetwork net = core.ReadNetwork(modelDir + "/" + MODEL_XML);

        Map<String, InputInfo> inputsInfo = net.getInputsInfo();
        inputName = new ArrayList<String>(inputsInfo.keySet()).get(0);
        InputInfo inputInfo = inputsInfo.get(inputName);
        inputInfo.getPreProcess().setResizeAlgorithm(ResizeAlgorithm.RESIZE_BILINEAR);
        inputInfo.setPrecision(Precision.U8);

        ExecutableNetwork executableNetwork = core.LoadNetwork(net, DEVICE_NAME);
        inferRequest = executableNetwork.CreateInferRequest();

        Map<String, Data> outputsInfo = net.getOutputsInfo();
        outputName = new ArrayList<>(outputsInfo.keySet()).get(0);
    }

    private float[] make_gaze(Blob leftEye , Blob rightEye , Blob angles){
        IECore core2 = new IECore(modelDir + "/" + PLUGINS_XML);
        CNNNetwork netGaze = null;
        ExecutableNetwork executableNetGaze = null;
        InferRequest inferRequestmake_gaze = null;
        float[] gaze_vector=null;

        try {
            netGaze = core2.ReadNetwork(modelDir + "/" + GAZE_XML);
            executableNetGaze = core2.LoadNetwork(netGaze, DEVICE_NAME);

            Map<String, InputInfo> inputsInfomake_gaze = netGaze.getInputsInfo();

            String inputNamemake_gaze1 = new ArrayList<>(inputsInfomake_gaze.keySet()).get(0);
            InputInfo inputInfomake_gaze1 = inputsInfomake_gaze.get(inputNamemake_gaze1);
            inputInfomake_gaze1.getPreProcess().setResizeAlgorithm(ResizeAlgorithm.RESIZE_BILINEAR);
            inputInfomake_gaze1.setPrecision(Precision.FP32);

            String inputNamemake_gaze2 = new ArrayList<>(inputsInfomake_gaze.keySet()).get(1);
            InputInfo inputInfomake_gaze2 = inputsInfomake_gaze.get(inputNamemake_gaze2);
            inputInfomake_gaze2.getPreProcess().setResizeAlgorithm(ResizeAlgorithm.RESIZE_BILINEAR);
            inputInfomake_gaze2.setPrecision(Precision.FP32);

            String inputNamemake_gaze3 = new ArrayList<>(inputsInfomake_gaze.keySet()).get(2);
            InputInfo inputInfomake_gaze3 = inputsInfomake_gaze.get(inputNamemake_gaze3);
            inputInfomake_gaze3.getPreProcess().setResizeAlgorithm(ResizeAlgorithm.RESIZE_BILINEAR);
            inputInfomake_gaze3.setPrecision(Precision.FP32);

            inferRequestmake_gaze = executableNetGaze.CreateInferRequest();
            inferRequestmake_gaze.SetBlob(inputNamemake_gaze1, leftEye);
            inferRequestmake_gaze.SetBlob(inputNamemake_gaze2, rightEye);
            inferRequestmake_gaze.SetBlob(inputNamemake_gaze3, angles);
            inferRequestmake_gaze.Infer();

            String outputName = "gaze_vector";
            Blob gazeblob = inferRequestmake_gaze.GetBlob(outputName);
            float [] gaze = new float[gazeblob.size()];
            gazeblob.rmap().get(gaze);
            gaze_vector = gaze;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return gaze_vector;
    }
    private float[] head_pose_angles(Mat image) {
        IECore core2 = new IECore(modelDir + "/" + PLUGINS_XML);

        CNNNetwork netHeadPose = core2.ReadNetwork(modelDir + "/" + POSE_XML);
        ExecutableNetwork executableNetHeadPose = core2.LoadNetwork(netHeadPose, DEVICE_NAME);

        Map<String, InputInfo> inputsInfoHeadPose = netHeadPose.getInputsInfo();
        String inputNameHeadPose = new ArrayList<>(inputsInfoHeadPose.keySet()).get(0);
        InputInfo inputInfoHeadPose = inputsInfoHeadPose.get(inputNameHeadPose);
        inputInfoHeadPose.getPreProcess().setResizeAlgorithm(ResizeAlgorithm.RESIZE_BILINEAR);
        inputInfoHeadPose.setPrecision(Precision.FP32);

        Mat headPoseResized = new Mat();
        Imgproc.resize(image, headPoseResized, new Size(60, 60));



        Blob headPoseBlob = new Blob(inputInfoHeadPose.getTensorDesc(), headPoseResized.dataAddr());
        InferRequest inferRequestHeadPose = executableNetHeadPose.CreateInferRequest();
        inferRequestHeadPose.SetBlob(inputNameHeadPose, headPoseBlob);
        inferRequestHeadPose.Infer();
        Map<String, Data> outputsInfoHeadPose = netHeadPose.getOutputsInfo();
        String outputNameYaw = new ArrayList<>(outputsInfoHeadPose.keySet()).get(0);
        String outputNamePitch = new ArrayList<>(outputsInfoHeadPose.keySet()).get(1);
        String outputNameRoll = new ArrayList<>(outputsInfoHeadPose.keySet()).get(2);

        float[] angles = new float[3];
        Blob yawBlob = inferRequestHeadPose.GetBlob(outputNameYaw);
        Blob pitchBlob = inferRequestHeadPose.GetBlob(outputNamePitch);
        Blob rollBlob = inferRequestHeadPose.GetBlob(outputNameRoll);


        float[] yaw = new float[yawBlob.size()];
        float[] pitch = new float[pitchBlob.size()];
        float[] roll = new float[rollBlob.size()];
        yawBlob.rmap().get(yaw);
        pitchBlob.rmap().get(pitch);
        rollBlob.rmap().get(roll);
        angles[0] = yaw[0];
        angles[1] = pitch[0];
        angles[2] = roll[0];

        return angles;

    }
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
            getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        }

        try{
            System.loadLibrary(OPENCV_LIBRARY_NAME);
            System.loadLibrary(IECore.NATIVE_LIBRARY_NAME);

        } catch (UnsatisfiedLinkError e) {
            Log.e("UnsatisfiedLinkError",
                    "Failed to load native OpenVINO libraries\n" + e.toString());
            System.exit(1);
        }
        modelDir = this.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath();
        if(checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.CAMERA}, 0);
        } else {
            processNetwork();
        }

    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (grantResults.length > 0 && grantResults[0] != PackageManager.PERMISSION_GRANTED) {
            Log.e("PermissionError", "The application can't work without camera permissions");
            System.exit(1);
        }
        processNetwork();
    }

    @Override
    public void onResume() {
        super.onResume();
        mOpenCvCameraView.enableView();
    }

    @Override
    public void onCameraViewStarted(int width, int height) {}

    @Override
    public void onCameraViewStopped() {}

    @Override
    public Mat onCameraFrame(CvCameraViewFrame inputFrame) {
        Mat frame = inputFrame.rgba();
        Mat frameBGR = new Mat();
        Imgproc.cvtColor(frame, frameBGR, Imgproc.COLOR_RGBA2RGB);
        int[] dimsArr = {1, frameBGR.channels(), frameBGR.height(), frameBGR.width()};
        TensorDesc tDesc = new TensorDesc(Precision.U8, dimsArr, Layout.NHWC);
        Blob imgBlob = new Blob(tDesc, frameBGR.dataAddr());
        inferRequest.SetBlob(inputName, imgBlob);
        inferRequest.Infer();
        Blob outputBlob = inferRequest.GetBlob(outputName);
        float[] scores = new float[outputBlob.size()];
        outputBlob.rmap().get(scores);
        int numDetections = outputBlob.size() / 7;

        float xx=0,yy=0;

        CascadeClassifier leye = new CascadeClassifier();
        leye.load(modelDir + "/" + LEYE_XML);

        CascadeClassifier reye = new CascadeClassifier();
        reye.load(modelDir + "/" + REYE_XML);

        Mat grayMat = new Mat();
        Imgproc.cvtColor(frameBGR,grayMat,Imgproc.COLOR_BGR2GRAY);

        float[] gaze_vector;
        String Direction = "";
        int confidentDetections = 0;
        for (int i = 0; i < numDetections; i++) {
            float confidence = scores[i * 7 + 2];
            if (confidence > CONFIDENCE_THRESHOLD) {
                float xmin = scores[i * 7 + 3] * frameBGR.cols();
                float ymin = scores[i * 7 + 4] * frameBGR.rows();
                float xmax = scores[i * 7 + 5] * frameBGR.cols();
                float ymax = scores[i * 7 + 6] * frameBGR.rows();
                Imgproc.rectangle(frame, new Point(xmin, ymin), new Point(xmax, ymax), new Scalar(0, 255, 0), 6);
                confidentDetections++;
                int x = (int) xmin;
                int y = (int) ymin;
                int width = (int) (xmax - xmin);
                int height = (int) (ymax - ymin);

                if (x >= 0 && y >= 0 && x + width <= grayMat.cols() && y + height <= grayMat.rows()) {
                    Blob rightEyeBlob = null;
                    Blob leftEyeBlob = null;
                    Blob anglesBlob = null;
                    // Face Box in Gray
                    Rect faceROI = new Rect(x, y, width, height);
                    Mat faceGrayMat = new Mat(grayMat, faceROI);


                    // EYE detections
                    MatOfRect leyes = new MatOfRect();
                    leye.detectMultiScale(faceGrayMat, leyes,1.3,5);
                    MatOfRect reyes = new MatOfRect();
                    reye.detectMultiScale(faceGrayMat, reyes,1.3,5);



                    for (Rect eyeRect : leyes.toArray()) {
                        Point eyeRectTL = new Point(eyeRect.x + x, eyeRect.y + y);
                        Point eyeRectBR = new Point(eyeRect.x + x + eyeRect.width, eyeRect.y + y + eyeRect.height);
                        Imgproc.rectangle(frame, eyeRectTL, eyeRectBR, new Scalar(255, 0, 0), 2);

                        Rect leyeROI = new Rect(eyeRectTL,eyeRectBR);
                        Mat leyemat = new Mat(frame,leyeROI);
                        Mat resizedRightEye = new Mat();
                        Imgproc.resize(leyemat, resizedRightEye, new Size(60, 60));
                        Mat bgrRightEye = new Mat();
                        Imgproc.cvtColor(resizedRightEye, bgrRightEye, Imgproc.COLOR_RGBA2BGR);

                        int[] dimsArr2 = {1, bgrRightEye.channels(), bgrRightEye.height(), bgrRightEye.width()};
                        TensorDesc tDesc2 = new TensorDesc(Precision.FP32, dimsArr2, Layout.NHWC);
                        leftEyeBlob = new Blob(tDesc2, bgrRightEye.dataAddr());


                    }
                    for (Rect eyeRect : reyes.toArray()) {
                        Point eyeRectTL = new Point(eyeRect.x + x, eyeRect.y + y);
                        Point eyeRectBR = new Point(eyeRect.x + x + eyeRect.width, eyeRect.y + y + eyeRect.height);
                        Imgproc.rectangle(frame, eyeRectTL, eyeRectBR, new Scalar(255, 0, 0), 2);


                        Rect reyeROI = new Rect(eyeRectTL,eyeRectBR);
                        Mat reyemat = new Mat(frame,reyeROI);
                        Mat resizedRightEye = new Mat();
                        Imgproc.resize(reyemat, resizedRightEye, new Size(60, 60));
                        Mat bgrRightEye = new Mat();
                        Imgproc.cvtColor(resizedRightEye, bgrRightEye, Imgproc.COLOR_RGBA2BGR);

                        int[] dimsArr2 = {1, bgrRightEye.channels(), bgrRightEye.height(), bgrRightEye.width()};
                        TensorDesc tDesc2 = new TensorDesc(Precision.FP32, dimsArr2, Layout.NHWC);
                        rightEyeBlob = new Blob(tDesc2, bgrRightEye.dataAddr());

                    }
                    // HEad POSition
                    float[] headPoseAngles = head_pose_angles(faceGrayMat);
                    float roll = headPoseAngles[2];
                    float rollRadians = (float) Math.toRadians(roll);

                    float vcos = (float) Math.cos(rollRadians);
                    float vsin = (float) Math.sin(rollRadians);


                    int[] dimsArr2 = {1,1,3,1};
                    TensorDesc tDesc2 = new TensorDesc(Precision.FP32, dimsArr2, Layout.NHWC);
                    anglesBlob = new Blob(tDesc2, headPoseAngles);


                    gaze_vector = make_gaze(leftEyeBlob,rightEyeBlob,anglesBlob);
                    try{
                        float gazeMagnitude = 0;
                        for (float value : gaze_vector) {
                            gazeMagnitude += value * value;
                        }
                        gazeMagnitude = (float) Math.sqrt(gazeMagnitude);


                        for (int j = 0; j < gaze_vector.length; j++) {
                            gaze_vector[j] /= gazeMagnitude;
                        }
                         xx = gaze_vector[0] * vcos + gaze_vector[1] * vsin;
                         yy = gaze_vector[0] * vsin + gaze_vector[1] * vcos;
                         Log.e("Direction",Direction);
                         System.out.println(gaze_vector[0]);
                         System.out.println(gaze_vector[1]);
                         Direction = headPoseDirection(xx,yy);
                         Log.e("Direction",Direction);
                    }catch (Exception e) {
                        e.printStackTrace();
                    }

                }

            }
        }

        Imgproc.putText(frame, String.valueOf(confidentDetections), new Point(10, 40),
                Imgproc.FONT_HERSHEY_COMPLEX, 1.8, new Scalar(0, 255, 0), 6);

        Imgproc.putText(frame, Direction, new Point(70, 60),
                Imgproc.FONT_HERSHEY_COMPLEX, 2.1, new Scalar(0, 255, 0), 4);

        return frame;
    }
    public String headPoseDirection(float xx, float yy) {
        String direction;
        System.out.println(xx);
        System.out.println(yy);
        if (xx > 0.05) {
            if (yy > 0.03) {
                direction = "Up-left";
            } else if (yy < 0.03) {
                direction = "Down-left";
            } else {
                direction = "left";
            }
        } else if (xx < -0.03) {
            if (yy > 0.03) {
                direction = "Up-right";
            } else if (yy < -0.03) {
                direction = "Down-right";
            } else {
                direction = "right";
            }
        } else if (yy > 0.03) {
            direction = "Up";
        } else if (yy < -0.03) {
            direction = "Down";
        } else {
            direction = "UP";
        }

        return direction;
    }
    private CameraBridgeViewBase mOpenCvCameraView;
    private InferRequest inferRequest;
    private String inputName;
    private String outputName;
    private String modelDir;
    public static final double CONFIDENCE_THRESHOLD = 0.5;
    public static final String OPENCV_LIBRARY_NAME = "opencv_java4";
    public static final String PLUGINS_XML = "plugins.xml";
    public static final String MODEL_XML = "face-detection-adas-0001.xml";
    public static final String MODEL_BIN = "face-detection-adas-0001.bin";
    public static final String POSE_XML = "head-pose-estimation-adas-0001.xml";
    public static final String POSE_BIN = "head-pose-estimation-adas-0001.bin";
    public static final String GAZE_XML = "gaze-estimation-adas-0002.xml";
    public static final String GAZE_BIN = "gaze-estimation-adas-0002.bin";
    public static final String LEYE_XML = "haarcascade_lefteye_2splits.xml";
    public static final String REYE_XML = "haarcascade_righteye_2splits.xml";
    public static final String DEVICE_NAME = "CPU";
}