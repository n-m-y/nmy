import time
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import cv2
import numpy as np
import base64
from ultralytics import YOLO
import tempfile
from PIL import Image, ImageDraw, ImageFont
from starlette.responses import StreamingResponse
from matplotlib import rcParams


# 设置 Matplotlib 显示中文
rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

app = FastAPI()

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


# 允许的文件类型
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# 加载YOLOv8模型
MODEL_PATH = "best.pt"  # 请确保路径正确，原代码使用 "D:/yolov8/runs/detect/train11/weights/best.pt"
model = YOLO(MODEL_PATH)

# 设置中文字体路径
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
FONT_SIZE = 20

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get('/')
async def index():
    return templates.TemplateResponse("index.html",{"request": {}})


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="不支持的文件类型，请上传JPG、JPEG或PNG格式的图片")
    if file.filename == '':
        raise HTTPException(status_code=400, detail="未选择文件")
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="文件大小不能超过10MB")


    try:
        # 创建临时文件保存上传的图片
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(await file.read())
            temp_filename = temp_file.name

        # 读取图片
        image = cv2.imread(temp_filename)
        if image is None:
            os.unlink(temp_filename)# 删除临时文件
            raise HTTPException(status_code=400, detail="无法读取图片，请确保图片格式正确")

        # 使用 YOLOv8 模型进行检测
        results = model(image)

        # 获取类别名称列表
        class_names = model.names

        # 创建结果对象列表
        detected_objects = []

        # 转换 OpenCV 图片为 PIL 格式
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)

        # 设置字体
        try:
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        except IOError:
            # 如果找不到指定字体，使用默认字体
            font = ImageFont.load_default()
            print(f"警告: 无法加载字体 {FONT_PATH}，使用默认字体")


        # 遍历检测结果
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                class_name = class_names.get(cls_id, "未知")

                # 仅添加物体类别和置信度
                detected_objects.append({
                    'class': class_name,
                    'confidence': conf
                })

                if class_name == 'smoke':
                # 绘制矩形框
                    draw.rectangle([int(x1), int(y1), int(x2), int(y2)], outline="green", width=2)

                if class_name == 'fire':
                    draw.rectangle([int(x1), int(y1), int(x2), int(y2)], outline="red", width=2)




        # 转回 OpenCV 图片格式
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

        # 保存处理后的图片
        result_filename = os.path.join(RESULT_FOLDER, f"result_{file.filename}")
        cv2.imwrite(result_filename, image)

        # 将处理后的图片转换为 base64 格式
        _, img_encoded = cv2.imencode('.jpg', image)
        processed_image_base64 = base64.b64encode(img_encoded).decode('utf-8')

        # 删除临时文件
        os.unlink(temp_filename)

        response_data = {
            'success': True,
            'data': {
                'objects': detected_objects,
                'processedImage': processed_image_base64,
            }
        }

        return JSONResponse(content=jsonable_encoder(response_data))

    except Exception as e:
        # 确保清理临时文件
        if 'temp_filename' in locals():
            try:
                os.unlink(temp_filename)
            except:
                pass

        raise HTTPException(status_code=500, detail=f"处理图片时出错: {str(e)}")




# 允许的视频文件类型
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov'}

def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

@app.post("/detect_video")
async def detect_video(file: UploadFile = File(...)):
    if not allowed_video_file(file.filename):
        raise HTTPException(status_code=400, detail="不支持的文件类型，请上传MP4、AVI或MOV格式的视频")
    if file.filename == '':
        raise HTTPException(status_code=400, detail="未选择文件")
    if file.size > 500 * 1024 * 1024:  # 100MB
        raise HTTPException(status_code=400, detail="文件大小不能超过100MB")

    try:
        # 创建临时文件保存上传的视频
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(await file.read())
            temp_filename = temp_file.name

        # 打开视频文件
        cap = cv2.VideoCapture(temp_filename)
        if not cap.isOpened():
            os.unlink(temp_filename)
            raise HTTPException(status_code=400, detail="无法读取视频，请确保视频格式正确")

        # 获取视频帧率、尺寸等信息
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 创建临时文件保存处理后的视频
        result_filename = os.path.join(RESULT_FOLDER, f"result_{file.filename}")
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(result_filename, fourcc, fps, (width, height))

        # 逐帧处理视频
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 使用 YOLOv8 模型进行检测
            results = model(frame)

            # 转换 OpenCV 图片为 PIL 格式
            frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(frame_pil)

            # 设置字体
            try:
                font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            except IOError:
                font = ImageFont.load_default()

            # 遍历检测结果
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    class_name = model.names.get(cls_id, "未知")

                    # 绘制矩形框
                    if class_name == 'smoke':
                        draw.rectangle([int(x1), int(y1), int(x2), int(y2)], outline="green", width=2)
                    elif class_name == 'fire':
                        draw.rectangle([int(x1), int(y1), int(x2), int(y2)], outline="red", width=2)



            # 转回 OpenCV 图片格式并写入输出视频
            frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
            out.write(frame)

        # 释放资源
        cap.release()
        out.release()

        # 删除临时文件
        os.unlink(temp_filename)

        # 检查输出文件是否存在
        if not os.path.exists(result_filename):
            raise HTTPException(status_code=500, detail="视频处理失败，输出文件未生成")


        # 返回处理后的视频文件
        return StreamingResponse(open(result_filename, "rb"), media_type="video/mp4")

    except Exception as e:
        # 确保清理临时文件
        if 'temp_filename' in locals():
            try:
                os.unlink(temp_filename)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"处理视频时出错: {str(e)}")





def run_server():
    # 启动 FastAPI 应用
    uvicorn.run(app, host="127.0.0.1", port=5000)


@app.websocket("/ws/video-detection")
async def websocket_video_detection(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 接收前端发送的视频帧（二进制数据）
            data = await websocket.receive_bytes()

            # 将二进制数据转为OpenCV帧
            frame = cv2.imdecode(
                np.frombuffer(data, np.uint8),
                cv2.IMREAD_COLOR
            )
            if frame is None:
                continue

            # 使用YOLOv8检测
            results = model(frame)
            detected_classes = set()

            # 在原始图像上绘制检测框
            processed_frame = results[0].plot()  # 这会返回一个带有检测框的图像

            # 分析检测结果
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0].cpu().numpy())
                    class_name = model.names.get(cls_id, "")
                    if class_name in ["fire", "smoke"]:
                        detected_classes.add(class_name)

            # 将处理后的帧转换为base64编码
            _, buffer = cv2.imencode('.jpg', processed_frame)
            processed_image_base64 = base64.b64encode(buffer).decode('utf-8')

            # 发送检测到的类别和处理后的图像（JSON格式）
            await websocket.send_json({
                "type": "detection",
                "classes": list(detected_classes),  # 只发送实际检测到的类别
                "processedImage": processed_image_base64,
                "timestamp": time.time()
            })

    except Exception as e:
        print(f"WebSocket错误: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    run_server()