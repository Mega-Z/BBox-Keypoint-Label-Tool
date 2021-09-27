# BBox-Keypoint-Label-Tool

一个对应目标边界框标注关键点的标注工具，基于tkinter编写。

## 依赖

python

pillow

## 使用说明

修改bbox-keypoint-label.py中第30行，配置关键点数量

```python
keypoint_num = 4
```

修改第32行，配置输出路径

```python
output_dir = r'./output'
```

运行bbox-keypoint-label.py

```shell
python bbox-keypoint-label.py
```

输入图片路径，点击Load；

![image-20210919112513383](README.assets\image-20210919112513383.png)

点击图片标注边界框；

![image-20210919112618984](README.assets\image-20210919112618984.png)

选择边界框，使用鼠标左键标注对应边界框的关键点，若关键点缺省可以按鼠标右键标注缺省关键点；

![image-20210919112710283](README.assets\image-20210919112710283.png)

切换图片时自动保存，保存格式如下，每一行对应一个目标的边界框，前四个数字为边界框参数，之后依次是各个关键点坐标，缺省关键点坐标为-1。

![image-20210927165450452](README.assets\image-20210927165450452.png)

## 参考

这个repo是在[puzzledqs/BBox-Label-Tool](https://github.com/puzzledqs/BBox-Label-Tool)的基础上修改的


