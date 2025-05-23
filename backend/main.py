from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os
import shutil
import logging
from dotenv import load_dotenv
from handwriting_recognizer import recognize_handwriting, generate_tags, publish_to_flomo

# 加载.env文件中的环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="笔记Agent API", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateTagsRequest(BaseModel):
    text: str
    prompt_template: Optional[str] = "default"

class PublishNoteRequest(BaseModel):
    text: str
    tags: List[str]
    image_urls: List[str]

@app.post("/api/upload_image")
async def upload_image(
    image: UploadFile = File(...),
    prompt_template: Optional[str] = Form("default")
):
    """上传图片，返回识别文本和图片URL"""
    logger.info("=== 开始处理图片上传请求 ===")
    
    try:
        # 详细日志输出
        logger.info(f"接收到文件: filename={image.filename}")
        logger.info(f"文件类型: content_type={image.content_type}")
        logger.info(f"文件大小: size={image.size}")
        logger.info(f"prompt_template参数: {prompt_template}")
        
        # 验证文件
        if not image.filename:
            logger.error("文件名为空")
            return {
                "success": False,
                "text": "",
                "image_url": "",
                "msg": "文件名不能为空"
            }
        
        # 验证文件类型
        if not image.content_type.startswith('image/'):
            logger.error(f"非图片文件: {image.content_type}")
            return {
                "success": False,
                "text": "",
                "image_url": "",
                "msg": "请上传图片文件"
            }
        
        logger.info("开始保存临时文件...")
        
        # 保存临时文件
        file_extension = os.path.splitext(image.filename)[1] or '.jpg'
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            logger.info(f"临时文件路径: {tmp_file.name}")
            
            # 读取文件内容
            content = await image.read()
            logger.info(f"读取文件内容大小: {len(content)} bytes")
            
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        logger.info("临时文件保存成功，开始调用识别API...")
        
        # 这里简化处理，直接用本地文件路径作为URL
        image_url = f"file://{tmp_path}"
        logger.info(f"图片URL: {image_url}")
        
        # 调用识别模块
        logger.info("调用handwriting_recognizer.recognize_handwriting...")
        result = recognize_handwriting(image_url, prompt_template)
        logger.info(f"识别结果: success={result.get('success')}, text长度={len(result.get('text', ''))}")
        
        # 清理临时文件
        try:
            os.unlink(tmp_path)
            logger.info("临时文件清理成功")
        except Exception as cleanup_error:
            logger.warning(f"临时文件清理失败: {cleanup_error}")
        
        if result["success"]:
            logger.info("识别成功，返回结果")
            return {
                "success": True,
                "text": result["text"],
                "image_url": image_url,
                "msg": "识别成功"
            }
        else:
            logger.warning(f"识别失败: {result['text']}")
            return {
                "success": False,
                "text": "",
                "image_url": image_url,
                "msg": result["text"]
            }
            
    except Exception as e:
        logger.error(f"处理图片时发生异常: {str(e)}", exc_info=True)
        return {
            "success": False,
            "text": "",
            "image_url": "",
            "msg": f"图片处理失败: {str(e)}"
        }

@app.post("/api/generate_tags")
async def generate_tags_api(request: GenerateTagsRequest):
    """生成标签"""
    logger.info(f"生成标签请求: text长度={len(request.text)}")
    try:
        result = generate_tags(request.text)
        logger.info(f"标签生成结果: success={result['success']}, tags={result.get('tags', [])}")
        return {
            "success": result["success"],
            "tags": result["tags"],
            "msg": "标签生成成功" if result["success"] else result["text"]
        }
    except Exception as e:
        logger.error(f"标签生成异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"标签生成失败: {str(e)}")

@app.post("/api/publish_note")
async def publish_note_api(request: PublishNoteRequest):
    """发布笔记到flomo"""
    logger.info(f"发布笔记请求: text长度={len(request.text)}, tags={request.tags}")
    try:
        result = publish_to_flomo(request.text, request.tags, request.image_urls)
        logger.info(f"发布结果: success={result['success']}")
        return {
            "success": result["success"],
            "msg": result["msg"]
        }
    except Exception as e:
        logger.error(f"发布笔记异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"发布失败: {str(e)}")

@app.get("/")
async def root():
    return {"message": "笔记Agent API服务正在运行"}

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"收到请求: {request.method} {request.url}")
    logger.info(f"请求头: {dict(request.headers)}")
    
    response = await call_next(request)
    
    logger.info(f"响应状态码: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 