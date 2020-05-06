# お弁当盛り付けロボット
## HIROを動かす

[add_by_tanemotoブランチのコミット参照](https://github.com/MiyabiTane/rtmros_tutorials/tree/add_by_tanemoto)

## jsk_model_toolsを使う

[add_by_tanemoブランチのコミット参照](https://github.com/MiyabiTane/jsk_model_tools/tree/add_by_tanemoto)

## Coral TPU を使う
### gazebo内で使うなら

hironxjskのgazeboを立ち上げる。例えば
```
source ~/ros/jsk_hiro_ws/devel/setup.bash
roslaunch hironx_tutorial hiro_lunch_box.launch 
```

Coralの認識ノードを立ち上げる
```
source ~/coral_ws/devel/setup.bash
roslaunch coral_usb edgetpu_object_detector.launch INPUT_IMAGE:=/head_camera/rgb/image_raw
```

結果を見てみる

```
rosrun image_view image_view image:=/edgetpu_object_detector/output/image
```

### Coral TPUのインストール を行う

https://github.com/knorth55/coral_usb_ros#install-the-edge-tpu-runtime をみてCoral TPUをインストールする

```
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install libedgetpu1-max
sudo apt-get install python3-edgetpu
```

### Tensorflowliteのインストール を行う

https://github.com/knorth55/coral_usb_ros#install-just-the-tensorflow-lite-interpreter をみてtensorflowlite interpreterをインストールする
```
sudo apt-get install python3-pip
wget https://dl.google.com/coral/python/tflite_runtime-1.14.0-cp36-cp36m-linux_x86_64.whl
pip3 install tflite_runtime-1.14.0-cp36-cp36m-linux_x86_64.whl
```

### ワークスペースをビルドする

https://github.com/knorth55/coral_usb_ros#workspace-build-melodic
をみてワークスペースを作成しコンパイルする

```
source /opt/ros/melodic/setup.bash
mkdir -p ~/coral_ws/src
cd ~/coral_ws/src
git clone https://github.com/knorth55/coral_usb_ros.git
wstool init
wstool merge coral_usb_ros/fc.rosinstall.melodic
wstool update
rosdep install --from-paths . --ignore-src -y -r
cd ~/coral_ws
catkin init
catkin config -DPYTHON_EXECUTABLE=/usr/bin/python3 -DPYTHON_INCLUDE_DIR=/usr/include/python3.6m -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.6m.so
catkin build -vi
````````````````

### 学習済みモデルをダウンロードする

https://github.com/knorth55/coral_usb_ros#model-download をみてモデルをダウンロードする

```
source /opt/ros/melodic/setup.bash
source ~/coral_ws/devel/setup.bash
roscd coral_usb/scripts
python download_models.py
`````

### Coral TPUを使うにあたっての事前準備

```
python3 -m pip install opencv-python
```

### USBカメラを立ち上げる

カメラノードを立ち上げる

```
source /opt/ros/melodic/setup.bash
roslaunch roseus_tutorials usb-camera.launch 
```

### Coralの認識ノードを立ち上げる

```
source /opt/ros/melodic/setup.bash
source ~/coral_ws/devel/setup.bash
roslaunch coral_usb edgetpu_object_detector.launch INPUT_IMAGE:=/image_raw

```

### 結果を見てみる

```
source /opt/ros/melodic/setup.bash
rosrun image_view image_view image:=/edgetpu_object_detector/output/image
```

### 閾値の調節

```
 rosrun rqt_reconfigure rqt_reconfigure
```

edgetpu_object_detectorのscore_threshで物体表示の閾値を変更することができる。


## 新しいモデルを学習させる

[詳細はこちら](https://github.com/MiyabiTane/HIRO_LunchBox/tree/master/labelme)
