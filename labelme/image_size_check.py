import glob
import cv2
import numpy as np

class Check:

    def __init__(self):
        self.count = 0
        self.bad_shape_images = []
    
    def check_img(self, file_path):
        for f_name in file_path:
            img = cv2.imread(f_name)
            print(f_name , "'s shape is ", img.shape)
            self.count += 1
            if img.shape != (3024, 4032, 3):
                self.bad_shape_images.append(f_name)

    def show_res(self):
        print("checked ", self.count, " images")
        print("bad shape images are ", self.bad_shape_images)
        

file_list = glob.glob("okazu_35/train/*.JPG")
file_list_2 = glob.glob("okazu_35/train/*.jpg")
file_list_3 = glob.glob("okazu_35/test/*.JPG")
file_list_4 = glob.glob("okazu_35/test/*.jpg")

check_train = Check()
check_train.check_img(file_list)
check_train.check_img(file_list_2)
check_train.show_res()

check_test = Check()
check_test.check_img(file_list_3)
check_test.check_img(file_list_4)
check_test.show_res()

