## データセットをつくる

まず、[labelmeを使ってアノテーション](https://github.com/jsk-ros-pkg/jsk_recognition/blob/c0fab6053e722663e063e86e009b794e8fa9207a/doc/deep_learning_with_image_dataset/annotate_images_with_labelme.rst)して、data_annotatedというフォルダに保存する。このフォルダには画像とjsonファイルが入っている状態になる。

次に、[このサイト](https://github.com/wkentaro/labelme/tree/master/examples/instance_segmentation)からlabelme2voc.pyを取ってきて

```
python3 ./labelme2voc.py data_annotated data_dataset_voc --labels labels.txt
```

私の環境ではpython2だと失敗してしまった。

coco形式なら
```
pip install pycocotools
chmod u+x labelme2coco.py
./labelme2coco.py data_annotated data_dataset_coco --labels labels.txt
```