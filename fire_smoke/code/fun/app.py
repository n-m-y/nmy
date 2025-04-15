import time
from contextlib import asynccontextmanager
import json
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket , Request
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

from fastapi import FastAPI, HTTPException
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

from datetime import datetime


# 设置 Matplotlib 显示中文
rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

aimodel = None
tokenizer = None
generator = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, tokenizer, generator
    print("🚀 正在加载模型...")
    model_path = "E:/Deek/models--gfdgdfasfsf--DeepSeek-R1-fire-1/snapshots/40d33a5879fbb2cb29cd572413b152f6f39e2c48"
    aimodel = AutoModelForCausalLM.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    generator = pipeline("text-generation", model=aimodel, tokenizer=tokenizer)
    print("🔥 模型加载完毕！")
    yield  # 应用运行期间执行
    print("🛑 应用关闭，清理资源...")

# 将 lifespan 传入 FastAPI
app = FastAPI(lifespan=lifespan,debug=True)
# app = FastAPI(debug=True)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


# 允许的文件类型
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# 加载YOLOv8模型
MODEL_PATH = "best.pt"  # 请确保路径正确
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
            "timestamp": datetime.utcnow().isoformat(),
            "file_name": file.filename,
            "detected_objects": detected_objects,
            "is_warning": any([obj["class"] in ["fire", "smoke"] for obj in detected_objects]),
            "is_fire": any([obj["class"] == "fire" for obj in detected_objects]),
            "is_smoke": any([obj["class"] == "smoke" for obj in detected_objects]),
            "confidence": max([obj["confidence"] for obj in detected_objects], default=0.0)  # 最大置信度
        }

        save_detection_data(response_data)

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



# 存储问答历史记录的列表
qa_history = []

# 保存问答历史记录到文件
def save_history(data):
    try:
        with open('qa_history.json', 'a') as f:
            f.write(json.dumps(data) + '\n')  # 每条数据单独一行
    except Exception as e:
        print(f"保存历史记录时出错: {e}")

# 从文件加载问答历史记录
def load_history():
    try:
        with open('qa_history.json', 'r') as f:
            data = [json.loads(line) for line in f]
        return data
    except Exception as e:
        print(f"读取历史记录时出错: {e}")
        return []


@app.post("/ask")
async def ask_question(payload: dict):
    question = payload.get("question", "")

    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:

        import re

        # 模拟调用生成模型
        response = generator(question, max_length=100, num_return_sequences=1)

        # 原始生成内容
        generated = response[0]["generated_text"]

        # 检查是否是问"你是谁？"
        if "你是谁" in generated:
            # 如果是问"你是谁？"就返回自我介绍
            intro = "我是一位资深的消防安全专家、博士，拥有丰富的火灾预防、灭火技术、火灾安全管理和应急处理经验。"
            whistory_entry = {
                "question": "你是谁",
                "answer": intro,
                "timestamp": datetime.utcnow().isoformat()
            }
            save_history(whistory_entry)

            return {
                "answer": intro  # 输出专家自我介绍
            }

        # 提取回答部分（### Response: 后的内容）
        if "### Response:" in generated:
            answer = generated.split("### Response:")[1].strip()
        else:
            answer = generated.strip()

        # 清理文本中的英文和不相关内容（如果有的话）
        answer = re.sub(r'[a-zA-Z]+', '', answer)  # 移除所有英文字符

        # 提取 think 内容
        if "<think>" in answer and "</think>" in answer:
            think = answer.split("<think>")[1].split("</think>")[0].strip()

        # 提取 think 之后的最终回答部分
        if "</think>" in answer:
            final_response = answer.split("</think>")[1].strip()
        else:
            final_response = answer  # 如果没有 <think> 标签，就直接当成最终回答
        final_response = re.sub(r'[<>,/,*,:]', '', final_response)
        # 将内容拼接为一块，使用换行符分隔各部分
        final_answer = f"{final_response}"


        # 创建历史记录条目
        history_entry = {
            "question": question,
            "answer": final_answer,
            "timestamp": datetime.utcnow().isoformat()
        }

        # 添加到历史记录
        qa_history.append(history_entry)
        save_history(history_entry)


        # 返回结构化的 answer 字段
        return {
            "answer": final_answer
        }

    except Exception as e:
        return {"answer": f"发生错误: {e}"}


@app.get("/qa-history")
async def get_qa_history(page: int = 1, size: int = 10):
    history = load_history()
    total_records = len(history)
    total_pages = (total_records + size - 1) // size
    current_page = max(1, min(page, total_pages))
    start = (current_page - 1) * size
    end = min(start + size, total_records)
    records = history[start:end]

    return {
        "currentPage": current_page,
        "totalPages": total_pages,
        "totalRecords": total_records,
        "prevPage": current_page - 1 if current_page > 1 else None,
        "nextPage": current_page + 1 if current_page < total_pages else None,
        "records": records
    }


@app.websocket("/ws/video-detection")
async def websocket_video_detection(websocket: WebSocket):
    await websocket.accept()
    frame_idx = 0
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
            detected_objects = []

            # 在原始图像上绘制检测框
            processed_frame = results[0].plot()  # 这会返回一个带有检测框的图像

            # 分析检测结果
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0].cpu().numpy())
                    class_name = model.names.get(cls_id, "")
                    confidence = float(box.conf[0].cpu().numpy())
                    detected_objects.append({
                        "class": class_name,
                        "confidence": confidence
                    })

            # 将处理后的帧转换为base64编码
            _, buffer = cv2.imencode('.jpg', processed_frame)
            processed_image_base64 = base64.b64encode(buffer).decode('utf-8')

            # 发送检测到的类别和处理后的图像（JSON格式）
            await websocket.send_json({
                "type": "detection",
                "classes": [obj["class"] for obj in detected_objects],  # 只发送实际检测到的类别
                "processedImage": processed_image_base64,
                "timestamp": time.time()
            })

            detection_data = {
                "timestamp": datetime.utcnow().isoformat(),  # 当前时间戳
                "frame_idx": frame_idx,  # 当前帧的索引（适用于视频）
                "detected_objects": detected_objects,  # 检测到的物体及其置信度
                "is_warning": any([obj["class"] in ["fire", "smoke"] for obj in detected_objects]),  # 是否触发预警
                "is_fire": any([obj["class"] == "fire" for obj in detected_objects]),  # 是否检测到火灾
                "is_smoke": any([obj["class"] == "smoke" for obj in detected_objects]),  # 是否检测到烟雾
                "confidence": max([obj["confidence"] for obj in detected_objects], default=0.0)  # 最大置信度，如果列表为空则默认为0.0
            }

            # 存储检测结果
            save_detection_data(detection_data)

            frame_idx += 1

    except Exception as e:
        print(f"WebSocket错误: {e}")
    finally:
        await websocket.close()

@app.get("/getresults")
async def get_results(page: int = 1, size: int = 10):
    results_dir = "static/results"
    if not os.path.exists(results_dir):
        return []

    files = []
    for filename in os.listdir(results_dir):
        file_path = os.path.join(results_dir, filename)
        if os.path.isfile(file_path):
            # 判断文件类型
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_type = "image"
            elif filename.lower().endswith(('.mp4', '.avi', '.mov')):
                file_type = "video"
            else:
                continue

            file_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
            files.append({
                "name": filename,
                "url": f"/static/results/{filename}",
                "type": file_type,
                "date": file_date,
                "mime": "video/mp4" if file_type == "video" else "image/jpeg",
                "is_fire": "fire" in filename.lower(),
                "is_smoke": "smoke" in filename.lower()
            })

    # 按时间降序排序
    files.sort(key=lambda x: os.path.getmtime(os.path.join(results_dir, x["name"])), reverse=True)

    total_records = len(files)
    total_pages = (total_records + size - 1) // size
    current_page = max(1, min(page, total_pages))
    start = (current_page - 1) * size
    end = min(start + size, total_records)
    records = files[start:end]

    return {
        "currentPage": current_page,
        "totalPages": total_pages,
        "totalRecords": total_records,
        "records": records
    }


def save_detection_data(data):
    try:
        with open('detection_logs.json', 'a') as f:
            f.write(json.dumps(data) + '\n')  # 每条数据单独一行
    except Exception as e:
        print(f"保存检测数据时出错: {e}")

def load_detection_data():
    try:
        with open('detection_logs.json', 'r') as f:
            data = [json.loads(line) for line in f]
        return data
    except Exception as e:
        print(f"读取检测数据时出错: {e}")
        return []

def generate_dashboard_data():
    data = load_detection_data()  # 加载检测数据
    today = datetime.utcnow().date()

    total_count = len(data)
    today_count = len([d for d in data if datetime.fromisoformat(d["timestamp"]).date() == today])
    warning_count = len([d for d in data if d["is_warning"]])
    today_warning_count = len(
        [d for d in data if datetime.fromisoformat(d["timestamp"]).date() == today and d["is_warning"]])

    # 按日期统计预警趋势
    warning_trend = {}
    for item in data:
        date_str = datetime.fromisoformat(item["timestamp"]).strftime("%Y-%m-%d")
        if date_str not in warning_trend:
            warning_trend[date_str] = 0
        if item["is_warning"]:
            warning_trend[date_str] += 1

    # 转换为列表并排序
    warning_trend_list = sorted(warning_trend.items(), key=lambda x: x[0])

    return {
        "total_count": total_count,
        "today_count": today_count,
        "warning_count": warning_count,
        "today_warning_count": today_warning_count,
        "warning_trend": warning_trend_list  # 添加预警趋势数据
    }




@app.get("/dashboard")
async def dashboard():
    data = generate_dashboard_data()
    return data

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    password = data.get("password")
    if password == '123456':
        return {"code": 1}
    else:
        return {"code": 0}


if __name__ == "__main__":
    run_server()