#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import CompressedImage
from ultralytics import YOLO

class VehicleDetector:
    def __init__(self):
        
        rospy.init_node('vehicle_detection_node', anonymous=True)
        
        self.model = YOLO('yolov8n.pt')
        
        self.image_topic = "/hikcamera/image_2/compressed"
        self.image_sub = rospy.Subscriber(self.image_topic, CompressedImage, self.image_callback)
        
        self.total_frames = 0
        self.vehicle_count = 0
        
        self.video_writer = None
        rospy.loginfo("✅ 车辆检测节点已启动！")

    def image_callback(self, data):
        try:
           
            np_arr = np.frombuffer(data.data, np.uint8)
            cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
           
            if self.video_writer is None:
                h, w = cv_image.shape[:2]
                self.video_writer = cv2.VideoWriter(
                    "detection_result.mp4",
                    cv2.VideoWriter_fourcc(*'mp4v'),
                    10,  
                    (w, h)
                )
        except Exception as e:
            rospy.logerr(f"❌ 图像转换失败: {e}")
            return

        results = self.model(cv_image, classes=[2,3,5,7])
        current_vehicles = 0
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
             
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()
                cls = box.cls[0].item()
                cls_name = self.model.names[int(cls)]
                
               
                cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(cv_image, f"{cls_name} {conf:.2f}", (x1, y1-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                current_vehicles += 1

        # 绘制统计信息
        self.total_frames += 1
        self.vehicle_count += current_vehicles
        cv2.putText(cv_image, f"总帧数: {self.total_frames} | 当前车辆数: {current_vehicles}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
   
        cv2.imshow("Vehicle Detection", cv_image)
        cv2.waitKey(1)
      
        self.video_writer.write(cv_image)
       
        rospy.loginfo(f"📸 第{self.total_frames}帧：检测到{current_vehicles}辆车")

    def run(self):
      
        rospy.spin()
       
        cv2.destroyAllWindows()
        if self.video_writer is not None:
            self.video_writer.release()
            rospy.loginfo("📹 检测结果已保存到 detection_result.mp4")

if __name__ == '__main__':
    try:

        import subprocess
        subprocess.call(["pip", "install", "--user", "ultralytics", "numpy", "opencv-python"])
     
        detector = VehicleDetector()
        detector.run()
    except rospy.ROSInterruptException:
   
        cv2.destroyAllWindows()
        rospy.loginfo("🛑 检测节点已停止")
    except Exception as e:

        rospy.logerr(f"❌ 节点启动失败: {e}")
        cv2.destroyAllWindows()
