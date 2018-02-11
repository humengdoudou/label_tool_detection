# 多类别的目标检测框标定工具label_tool_detection使用流程


标签： 多目标检测标定工具

---

### 1. 背景

本文主要介绍多类别的目标检测框标定工具label_tool_detection[1]使用流程，代码基于开源目标标定工具BBox-Label-Tool[1]修改。

通过使用label_tool_detection，可以对单张图像进行以下方式标定： 

<div align=middle><img width="300" height="450" src="https://github.com/humengdoudou/label_tool_detection/blob/master/sups_img_for_readme/img1.png?raw=true"/></div>

图1 使用label_tool_detection标定结果示意图

通过label_tool_detection标定保存的图像标定结果.txt内容格式：

- 4
- coat 43 93 254 375
- pants 58 365 216 665
- shoes 26 663 90 717
- shoes 176 665 236 719

第一行数字4表示一张图像中标定了四个目标框，剩下四行分别表示每一个被标定的目标，格式为(class, top_x, top_y, button_x, button_y)。

原始版本BBox-Label-Tool在标定多目标检测框时，存在以下不便之处：
1. 	bounding box list框内，无法显示已经标定的bbox的类别标签；
1. 	每个bbox的类别标签即使缺省为空，也能保存至.txt文件中，没有任何报错和校验机制；
1. 	点击prev/next按钮，查看之前的标定结果，即使没有重新标定，由于2中的原因，会造成已标定的结果被重置；上一帧的标定类别标签会默认顺延至下一帧为标定图像中，同样由于2中的原因，会造成标定结果被修改；
1.  缺少对目标框标签的重置清零功能；

我通过修改部分代码和处理流程，完善了以上四个问题，使得标定工具更方便使用，目前该标定工具已用于多类别的目标检测框标定工作中。

**重要：标定目标框前，需要先设置该目标框类别，如"coat", "pants"，再进行目标框坐标标定。**


### 2. 参考文献

1. 	https://github.com/puzzledqs/BBox-Label-Tool

### 3. 图像的收集标定与格式转换
本小节主要介绍图像的收集与标定流程、标定结果的校验、训练测试图像列表的生成、Pascal VOC格式的.xml文件转换、通过标定标签crop局部图像区域等步骤，相关代码可以参照label_tool_detection 项目中的代码。

#### 3.1 图像收集 
图像的收集比较简单，我们使用label_tool_detection完成智能服饰识别中的服饰图像标定，图像主要来自于淘宝图像、百度街拍图片等，直接使用爬虫收集图片即可，图像风格类似图2。

<div align=middle><img width="600" height="650" src="https://github.com/humengdoudou/label_tool_detection/blob/master/sups_img_for_readme/img2.png?raw=true"/></div>

图2 收集图像风格示意

#### 3.2 图像的标定
标定使用label_tool_detection完成标定，一张图像标定结果示意如图3所示：

<div align=middle><img width="550" height="480" src="https://github.com/humengdoudou/label_tool_detection/blob/master/sups_img_for_readme/img3.png?raw=true"/></div>

图3 label_tool_detection结果示意图

当前确定的标定类别为“coat”、“pants”、“glasses”、“hat”、“shoes”、“bag”等六类，如需增删类别，可在label_tool.py文件中按照def selectcoat(self):函数增删即可。目标标定框颜色随机生成，无其他特殊含义。

系统的标签与图片组织路径如图4所示，label_tool.py放在label_tool_detection的根目录，Annotations存放最后生成的.xml文件，JPEGImages下按子文件夹目录存放.jpg/.jpeg图片，Labels存放标注好的.txt标签文件。Annotations、JPEGImages、Labels存放相同的子目录文件即可，例如截图中所示的20180123文件夹，该文件夹需要手动新建。

<div align=middle><img width="250" height="350" src="https://github.com/humengdoudou/label_tool_detection/blob/master/sups_img_for_readme/img4.png?raw=true"/></div>

图4 标定工具文件组织格式

操作流程比较简单：
1. 在Image Dir内填入图片路径，注意，只用填写子文件夹名如20180123即可；
1. 点击load，十字线在鼠标进入图片区域后自动生成；
1. **在标注目标前先确定该目标类别，点击六个按钮中的一个，class中将显示该类别；**
1. 点击标注区域左上角，松开鼠标，移动至标注区域右下角，再次点击鼠标，即可在右边bounding boxes区域生成标定区域的类别、左上角、右下角坐标；
1. 重复单张图像内的多个目标标定；
1. 单张图片标定完成，点击next，进行下一张图片标定；

其他：
1. 鼠标点击bounding boxes区域的某一个标定框，选定后点击Delete，可以完成该目标框的删除；
1. 标定过程中，若对当前标定结果不满意，可以直接Esc退出当前框标定；
1. clear all可以删除当前图像的所有标定目标框；
1. clear label可以清空class中的类别标签；
1. 点击prev/next浏览标定结果时，最好点击clear label清空class类别；

Labels/*.txt文件内的标定结果随单张图像的标定完成，自动生成，格式如图5所示：

<div align=middle><img width="600" height="100" src="https://github.com/humengdoudou/label_tool_detection/blob/master/sups_img_for_readme/img5.png?raw=true"/></div>

图5 标定文件格式

第一行的4表示本张图片有4个标定目标框，coat、pants、shoes表示每个标定目标框类别，后四个数字对应目标框左上角、右下角(x, y)坐标。


#### 3.3 标定结果校验

因为标定过程中可能出现某些框忘记打类别标签的情况，例如其中一行只出现了坐标信息，而没有类别信息(BBox-Label-Tool中存在此类情形，修改后的label_tool_detection此类情形已不会发生)。因此可以通过一个脚本简单地对最终标定结果进行校验，判断标定结果是否正确。具体可以参照check_label_vilid.py文件，其功能在comments中有解释。

#### 3.4 训练验证列表生成
本小节完成训练/验证图像列表的生成，可以参照脚本create_trainval_test.py(其实是生成了train\val两类列表)。生成方式比较简单，调用create_trainval_label得到Labels下所有标定文件名(不包含后缀名)列表，该.txt文件列表由3.2小节生成。然后随机打乱即可，VAL_NUM_END、TRAIN_NUM_END分别指定生成的train.txt、test.txt的文件数目，根据实际数据量做相应修改即可。生成文件保存在label_tool_detection根目录下。

#### 3.5 标定.xml文件的生成

基于caffe_SSD、mxnet_SSD的目标检测，都是按照Pascal VOC格式进行数据组织的，因此最后一步中，需要将标定标签.txt生成对应的.xml格式，可以参照脚本create_txt2xml.py完成，文件的组织形式和路径修改在20~23行完成，对应修改路径即可。

Annotations文件夹下需要手动新建对应的如20180123子文件夹。
	
#### 3.6 标定区域截图

由于标定的每个矩形框都包含了一个特定类别的目标，因此这些目标框也可用来完成分类训练任务，在智能服饰识别项目中，标定的目标框图像将用于后续的多任务图像分类训练，crop_patch_from_image.py文件完成此功能，并根据标定类别，将截取的子区域保存在不同的文件夹中。


### 4. 附录

#### 4.1 使用代码列表清单

查看本git即可

### 5. 修订明细

| 修订号   |  修订时间  |  修订版本  |  修订人  | 修订说明 |
| :-----:  | :-----:    | :----:     | :-----:  | :----:   |
| 1        | 2018-01-24 |   V1.0     |   胡孟   |          |
| 2        |            |            |          |          |
| 3        |            |            |          |          |
| 4        |            |            |          |          |
