# 🔥烟雾火灾检测系统

本项目是一个基于前端 HTML/CSS/JavaScript 与后端 FastAPI 构建的目标检测Web应用。系统集成了YOLO（YOLOv8）模型，实现了图像和视频的上传与目标检测可视化功能，功能是检测和提示火灾发生。

------

## 🛠️ 技术栈

- **前端**：HTML + CSS + JavaScript (原生)
- **后端**：FastAPI (Python)
- **实时传输**：websocket
- **请求**：fetch

------

## 📦 安装指南

1.安装Anaconda

进入Anaconda的官网（https://www.anaconda.com/products/individual#macos），再根据自己的操作系统选择相应的选项下载软件。

2.下载项目:https://github.com/ultralytics/ultralytics/tree/v8.0.50

3.解压

4.创建虚拟环境

```
# 创建虚拟环境
conda create -n yolo_env python==3.10
# 激活环境 conda env list 查看所有的虚拟环境
conda activate yolo_env
```

5.安装项目所需依赖
   pip install -r requirements.txt

6.用PyCharm打开项目，并设置python环境为上面的虚拟环境

![ba89a3b6c2dd6af949a008b7689cc5f2](D:\桌面\ba89a3b6c2dd6af949a008b7689cc5f2.png)

------

## 🚀 运行项目

1. 启动 FastAPI 后端

   ![image-20250405224923560](C:\Users\牛\AppData\Roaming\Typora\typora-user-images\image-20250405224923560.png)

   默认运行在 `http://127.0.0.1:5000/`。

2. 访问前端页面

   ![image-20250405225032133](C:\Users\牛\AppData\Roaming\Typora\typora-user-images\image-20250405225032133.png)

------

## 📁 项目结构

app/
├── results/
│   ├── static/
│   │   ├──script.js/
│   │   └── styles.css/
│   └──templates/
│       └──index.html/
├── uploads/ 
├── app.py/ 
│   └── yolov8_custom.yaml
├── best.pt/
├── openh264-1.8.0-win64.dll/ 
├── requirements.txt
└── README.md

------

## 📸 使用方法

1.打开网页。

2.选择图片检测或视频检测

3.上传一张图片/视频。

4.点击“开始检测”按钮。

5.系统返回检测结果。

------

## 🧠 系统模型说明

使用YOLOv8已经训练好的`best.pt` 模型。

------

## ✅ 示例截图

![image-20250405230342931](C:\Users\牛\AppData\Roaming\Typora\typora-user-images\image-20250405230342931.png)

![image-20250405230403527](C:\Users\牛\AppData\Roaming\Typora\typora-user-images\image-20250405230403527.png)