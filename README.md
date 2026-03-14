# AAE4011-25-26-Assignment-Github-Submission-



# AAE4011-Assignment 1-Q3: ROS-Based Vehicle Detection from Rosbag
Student Name: LongYiqi | Student ID: 23107894D | Date:14th March, 2026

## 1. Overview
This ROS package implements real-time vehicle detection for unmanned aerial systems (UAS) using YOLOv8 deep learning model. The pipeline processes compressed image streams from a given rosbag file, detects typical vehicle categories (cars, trucks, buses, motorcycles), and outputs detection results through terminal logs and video file saving (due to WSL2 GUI limitations, real-time window visualization is replaced by video recording).

## 2. Detection Method
I selected YOLOv8n (the nano version of YOLOv8) for this project due to the key advantages listed below:

- **Speed**: YOLOv8n achieves ultra-fast inference (29ms per frame in testing) with minimal computational resource consumption, making it ideal for real-time UAS applications with limited onboard computing power.
- **Accuracy-Efficiency Balance**: As the latest version of YOLO series, YOLOv8n maintains high detection accuracy for common vehicles while having a smaller model size (only a few MBs) compared to YOLOv5s.
- **Seamless ROS Integration**: The `ultralytics` library provides a user-friendly Python API for YOLOv8, which can be easily integrated with ROS `rospy` and `cv_bridge` for image stream processing.
- **Compressed Image Compatibility**: The pipeline is optimized to handle `sensor_msgs/CompressedImage` topics from rosbag, reducing network bandwidth usage in UAS scenarios.

## 3. Repository Structure
```
vehicle_detection/
├── CMakeLists.txt          # ROS build configuration (Python node installation)
├── package.xml             # ROS package dependencies declaration
├── README.md               # Project documentation (this file)
├── .gitignore              # Git ignore rules (exclude rosbag, video, logs)
├── launch/                 # ROS launch files
│   └── detection.launch    # Launch file for detector node
└── scripts/                # Core Python scripts
    └── detection_node.py   # MAIN DETECTOR (YOLOv8 + ROS image processing)
```

## 4. Prerequisites
- **Operating System**: Ubuntu 20.04 LTS (WSL2 on Windows 10/11)
- **ROS Distribution**: ROS Noetic Ninjemys
- **Python Version**: Python 3.8+
- **Key Libraries**:
  ```
  ultralytics >= 8.0.0      # YOLOv8 inference
  opencv-python >= 4.8.0    # Image processing and video saving
  numpy >= 1.24.0           # Array manipulation for image decoding
  rospy >= 1.15.0           # ROS Python interface
  cv_bridge >= 1.13.0       # ROS-OpenCV image conversion (optional)
  ```

## 5. How to Run
### Step 1: Setup ROS Workspace and Clone Repository
```bash
# Create catkin workspace (if not exists)
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws
catkin_make
source devel/setup.bash

# Clone repository to src directory
cd ~/catkin_ws/src
git clone [你的GitHub仓库链接] vehicle_detection
```

### Step 2: Install Dependencies
```bash
# Install system-level ROS dependencies
sudo apt update && sudo apt install -y python3-pip ros-noetic-cv-bridge

# Install Python libraries
pip3 install --user ultralytics numpy opencv-python
```

### Step 3: Build the ROS Package
```bash
cd ~/catkin_ws
# Build only vehicle_detection (skip LIO-SAM compilation errors)
catkin_make --only-pkg-with-deps vehicle_detection
source devel/setup.bash

# Add execute permission to detector script
chmod +x ~/catkin_ws/src/vehicle_detection/scripts/detection_node.py
```

### Step 4: Prepare Rosbag File
```bash
# Create data directory (optional)
mkdir -p ~/catkin_ws/src/vehicle_detection/data

# Copy rosbag to data directory (replace with your rosbag path)
cp "/mnt/c/Users/Tony Long/Documents/dataset/LIOSAM/2026-02-02-17-57-27.bag" ~/catkin_ws/src/vehicle_detection/data/
```

### Step 5: Launch the Detection Pipeline
#### Terminal 1: Start ROS Master
```bash
roscore
```

#### Terminal 2: Run YOLOv8 Detector Node
```bash
cd ~/catkin_ws
source devel/setup.bash
rosrun vehicle_detection detection_node.py
```

#### Terminal 3: Play Rosbag File (Slow Rate for Testing)
```bash
cd ~/catkin_ws/src/vehicle_detection/data/
# Play rosbag at 0.1x speed to observe detection logs clearly
rosbag play --rate 0.1 2026-02-02-17-57-27.bag
```

## 6. Sample Results

```
[sample result](https://github.com/tonylyq528/AAE4011-25-26-Assignment-Github-Submission-/blob/main/assets/image.png)```

### Detection Log Summary



### Key Detection Metrics
- **Supported Vehicle Classes**: Car (class ID 2), Motorcycle (class ID 3), Bus (class ID 5), Truck (class ID 7)
- **Image Resolution**: 512x640 pixels (compressed from original rosbag stream)
- **Bounding Box Visualization**: Green boxes with class name and confidence score (e.g., "car 0.92")
- **Statistical Output**: Total frames processed + real-time vehicle count per frame

## 7. Video Demonstration
Video Demo Link: [你的视频链接，如YouTube/OneDrive/Google Drive]

This video demonstrates:
1. The process of launching ROS Master, detector node and rosbag playback
2. Real-time terminal logs showing vehicle detection results
3. The generated `detection_result.mp4` video with bounding boxes and statistical overlays
4. Explanation of WSL2 GUI limitations and video-saving workaround

## 8. Reflection and Critical Analysis
### (a) What did I learn?
- **ROS Compressed Image Processing**: I mastered how to subscribe to and decode `sensor_msgs/CompressedImage` topics from rosbag, which is critical for bandwidth-efficient UAS applications (compared to uncompressed `sensor_msgs/Image`).
- **YOLOv8 Integration with ROS**: I learned to integrate pre-trained YOLOv8 models into ROS pipelines, including model loading, inference on OpenCV images, and result parsing (bounding boxes, confidence scores, class labels).
- **WSL2 ROS Environment Troubleshooting**: I gained practical experience in solving WSL2-specific issues (e.g., GUI visualization failure, X Server configuration, core dump errors) and implemented robust workarounds (video saving + terminal logs).
- **ROS Node Lifecycle Management**: I understood ROS node initialization, topic subscription, and resource cleanup (e.g., video writer release) to avoid memory leaks and crashes.

### (b) How was AI tools used?
- **Code Generation and Debugging**: I used AI tools (e.g., GitHub Copilot, ChatGPT) to generate initial ROS node templates, fix syntax/indentation errors, and optimize image decoding logic for compressed ROS messages.
- **YOLOv8 API Understanding**: AI tools helped me quickly learn the `ultralytics` library API, including class filtering, inference speed optimization, and result parsing.
- **Error Diagnosis**: AI tools assisted in analyzing "Aborted (core dumped)" errors and WSL2 GUI issues, providing targeted solutions (e.g., disabling `cv2.imshow()` and using video saving instead).

### (c) How to improve accuracy?
- **Dataset Fine-Tuning**: Fine-tune YOLOv8n on aerial vehicle datasets (e.g., UA-DETRAC, VisDrone) to adapt to UAS-specific viewing angles and small vehicle sizes.
- **Data Augmentation**: Apply real-time augmentation (e.g., brightness adjustment, rotation, scaling) during inference to improve robustness against varying lighting and weather conditions.
- **Multi-Scale Detection**: Modify YOLOv8 input resolution dynamically to detect both large and small vehicles more effectively.
- **Post-Processing Optimization**: Implement Non-Maximum Suppression (NMS) with adaptive thresholds to reduce false positives and duplicate detections.

### (d) Real-world challenges
- **Onboard Computing Constraints**: UAS has limited CPU/GPU resources, requiring model quantization (e.g., INT8) to reduce inference latency and power consumption.
- **Environmental Factors**: Outdoor conditions (e.g., rain, fog, shadows) can degrade image quality and detection accuracy, requiring pre-processing (e.g., contrast enhancement, dehazing).
- **Network Latency**: In real UAS scenarios, wireless image transmission introduces latency, requiring edge computing (onboard detection) instead of cloud processing.
- **Dynamic Vehicle Motion**: Fast-moving vehicles may cause motion blur, requiring motion compensation or frame interpolation to maintain detection accuracy.
```

---

