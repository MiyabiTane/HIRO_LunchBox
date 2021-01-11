#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from jsk_recognition_msgs.msg import RectArray
from jsk_recognition_msgs.msg import LineArray
from jsk_recognition_msgs.msg import Line
from std_msgs.msg import Float32
from cv_bridge import CvBridge

from copy import deepcopy
import cv2
import numpy as np
import math
TH = 200

class ImageProcessing:
    def __init__(self):
        self.flag = False
        self.cv_image = None
        self.output_img = None
        self.rects_info = None
        self.header = None
        self.pub_info_list = None
        self.lbox_y = None
        self.max_size = 0
        self.bridge = CvBridge()

        self.pub = rospy.Publisher("/result_of_imageprocessing", LineArray, queue_size=1)

        rospy.Subscriber("/coral_rects_info", RectArray, self.coral_cb)
        rospy.Subscriber("/head_camera/rgb/image_raw", Image, self.image_cb)
        rospy.Subscriber("/lunchbox_2D_y", Float32, self.pos_cb)
        
    def image_cb(self, msg):
        if self.flag and self.lbox_y:
            print("Img Called")
            self.cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            self.output_img = deepcopy(self.cv_image)
            self.get_foods_rects()
            self.publish_result()
            self.flag = False
            self.rects_info = None
            self.output_img = None
            self.lbox_y = None

    def coral_cb(self, msg):
        if not self.rects_info:
            print("Coral Called")
            self.rects_info = msg.rects
            self.header = msg.header
            self.pub_info_list = [[]] * len(self.rects_info)
            # draw coral result
            self.output_img = deepcopy(self.cv_image)
            self.max_size = 0
            for rect in self.rects_info:
                self.max_size = max(rect.width * rect.height, self.max_size)
                cv2.rectangle(self.output_img, (rect.x, rect.y), (rect.x + rect.width, rect.y + rect.height), (255,0,0))
                # print("center-coords {} {}".format(rect.x+rect.width/2, rect.y+ rect.height/2))
            self.flag = True

    def pos_cb(self, msg):
        if not self.lbox_y:
            print("Position Called")
            self.lbox_y = msg.data

    def get_foods_rects(self):
        # self.cv_image = cv2.imread("/home/tork/Desktop/images/output_color.png")
        black_img = deepcopy(self.cv_image)
        # draw white plate black
        black_img[np.where(black_img[:,:,0] > TH) or np.where(black_img[:,:,1] > TH) or np.where(black_img[:,:,2] > TH)] = 0
        img_gray = cv2.cvtColor(black_img, cv2.COLOR_BGR2GRAY)
        # draw others black
        _thre, bw_img = cv2.threshold(img_gray, 1, 255, cv2.THRESH_BINARY)
        cv2.imwrite("/home/tork/Desktop/images/output_binary.png", bw_img)
        # get contours
        # if opencv version is latest, _, contours, _hierarchy -> contours, _hierarchy
        contours, _hierarchy = cv2.findContours(bw_img ,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        boxes_cand = []
        max_foods_size = self.max_size * 2
        for cnt in contours:
            #remove too small objects and too big object
            if 100 < cv2.contourArea(cnt) < max_foods_size:
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                boxes_cand.append(np.array(box))
        
        for i, rect in enumerate(self.rects_info):
            for box in boxes_cand:
                bcenter_x = np.mean(box[:, 0])
                bcenter_y = np.mean(box[:, 1])
                if rect.x <= bcenter_x <= rect.x + rect.width:
                    if rect.y <= bcenter_y <= rect.y + rect.height:
                        x_sorted = (deepcopy(box)).tolist()
                        x_sorted.sort(key=lambda x:x[0])
                        left_lst = x_sorted[:2]
                        right_lst = x_sorted[2:]
                        left_lst.sort(key=lambda x:x[1])
                        right_lst.sort(key=lambda x:x[1])
                        ltop = left_lst[0]
                        lbottom = left_lst[1]
                        rbottom = right_lst[1]
                        width =  math.sqrt((rbottom[0] - lbottom[0])**2 + (rbottom[1] - lbottom[1])**2)
                        length = math.sqrt((lbottom[0] - ltop[0])**2 + (lbottom[1] - ltop[1])**2)
                        len_x =  rbottom[0] - lbottom[0]
                        len_y = lbottom[1] - rbottom[1]
                        # adjustment of perspective
                        diff_y = self.lbox_y - (rect.y + rect.height / 2)
                        width += diff_y * 4 / 100
                        length += diff_y * 4 / 100
                        if width > rect.width * 2:
                            continue
                        # visualize result
                        cv2.line(self.output_img, (ltop[0], ltop[1]), (lbottom[0], lbottom[1]), (0, 255, 0), thickness=2)
                        cv2.line(self.output_img, (lbottom[0], lbottom[1]), (rbottom[0], rbottom[1]), (255, 0, 0), thickness=2)
                        # catch the longer edge
                        if float(width) / length >= 1.5:
                            if bcenter_y > 260:
                                angular = math.atan(float(len_y) / len_x) + math.pi / 2
                            else:
                                angular = math.atan(float(len_y) / len_x) - math.pi / 2
                        elif float(length) / width >= 1.5:
                            angular = math.atan(float(len_y) / len_x)
                            width, length = length, width
                        else:
                            angular = 0
                        self.pub_info_list[i] = (angular, angular, width, length)
        
    def publish_result(self):
        pub_msgs = LineArray()
        pub_msgs.header = self.header
        for info, rect_origin in zip(self.pub_info_list, self.rects_info):
            pub_msg = Line()
            if info:
                pub_msg.x1 = info[0]
                pub_msg.y1 = info[1]
                pub_msg.x2 = info[2]
                pub_msg.y2 = info[3]
            else:
                pub_msg.x1 = 0
                pub_msg.y1 = 0
                pub_msg.x2 = 0  # rect_origin.width
                pub_msg.y2 = 0  # rect_origin.height
            pub_msgs.lines.append(pub_msg)
        # visualize result
        # cv2.imwrite("/home/tork/Desktop/images/output.png", self.output_img)
        self.pub.publish(pub_msgs)


if __name__ == '__main__':
    rospy.init_node("get_food_rects")
    img_pro = ImageProcessing()
    rospy.spin()


