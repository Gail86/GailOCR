import importlib
import subprocess
import sys

def check_and_install(package_name):
    # 尝试导入包,如果当前目录已存在离线包则直接导入
    try:
        importlib.import_module(package_name)
        print(f'{package_name} 已加载成功')
    except ImportError:
        print(f'未找到 {package_name}，正在尝试安装...')
        # 使用pip安装缺失的包
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f'{package_name} 安装完成并加载成功')

# 对核心库进行验证，如果缺失则进行安装
check_and_install('Image')
check_and_install('base64')
check_and_install('importlib')
check_and_install('subprocess')
check_and_install('ddddocr')
check_and_install('uvicorn')
check_and_install('FastAPI')
check_and_install('json')

import json
#核心库带带弟弟验证码库
import ddddocr
#FastAPI及其依赖项uvicorn
import uvicorn
import base64
import os
from io import BytesIO
from PIL import Image
#增加HTTPException用于返回http响应码 400/4003
#增加Request用于捕获全局异常响应返回
from fastapi import FastAPI, HTTPException, Request
#增加JSONResponse用于处理全局异常返回
from fastapi.responses import JSONResponse
import re
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from datetime import datetime
# 读取配置文件中的授权keys、验证设置和端口，默认授权关闭按需开启。
#授权开启方式，设置key，设置expire_at，把verify_authorization的值改成true即可，收到请求时，验证key是否存在如果存在则验证key是否为有效期
#返回值：正常验证码识别结果、Authorization does not exist、Invalid expiration date format、Authorization expired
config_path = 'config.json'
vers = '1.1.1'
# 默认配置
default_config = {
    "authorized_keys": [
        {
            "key": "example_key",
            "expire_at": "2025-12-31T23:59:59Z"
        },
        {
            "key": "another_example_key",
            "expire_at": "2024-06-30T23:59:59Z"
        }
    ],
    "verify_authorization": False,
    "port": 8000
}
#初始化完成，生成10行换行符
print('\n' * 10)
# 检查并生成默认配置文件（如果不存在）
if not os.path.exists(config_path):
    with open(config_path, 'w') as file:
        json.dump(default_config, file, indent=4)
        print(f"配置文件不存在，已载入默认配置并生成输出配置文件 {config_path}")

# 加载配置文件
with open(config_path, 'r') as file:
    config = json.load(file)
print(f"已载入配置文件 {config_path}")
# 合并默认配置和用户配置
authorized_keys = config.get('authorized_keys', default_config['authorized_keys']) # 获取授权key列表，如果配置文件中没有则使用默认值
verify_authorization = config.get('verify_authorization', default_config['verify_authorization']) # 获取是否启用授权验证，如果配置文件中没有则使用默认值
# 配置端口号
port_from_config = config.get('port', default_config['port'])  # 默认值为6688，以防配置文件中没有找到port键，如果没有配置文件则默认启动6688为端口
#授权验证函数
def validate_key(api_key: str) -> str:
    """
    验证授权key的有效性
    :param api_key: 要验证的授权key
    :return: 验证结果的文本信息
    """
    if not verify_authorization:  # 如果未启用授权验证
        return "Authorized by system"  # 返回授权通过的信息

    auth_key_info = next((item for item in authorized_keys if item["key"] == api_key), None)  # 查找授权key信息
    if not auth_key_info:  # 如果找不到对应的授权key
        return "Authorization does not exist"  # 返回授权不存在的信息

    expire_at_str = auth_key_info.get("expire_at")  # 获取授权key的过期时间
    if expire_at_str:
        try:
            expire_at = datetime.fromisoformat(expire_at_str.replace("Z", "+00:00"))  # 将ISO格式的时间字符串转换为datetime对象
        except ValueError:
            return "Invalid expiration date format"  # 返回无效日期格式的信息

        current_time = datetime.utcnow()  # 获取当前UTC时间
        if current_time > expire_at:  # 如果当前时间超过过期时间
            return "Authorization expired"  # 返回授权过期的信息
    
    return "Authorized by system"  # 返回授权通过的信息

description = """
* 增强版DDDDOCR

* 识别效果完全靠玄学，可能可以识别，可能不能识别。——DDDDOCR

  <img src="https://img.shields.io/badge/GitHub-ffffff"></a> <a href="https://github.com/81NewArk/StupidOCR"> <img src="https://img.shields.io/github/stars/81NewArk/StupidOCR?style=social"> <img src="https://badges.pufler.dev/visits/81NewArk/StupidOCR">
"""
description1 = """
* 增强版DDDDOCR

* StupidOCR 是一个简单的 OCR（光学字符识别）服务，支持图像中的文本提取和验证授权功能。
## 主要特性
  - **Base64 图像处理**：接收 Base64 编码的图像数据进行 OCR 处理。
- **授权验证**：支持基于密钥的授权验证机制。
- **错误处理**：提供友好的错误信息和日志记录功能。

## 使用说明

1. 发送 POST 请求到 `/api/ocr/image` 端点，请求体中包含 Base64 编码的图像数据和授权密钥。
2. 返回 OCR 结果或相应的错误信息。
## 特别说明，及改动事宜
- ** 此版本注释掉了原作者的Github地址，避免由于打不开Github导致无法打开docs页面。
- ** [原项目地址](https://github.com/81NewArk/StupidOCR)
- **授权验证**：允许通过配置文件增加或者删除授权key，并且提供授权开关。
- **自动初始化**：增加了对使用库的自动安装初始化步骤，避免因为环境问题导致无法启动。
- **端口自定义**：配置文件里增加了端口项，避免编译成exe后无法修改端口的问题。
"""

app = FastAPI(title="StupidOCR", description=description1, version="1.1.1")
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
number_ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
number_ocr.set_ranges(0)
compute_ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
compute_ocr.set_ranges("0123456789+-x÷=")
alphabet_ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
alphabet_ocr.set_ranges(3)
det = ddddocr.DdddOcr(det=True,show_ad=False)
shadow_slide = ddddocr.DdddOcr(det=False, ocr=False,show_ad=False)

class ModelImageIn(BaseModel):
    img_base64: str
    key: str

class ModelSliderImageIn(BaseModel):
    gapimg_base64: str
    fullimg_base64: str
    key: str






@app.get("/",summary="index.html",tags=["主页"])
async def read_root():
    return FileResponse("dist/index.html")
# 全局异常处理器
@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    #logger.error(f"An error occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)},
    )

@app.post("/api/ocr/image", summary="通用", tags=["验证码识别"])
async def ocr_image(data: ModelImageIn):
    validation_result = validate_key(data.key)  # 验证授权键
    if validation_result != "Authorized by system":  # 如果验证未通过
        raise HTTPException(status_code=403, detail=validation_result)  # 抛出HTTP 403异常
    # 在尝试解码之前，使用正则表达式检查Base64字符串的格式。额外的Base64有效性检查，如果收到的base64编码检查无效则直接抛出避免收到无效数据进行处理导致服务器异常
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', data.img_base64):
        raise HTTPException(status_code=400, detail="Invalid base64 image data: Incorrect format")
    try:
        img = base64.b64decode(data.img_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")  # 增加解码失败则抛出HTTP 400异常返回异常信息
    result = ocr.classification(img) # 进行OCR识别
    return {"result": result}# 返回识别结果

@app.post("/api/ocr/number", summary="数字", tags=["验证码识别"])
async def ocr_image_number(data: ModelImageIn):
    validation_result = validate_key(data.key)
    if validation_result != "Authorized by system":
        raise HTTPException(status_code=403, detail=validation_result)
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', data.img_base64):
        raise HTTPException(status_code=400, detail="Invalid base64 image data: Incorrect format")
    try:
        img = base64.b64decode(data.img_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")
    result = number_ocr.classification(img, probability=True)
    string = "".join(result['charsets'][i.index(max(i))] for i in result['probability'])
    return {"result": string}

@app.post("/api/ocr/compute", summary="算术", tags=["验证码识别"])
async def ocr_image_compute(data: ModelImageIn):
    validation_result = validate_key(data.key)
    if validation_result != "Authorized by system":
        raise HTTPException(status_code=403, detail=validation_result)
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', data.img_base64):
        raise HTTPException(status_code=400, detail="Invalid base64 image data: Incorrect format")
    try:
        img = base64.b64decode(data.img_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")
    result = compute_ocr.classification(img, probability=True)
    string = "".join(result['charsets'][i.index(max(i))] for i in result['probability'])
    string = string.split("=")[0].replace("x", "*").replace("÷", "/")
    try:
        result = eval(string)
    except:
        result = "Error"
    return {"result": result}

@app.post("/api/ocr/alphabet", summary="字母", tags=["验证码识别"])
async def ocr_image_alphabet(data: ModelImageIn):
    validation_result = validate_key(data.key)
    if validation_result != "Authorized by system":
        raise HTTPException(status_code=403, detail=validation_result)
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', data.img_base64):
        raise HTTPException(status_code=400, detail="Invalid base64 image data: Incorrect format")
    try:
        img = base64.b64decode(data.img_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")
    result = alphabet_ocr.classification(img, probability=True)
    string = "".join(result['charsets'][i.index(max(i))] for i in result['probability'])
    return {"result": string}

@app.post("/api/ocr/detection", summary="文字点选", tags=["验证码识别"])
async def ocr_image_det(data: ModelImageIn):
    validation_result = validate_key(data.key)
    if validation_result != "Authorized by system":
        raise HTTPException(status_code=403, detail=validation_result)
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', data.img_base64):
        raise HTTPException(status_code=400, detail="Invalid base64 image data: Incorrect format")
    try:
        img = base64.b64decode(data.img_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")
    img_pil = Image.open(BytesIO(img))
    res = det.detection(img)
    result = {ocr.classification(img_pil.crop(box)): [box[0] + (box[2] - box[0]) // 2, box[1] + (box[3] - box[1]) // 2] for box in res}
    return {"result": result}

@app.post("/api/ocr/slider/gap", summary="缺口滑块识别", tags=["验证码识别"])
async def ocr_image_slider_gap(data: ModelSliderImageIn):
    validation_result = validate_key(data.key)
    if validation_result != "Authorized by system":
        raise HTTPException(status_code=403, detail=validation_result)
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', data.gapimg_base64) or not re.match(r'^[A-Za-z0-9+/]*={0,2}$', data.fullimg_base64):
        raise HTTPException(status_code=400, detail="Invalid base64 image data: Incorrect format")
    try:
        gapimg = base64.b64decode(data.gapimg_base64)
        fullimg = base64.b64decode(data.fullimg_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")
    result = det.slide_match(gapimg, fullimg)
    return {"result": result}

@app.post("/api/ocr/slider/shadow", summary="阴影滑块识别", tags=["验证码识别"])
async def ocr_image_slider_shadow(data: ModelSliderImageIn):
    validation_result = validate_key(data.key)
    if validation_result != "Authorized by system":
        raise HTTPException(status_code=403, detail=validation_result)
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', data.gapimg_base64) or not re.match(r'^[A-Za-z0-9+/]*={0,2}$', data.fullimg_base64):
        raise HTTPException(status_code=400, detail="Invalid base64 image data: Incorrect format")
    try:
        shadowimg = base64.b64decode(data.gapimg_base64)
        fullimg = base64.b64decode(data.fullimg_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")
    result = shadow_slide.slide_comparison(shadowimg, fullimg)
    return {"result": result}

if __name__ == '__main__':
    print(f'''

      _____   _                     _       _    ____     _____   _____  
     / ____| | |                   (_)     | |  / __ \   / ____| |  __  \ 
    | (___   | |_   _   _   _ __    _    __| | | |  | | | |      | |__) |
     \___ \  | __| | | | | | '_ \  | |  / _` | | |  | | | |      |  _  / 
     ____) | | |_  | |_| | | |_) | | | | (_| | | |__| | | |____  | | \  \ 
    |_____/   \__|  \__,_| | .__/  |_|  \__,_|  \____/   \_____| |_|  \_/
                           | |                                           
                           |_|                                           


                    软件主页：http://127.0.0.1:{port_from_config}
                    开发文档：http://localhost:{port_from_config}/docs
                    当前版本：{vers}
                   

                    代码编写：81NewArk/Gail86改

       ''')

    uvicorn.run(app, host="0.0.0.0", port=port_from_config, access_log=True)
