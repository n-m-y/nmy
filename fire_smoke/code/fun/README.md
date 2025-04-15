# 🔥烟雾火灾检测系统

------

## 🌐 项目简介

本项目基于先进的计算机视觉与深度学习技术，构建了一个集**火焰与烟雾检测、历史记录管理、智能问答与数据统计分析**于一体的综合性火灾预警系统。

系统核心采用**YOLOv8目标检测模型**，实现对图像与视频中火焰、烟雾的快速准确识别。后端采用**FastAPI**框架，前端通过简洁交互界面实现用户操作，整体系统具备良好的响应性与可扩展性。

------

## ✅ 核心功能

### 🔥 **火焰与烟雾检测**

 利用YOLOv8模型对图像或视频进行火灾元素检测，实时返回检测结果与图像标注。

### 🕓 **历史记录管理**

 自动保存每次检测的图片、时间与结果，支持浏览、查询与追溯，便于后期分析。

### 💬 **智能问答系统**

 集成微调后的大语言模型（DeepSeek），支持消防安全相关知识的自然语言交互问答。

### 📊 **数据看板统计系统（管理员专属）**

 通过图表方式展示结果，进行辅助分析。

------

## 🛠️ 技术栈

- **前端**：HTML + CSS + JavaScript (原生)
- **后端**：FastAPI (Python)
- **实时传输**：websocket
- **请求**：fetch
- **检测模型**：YOLO结果模型
- **AI模型**：基于DeepSeek-R1的LoRA微调模型

------

## 📦 安装指南

1.安装Anaconda

进入Anaconda的官网（https://www.anaconda.com/products/individual#macos），再根据自己的操作系统选择相应的选项下载软件。

2.下载项目:[nmy/fire_smoke/code/app at master · n-m-y/nmy](https://github.com/n-m-y/nmy/tree/master/fire_smoke/code/app)/////////////////////

3.解压

4.创建虚拟环境

```bash
# 创建虚拟环境
conda create -n yolo_env python==3.10
# 激活环境 conda env list 查看所有的虚拟环境
conda activate yolo_env
```

5.用PyCharm打开项目，并设置python环境为上面的虚拟环境

![1](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/1.png)

6.安装项目所需依赖
   pip install -r requirements.txt

------

## 🚀 运行项目

1. 启动 FastAPI 后端

   ![2](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/2.png)

   默认运行在http://127.0.0.1:5000/

2. 访问前端页面

   ![3](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/3.png)
   
   默认管理端密码**123456**

------

## 📁 项目结构

fun/
├── static/ 
│   ├── results/ 
│   ├── script.js/
│   └── styles.css/ 
├── templates/ 
│   └── index.html/ 
├── uploads/ 
├── app.py
├── best.pt 
├── detection_logs.json 
├── qa_history.json 
├── openh264-1.8.0-win64.dll 
├── README.md
└── requirements.txt

------

## 📸 使用方法

1.打开网页。

2.选择图片检测或视频检测

3.上传一张图片/视频。

4.点击“开始检测”按钮。

5.系统返回检测结果。

6.点击查询历史记录按钮可查询以往的记录

7.点击ai助手可进行相关知识问答

8.点击数据看板输入管理员权限密码可查看数据统计

------

## 🧠 系统模型说明

**使用YOLOv8已经训练好的`best.pt` 模型。**

![4](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/4.jpg)

![5](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/5.jpg)

**基于DeepSeek-R1的LoRA微调模型**



------

## ✅ 示例截图

![6](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/6.png)

![7](https://github.com/n-m-y/nmy/raw/master/fire_smoke/img/7.png)