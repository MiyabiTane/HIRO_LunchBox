#!/usr/bin/env python

import cv2
import numpy as np
from copy import deepcopy

TH = 50
X_OFFSET = -5
Y_OFFSET = -18
EXTENTION = 0
TH2 = 15
TH3 = 10
EXTENTION2 = 10

class Point:
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

class MSG:
    def __init__(self):
        # input
        self.before_img = cv2.imread("before.png")
        self.after_img = cv2.imread("after.png")
        self.empty_img = cv2.imread("empty.png")
        self.ltop = Point(202.839, 260.531)
        self.lbottom = Point(194.532, 336.66)
        self.rtop = Point(265.374, 259.599)
        self.rbottom = Point(262.358, 335.562)
        self.goal = Point(x=0)

class VisualFeedback:

    def __init__(self):
        self.before_img = None
        self.after_img = None
        self.output_img = None
        self.empty_img = None
        self.stamp = None
        self.pub_msg = None
        self.count = 0 #for visualize
        self.lt_x = None; self.lt_y = None; self.lb_x = None; self.lb_y = None
        self.rt_x = None; self.rt_y = None; self.rb_x = None; self.rb_y = None
        # to check the result of pulling over
        self.pos_x = None; self.pos_y = None
        self.width = None; self.height = None
        #for debug visualize
        self.vis_img = None
        self.vis2_img = None


    def status_cb(self, msg):
        # print("Called Lunchbox status")
        self.empty_img = msg.empty_img
        self.before_img = msg.before_img
        self.after_img = msg.after_img
        before = deepcopy(self.before_img)
        after = deepcopy(self.after_img)
        # cv2.imwrite("output_before" + str(self.count) + ".png", self.before_img)
        # cv2.imwrite("output_after" + str(self.count) + ".png", self.after_img)
        self.lt_x = msg.ltop.x; self.lt_y = msg.ltop.y; self.lb_x = msg.lbottom.x; self.lb_y = msg.lbottom.y
        self.rt_x = msg.rtop.x; self.rt_y = msg.rtop.y; self.rb_x = msg.rbottom.x; self.rb_y = msg.rbottom.y
        self.lt_x += X_OFFSET; self.lb_x += X_OFFSET; self.rt_x += X_OFFSET; self.rb_x += X_OFFSET
        self.lt_y += Y_OFFSET; self.lb_y += Y_OFFSET; self.rt_y += Y_OFFSET; self.rb_y += Y_OFFSET
        if msg.goal.x == 0:
            self.publish_info()
        else:
            self.publish_info(restrict=True, goal_x=msg.goal.x, goal_y=msg.goal.y)
        self.count += 1


    def get_diff_img(self, before_img, after_img, k_size=3):
        im_diff = before_img.astype(int) - after_img.astype(int)
        im_diff_abs = np.abs(im_diff)
        im_diff_img = im_diff_abs.astype(np.uint8)
        im_diff_img[np.where(im_diff_abs[:,:,0] < TH) and np.where(im_diff_abs[:,:,1] < TH) and np.where(im_diff_abs[:,:,2] < TH)] = [0, 0, 0]
        img_gray = cv2.cvtColor(im_diff_img, cv2.COLOR_BGR2GRAY)
        _, img_binary = cv2.threshold(img_gray, 1, 255, cv2.THRESH_BINARY)
        # remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(k_size,k_size))
        img_del_noise = cv2.morphologyEx(img_binary, cv2.MORPH_OPEN, kernel)
        img_closing = cv2.morphologyEx(img_del_noise, cv2.MORPH_CLOSE, kernel)
        return img_closing, img_binary
    
    def ignore_extra_space(self, diff_img, goal_x, goal_y):
        start_x = self.pos_x; start_y = self.pos_y
        width = self.width; height = self.height
        print("start_x {}, goal_x {}, start_y {}, goal_y {}".format(start_x, start_y, goal_x, goal_y))
        print("width {}, height {}".format(width, height))
        H, W = diff_img.shape
        restrict_img = np.zeros((H, W))
        # range 1
        x1_1 = max(0, int(start_x - (width + EXTENTION2) / 2))
        x1_2 = min(W, int(start_x + (width + EXTENTION2) / 2))
        y1_1 = max(0, int(min(start_y, goal_y) - (height + EXTENTION2) / 2))
        y1_2 = min(H, int(max(start_y, goal_y) + (height + EXTENTION2) / 2))
        keep_img1, _ = diff_img[y1_1: y1_2, x1_1: x1_2]
        cv2.rectangle(self.vis_img, (x1_1, y1_1), (x1_2, y1_2), (255, 0, 0))
        # range 2
        x2_1 = max(0, int(min(start_x, goal_x) - (width + EXTENTION2) / 2))
        x2_2 = min(W, int(max(start_x, goal_x) + (width + EXTENTION2) / 2))
        y2_1 = max(0, int(goal_y - (height + EXTENTION2) / 2))
        y2_2 = min(H, int(goal_y + (height + EXTENTION2) / 2))
        keep_img2, _ = diff_img[y2_1: y2_2, x2_1: x2_2]
        cv2.rectangle(self.vis_img, (x2_1, y2_1), (x2_2, y2_2), (255, 0, 0))
        # make restricted img
        restrict_img[y1_1: y1_2, x1_1: x1_2] = keep_img1
        restrict_img[y2_1: y2_2, x2_1: x2_2] = keep_img2
        restrict_img = restrict_img.astype(np.uint8)
        # cv2.imwrite("/home/tanemoto/Desktop/images/diff_restrict_" + str(self.count) + ".png", restrict_img)
        return restrict_img

    def get_food_info(self, diff_img):
        where = np.where(diff_img != 0)
        if len(where[0]) < 30:
            return None, None, None, None
        contours, _hierarchy = cv2.findContours(diff_img ,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        max_size = 0
        # box = None
        if len(contours) == 0:
            return None, None, None, None
        for cnt in contours:
            if max_size < cv2.contourArea(cnt):
                max_size = cv2.contourArea(cnt)
                # rect = cv2.minAreaRect(cnt)
                # box = cv2.boxPoints(rect)
                # box = np.int0(box)
                x, y, w, h = cv2.boundingRect(cnt)
        # print("BOX: {}".format(box))
        cv2.imwrite("diff_" + str(self.count) + ".png", diff_img)
        # vis_img = cv2.drawContours(after_img, [box], 0, (0,0,255), 2)
        vis_img = cv2.rectangle(self.vis_img,(x,y),(x+w,y+h),(0,0,255),2)
        cv2.imwrite("diff_box_" + str(self.count) + ".png", vis_img)
        # pos_x = np.mean(box[:, 0])
        # pos_y = np.mean(box[:, 1])
        # width = np.max(box[:, 0]) - np.min(box[:, 0])
        # height = np.max(box[:, 1]) - np.min(box[:, 1])
        pos_x = x + w / 2
        pos_y = y + h / 2
        self.pos_x = pos_x; self.pos_y = pos_y; self.width = w; self.height = h
        return pos_x, pos_y, w, h

    def if_can_place(self, diff_img, thresh=0.4):
        image_size = diff_img.size
        whitePixels = cv2.countNonZero(diff_img)
        # print("full : {}%".format(float(whitePixels) / image_size * 100))
        if float(whitePixels) / image_size > thresh:
            return False
        return True

    def get_available_angle(self, empty_img, before_img, pos, size):
        # pos:Tuple[x: float, y: float], size:Tuple[width: float, height: float]
        ans_str = ""
        # check availability of lunchbox
        diff_img, img_b =  self.get_diff_img(empty_img, before_img)
        cv2.imwrite("pre_diff_1" + str(self.count) + ".png", img_b)
        cv2.imwrite("capacity" + str(self.count) + ".png", diff_img)
        # calculate how to approach placed food
        H, W, _C = empty_img.shape
        x_ = pos[0]
        y_ = pos[1]
        width_ = size[0]
        height_ = size[1]
        # check top space
        top = int(y_ - height_ / 2 - TH3)
        bottom = int(y_ - height_ / 2)
        left = int(max(0, x_ - width_ / 2))
        right = int(min(W, x_ + width_ / 2))
        if y_ - height_ / 2 - TH2 >= 0:
            ans = self.if_can_place(diff_img[top: bottom, left: right])
            cv2.imwrite("diff_" + str(self.count) + "_top.png", diff_img[top: bottom, left: right])
            cv2.rectangle(self.vis2_img, (left, top), (right, bottom), (0, 255, 0))
            if ans:
                ans_str += "top,"
        else:
            cv2.rectangle(self.vis2_img, (left, top), (right, bottom), (255, 0, 0))
        # check bottom space
        top = int(y_ + height_ / 2)
        bottom = int(y_ + height_ / 2 + TH3)
        left = int(max(0, x_ - width_ / 2))
        right = int(min(W, x_ + width_ / 2))
        if y_ + height_ / 2 + TH2 <= H: 
            ans = self.if_can_place(diff_img[top: bottom, left: right])
            cv2.imwrite("diff_" + str(self.count) + "_bottom.png", diff_img[top: bottom, left: right])
            cv2.rectangle(self.vis2_img, (left, top), (right, bottom), (0, 255, 0))
            if ans:
                ans_str += "bottom,"
        else:
            cv2.rectangle(self.vis2_img, (left, top), (right, bottom), (255, 0, 0))
        # check left space
        top = int(max(0, y_ - height_ / 2))
        bottom = int(min(H, y_ + height_ / 2))
        left = int(x_ - width_ / 2 - TH3)
        right = int(x_ - width_ / 2)
        if x_ - width_ / 2 - TH2 >= 0:
            ans = self.if_can_place(diff_img[top: bottom, left: right])
            cv2.imwrite("diff_" + str(self.count) + "_left.png", diff_img[top: bottom, left: right])
            cv2.rectangle(self.vis2_img, (left, top), (right, bottom), (0, 255, 0))
            if ans:
                ans_str += "left,"
        else:
            cv2.rectangle(self.vis2_img, (left, top), (right, bottom), (255, 0, 0))
        # check right space
        top = int(max(0, y_ - height_ / 2))
        bottom = int(min(H, y_ + height_ / 2))
        left = int(x_ + width_ / 2)
        right = int(x_ + width_ / 2 + TH3)
        if x_ + width_ / 2 + TH2 <= W:
            ans = self.if_can_place(diff_img[top: bottom, left: right])
            cv2.imwrite("diff_" + str(self.count) + "_right.png", diff_img[top: bottom, left: right])
            cv2.rectangle(self.vis2_img, (left, top), (right, bottom), (0, 255, 0))
            if ans:
                ans_str += "right,"
        else:
            cv2.rectangle(self.vis2_img, (left, top), (right, bottom), (255, 0 ,0))
        # check overlapping
        top = int(y_ - height_ / 2)
        bottom = int(y_ + height_ / 2)
        left = int(x_ - width_ / 2)
        right = int(x_ + width_ / 2) 
        ans = self.if_can_place(diff_img[top: bottom, left: right], thresh=0.1)
        cv2.imwrite("diff_" + str(self.count) + "_overlap.png", diff_img[top: bottom, left: right])
        cv2.rectangle(self.vis2_img, (left, top), (right, bottom), (0, 0, 255))
        if not ans:
            ans_str += "overlap"
        cv2.imwrite("check" + str(self.count) + ".png", self.vis2_img)
        print(ans_str)
        return ans_str
        
    def publish_info(self, restrict=False, goal_x=-1, goal_y=-1):
        self.output_img = deepcopy(self.after_img)
        cv2.line(self.output_img, (int(self.rt_x), int(self.rt_y)), (int(self.rb_x), int(self.rb_y)), (0, 255, 0), thickness=2, lineType=cv2.LINE_4)
        cv2.line(self.output_img, (int(self.lt_x), int(self.lt_y)), (int(self.rt_x), int(self.rt_y)), (0, 255, 0), thickness=2, lineType=cv2.LINE_4)
        cv2.line(self.output_img, (int(self.lt_x), int(self.lt_y)), (int(self.lb_x), int(self.lb_y)), (0, 255, 0), thickness=2, lineType=cv2.LINE_4)
        cv2.line(self.output_img, (int(self.lb_x), int(self.lb_y)), (int(self.rb_x), int(self.rb_y)), (0, 255, 0), thickness=2, lineType=cv2.LINE_4)
        top = int((self.lt_y + self.rt_y) / 2 - EXTENTION)
        bottom = int((self.lb_y + self.rb_y) / 2 + EXTENTION)
        left = int((self.lt_x + self.lb_x) / 2 - EXTENTION)
        right = int((self.rt_x + self.rb_x) / 2 + EXTENTION)
        lbox_bimg = self.before_img[top: bottom, left: right, :]
        lbox_aimg = self.after_img[top: bottom, left: right, :]
        cv2.imwrite("lbox_bimg" + str(self.count) + ".png", lbox_bimg)
        cv2.imwrite("lbox_aimg" + str(self.count) + ".png", lbox_aimg)
        cv2.imwrite("lbox_eimg" + str(self.count) + ".png",
                    self.empty_img[top: bottom, left: right, :])
        self.vis_img = deepcopy(lbox_aimg)
        self.vis2_img = deepcopy(lbox_aimg)
        diff_img, img_b = self.get_diff_img(lbox_bimg, lbox_aimg)
        cv2.imwrite("pre_diff_0" + str(self.count) + ".png", img_b)
        if restrict:
            goal_x = goal_x + X_OFFSET - left
            goal_y = goal_y + Y_OFFSET - top
            diff_img = self.ignore_extra_space(diff_img, goal_x, goal_y)
        pos_x, pos_y, width, height = self.get_food_info(diff_img)
        if pos_x:
            _direction = self.get_available_angle(self.empty_img[top: bottom, left: right, :], lbox_bimg, (pos_x, pos_y), (width, height))
            pos_x += left
            pos_y += top
        else:
            direction = ""
            width = 0
            height = 0
            pos_x = 0
            pos_y = 0
        cv2.drawMarker(self.output_img, (int(pos_x), int(pos_y)), (0, 0, 255), markerType=cv2.MARKER_STAR, markerSize=20)
        cv2.imwrite("output_" + str(self.count) + ".png", self.output_img)


vis = VisualFeedback()
msg = MSG()
vis.status_cb(msg)
