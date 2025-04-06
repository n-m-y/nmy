# 🔥烟雾火灾检测系统

本项目旨在通过先进的计算机视觉技术，快速、准确地检测火焰和烟雾，以提高火灾预警的效率和准确性。本系统利用YOLOv8目标检测模型，结合FastAPI后端服务和前端交互界面，为用户提供了一个便捷的火灾检测工具。

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

2.下载项目:[nmy/fire_smoke/code/app at master · n-m-y/nmy](https://github.com/n-m-y/nmy/tree/master/fire_smoke/code/app)

3.解压

4.创建虚拟环境

```bash
# 创建虚拟环境
conda create -n yolo_env python==3.10
# 激活环境 conda env list 查看所有的虚拟环境
conda activate yolo_env
```

5.安装项目所需依赖
   pip install -r requirements.txt

6.用PyCharm打开项目，并设置python环境为上面的虚拟环境

![1](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/1.png)

------

## 🚀 运行项目

1. 启动 FastAPI 后端

   ![2](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/2.png)

   默认运行在 `http://127.0.0.1:5000/`。

2. 访问前端页面

   ![3](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/3.png)

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

![4](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/4.jpg)

![5](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/5.jpg)

------

## ✅ 示例截图

![6](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/6.png)

![7](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/7.png)