import json
import os
from mangum import Mangum
from main import app

# 云函数处理器
handler = Mangum(app, lifespan="off")

def main_handler(event, context):
    """
    腾讯云函数入口点
    """
    return handler(event, context) 