#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import CompressedImage
from ultralytics import YOLO

class VehicleDetector:
    def __init__(self):
        # 初始化ROS节点
        rospy.init_node('vehicle_detection_node', anonymous=True)
        # 加载YOLOv8轻量级模型
        self.model = YOLO('yolov8n.pt')
        # 订阅压缩图像话题（你的rosbag实际话题）
        self.image_topic = "/hikcamera/image_2/compressed"
        self.image_sub = rospy.Subscriber(self.image_topic, CompressedImage, self.image_callback)
        # 统计变量
        self.total_frames = 0
        self.vehicle_count = 0
        # 可选：保存检测结果为视频（解决WSL窗口问题）
        self.video_writer = None
        rospy.loginfo("✅ 车辆检测节点已启动！")

    def image_callback(self, data):
        try:
            # 解压CompressedImage → OpenCV BGR图像
            np_arr = np.frombuffer(data.data, np.uint8)
            cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            # 初始化视频写入器（只在第一帧执行）
            if self.video_writer is None:
                h, w = cv_image.shape[:2]
                self.video_writer = cv2.VideoWriter(
                    "detection_result.mp4",
                    cv2.VideoWriter_fourcc(*'mp4v'),
                    10,  # 帧率
                    (w, h)
                )
        except Exception as e:
            rospy.logerr(f"❌ 图像转换失败: {e}")
            return

        # 车辆检测（只检测汽车/摩托/公交/卡车，对应YOLO类别ID：2,3,5,7）
        results = self.model(cv_image, classes=[2,3,5,7])
        current_vehicles = 0
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # 获取检测框、置信度、类别
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()
                cls = box.cls[0].item()
                cls_name = self.model.names[int(cls)]
                
                # 绘制检测框和标签
                cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(cv_image, f"{cls_name} {conf:.2f}", (x1, y1-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                current_vehicles += 1

        # 绘制统计信息
        self.total_frames += 1
        self.vehicle_count += current_vehicles
        cv2.putText(cv_image, f"总帧数: {self.total_frames} | 当前车辆数: {current_vehicles}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # 1. 尝试显示窗口（WSL可能弹不出，不影响）
        cv2.imshow("Vehicle Detection", cv_image)
        cv2.waitKey(1)
        # 2. 保存检测结果到视频文件（关键！解决WSL窗口问题）
        self.video_writer.write(cv_image)
        # 打印日志，证明检测正常运行
        rospy.loginfo(f"📸 第{self.total_frames}帧：检测到{current_vehicles}辆车")

    def run(self):
        # 保持节点运行
        rospy.spin()
        # 释放资源
        cv2.destroyAllWindows()
        if self.video_writer is not None:
            self.video_writer.release()
            rospy.loginfo("📹 检测结果已保存到 detection_result.mp4")

if __name__ == '__main__':
    try:
        # 自动安装依赖（第一次运行需要）
        import subprocess
        subprocess.call(["pip", "install", "--user", "ultralytics", "numpy", "opencv-python"])
        # 启动检测节点
        detector = VehicleDetector()
        detector.run()
    except rospy.ROSInterruptException:
        # 节点停止时清理资源
        cv2.destroyAllWindows()
        rospy.loginfo("🛑 检测节点已停止")
    except Exception as e:
        # 捕获其他错误
        rospy.logerr(f"❌ 节点启动失败: {e}")
        cv2.destroyAllWindows()