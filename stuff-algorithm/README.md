## おかずを詰める位置の決定

[README.me](https://github.com/jsk-ros-pkg/jsk_3rdparty/tree/master/respeaker_ros)を読んでrespeakerを使うための準備をしておく。<br>

それぞれ別のターミナルで実行する。<br>
```
roslaunch respeaker_ros sample_respeaker.launch language:=ja-JP
```
会話のためにrespeakerを立ち上げる。<br>
```
roseus publisher.l
```
3つのトピックをpublishする。<br>
"/lunchbox_info" : width▷お弁当箱の横幅、height▷お弁当箱の縦幅<br>
"/food_name_info":labels[name▷おかずの名前のリスト]<br>
"/food_size_info":poses[position.x、position.y、position.z▷おかずの座標。food_name_infoの順序に対応]
```
python ./stuff_by_GA.py
```
publisher.lの情報を利用して、お弁当箱の位置を(0,0)とした時の適切なおかずの置き場所を計算する。<br>
以下のトピックをpublishする。<br>
"/stuff_food_pos" :poses[position.x、position.y、position.z▷おかずを詰める位置。food_name_infoの順序に対応]
```
roseus subscriber.l
```
"/stuff_food_pos"の情報を受け取って[[x,y,z],[x,y,z] ...]のかたちのリストに格納する。<br>