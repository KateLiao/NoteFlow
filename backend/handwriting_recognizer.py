import os
from openai import OpenAI
from typing import Optional, Dict, List
import requests
import json
import base64
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 配置与初始化 - 使用环境变量（安全）
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

FLMO_WEBHOOK_URL = os.getenv("FLMO_WEBHOOK_URL")

# 验证必要的环境变量
if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY environment variable is required")
if not FLMO_WEBHOOK_URL:
    raise ValueError("FLMO_WEBHOOK_URL environment variable is required")

# Prompt模板管理
PROMPT_TEMPLATES = {
    "default": "请识别图片中的所有手写文字内容，只返回手写文字部分，不要描述图片。如果图片中没有可识别的手写文字，则返回【未识别到手写文字】",
    "note": "请帮我提取这张图片中的手写笔记内容，忽略印刷体和背景。",
}

TAG_PROMPT_TEMPLATE = (
    "请阅读以下笔记内容，并根据其可能被使用的具体场景或项目，为其生成 3 个标签。\n"
    "要求：\n"
    "1.标签应反映笔记的潜在用途，而非信息来源。\n"
    "2.避免使用如\"读书笔记\"、\"播客\"等来源类标签。\n"
    "3.每个标签应简洁明了，最多包含 3 个词。\n"
    "4.标签应有助于在未来的项目中快速检索和应用该笔记内容。\n"
    "笔记内容：\n{content}"
)

def get_prompt(template_name: str = "default") -> str:
    return PROMPT_TEMPLATES.get(template_name, PROMPT_TEMPLATES["default"])

def get_tag_prompt(content: str) -> str:
    return TAG_PROMPT_TEMPLATE.format(content=content)

def image_to_base64(image_path: str) -> str:
    """将图片文件转换为base64编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 通义千问API调用封装
def recognize_handwriting(image_input: str, prompt_template: str = "default") -> Dict:
    client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL)
    prompt = get_prompt(prompt_template)
    try:
        # 判断输入是URL还是文件路径
        if image_input.startswith(('http://', 'https://')):
            # 公网URL
            image_content = {"type": "image_url", "image_url": {"url": image_input}}
        elif image_input.startswith('file://'):
            # 本地文件路径，转换为base64
            file_path = image_input.replace('file://', '')
            base64_image = image_to_base64(file_path)
            image_content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        else:
            # 直接作为文件路径处理
            base64_image = image_to_base64(image_input)
            image_content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        
        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                image_content
            ]}]
        )
        data = completion.model_dump()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not text.strip() or "未识别到手写文字" in text:
            return {"success": False, "text": "未检测到手写内容。", "raw": data}
        return {"success": True, "text": text.strip(), "raw": data}
    except Exception as e:
        return {"success": False, "text": f"识别失败: {str(e)}", "raw": None}

# 标签生成模块
def generate_tags(note_content: str) -> Dict:
    client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL)
    prompt = get_tag_prompt(note_content)
    try:
        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt}
            ]}]
        )
        data = completion.model_dump()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # 改进的标签解析逻辑
        import re
        
        # 将文本按换行、逗号、分号等分割
        tags = re.split(r'[\n,;，；]+', text)
        
        # 处理每个标签
        cleaned_tags = []
        for tag in tags:
            # 去除空白
            tag = tag.strip()
            if not tag:
                continue
                
            # 去除序号、点号、星号等
            tag = re.sub(r'^[\d\.\*\-\+]+\s*', '', tag)
            
            # 去除markdown格式符号 **
            tag = re.sub(r'\*\*([^*]+)\*\*', r'\1', tag)
            
            # 去除其他格式符号
            tag = re.sub(r'[#\*\-\+\s]*([^\*\#\-\+]+)', r'\1', tag).strip()
            
            # 过滤掉无效标签
            if tag and len(tag) > 1 and not any(keyword in tag for keyword in [
                '标签建议', '标签：', '建议', '以下', '标签', '：', 'tag', 'Tag'
            ]):
                # 限制标签长度
                if len(tag) <= 10:  # 最多10个字符
                    cleaned_tags.append(tag)
        
        # 只取前3个有效标签
        tags = cleaned_tags[:3]
        
        if not tags:
            return {"success": False, "tags": [], "raw": data, "text": text}
        return {"success": True, "tags": tags, "raw": data, "text": text}
    except Exception as e:
        return {"success": False, "tags": [], "raw": None, "text": f"标签生成失败: {str(e)}"}

def publish_to_flomo(text: str, tags: list, image_urls: list) -> dict:
    # 标签格式化：#标签名 空格分隔
    tag_str = ' '.join([f'#{t.lstrip("#")}' for t in tags])
    content = f'{text.strip()} {tag_str}'.strip()
    # 图片最多9个
    image_urls = image_urls[:9]
    data = {
        'content': content,
        'image_urls': json.dumps(image_urls, ensure_ascii=False)
    }
    try:
        resp = requests.post(FLMO_WEBHOOK_URL, data=data, timeout=10)
        if resp.status_code == 200:
            return {'success': True, 'msg': '同步成功'}
        else:
            return {'success': False, 'msg': f'同步失败: {resp.text}'}
    except Exception as e:
        return {'success': False, 'msg': f'同步异常: {str(e)}'}

# 串联主流程示例（含flomo同步）
def main_process_with_flomo(image_url: str, user_text: str = None, user_tags: list = None, user_images: list = None) -> dict:
    # 1. 识别手写内容
    recog = recognize_handwriting(image_url)
    if not recog["success"]:
        return {"success": False, "step": "recognize", "msg": recog["text"]}
    # 2. 生成标签
    tag_result = generate_tags(recog["text"])
    tags = tag_result["tags"] if tag_result["success"] else []
    # 3. 用户可编辑文本和标签
    final_text = user_text if user_text is not None else recog["text"]
    final_tags = user_tags if user_tags is not None else tags
    final_images = user_images if user_images is not None else [image_url]
    # 4. 发布到flomo
    flomo_result = publish_to_flomo(final_text, final_tags, final_images)
    return {
        "success": flomo_result["success"],
        "text": final_text,
        "tags": final_tags,
        "images": final_images,
        "msg": flomo_result["msg"]
    }

# 示例用法
def test_main_with_flomo():
    #有手写字体的图
    #test_url = "https://openplantform.oss-cn-beijing.aliyuncs.com/demonstration/ocr-hr/handwriting-recognition-chinese-one.jpg?OSSAccessKeyId=LTAI4FvBYgUM9wyFK4wa9nvy&Expires=4741744502&Signature=ZI6p5nkNDm4YuyB6rqU55hjPJ38%3D"
    
    #没有手写字体的图
    test_url="https://taise.org.tw/userfiles/images/CCS/%E9%9B%BB%E5%AD%90%E5%A0%B1%E5%9C%96%E7%89%87/%E6%B5%B7%E6%B4%8B.jpeg"
    result = main_process_with_flomo(test_url)
    print(result)

if __name__ == "__main__":
    test_main_with_flomo() 