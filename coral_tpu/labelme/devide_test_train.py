#all_imgフォルダ内の画像をアノテーションしてjsonファイルを作成した状態にしてください。
#all_imgフォルダ内のデータをテスト用と学習用に分け、test_data, train_dataで出力します。

import glob
import shutil
import numpy as np
import random
import os

input_path = "all_img" 
os.mkdir("test_data")
os.mkdir("train_data")

jpg_list = glob.glob(input_path + "/*.jpg")
JPG_list = glob.glob(input_path + "/*.JPG")
new_list = jpg_list + JPG_list

leng = len(new_list)
print(leng)

random.shuffle(new_list)
#４割をテストデータ、６割を学習データに
test_len = leng * 0.4

for i, img in enumerate(new_list):
    img_name = img[8:]
    json = img[:-4] + ".json"
    json_name = json[8:]
    if i < test_len:
        shutil.copy(img, "test_data/" + img_name)
        shutil.copy(json, "test_data/" + json_name)
    else:
        shutil.copy(img, "train_data/" + img_name)
        shutil.copy(json, "train_data/" + json_name)

