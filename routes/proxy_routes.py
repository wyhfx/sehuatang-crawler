# routes/proxy_routes.py
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ProxyTestRequest(BaseModel):
    proxy_url: str

@router.post("/api/proxy/test")
def test_proxy(request: ProxyTestRequest):
    """测试代理连接"""
    try:
        # 配置代理
        proxies = {
            'http': request.proxy_url,
            'https': request.proxy_url
        }
        
        # 测试连接（使用一个简单的测试网站）
        response = requests.get(
            'http://httpbin.org/ip',
            proxies=proxies,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "代理连接测试成功",
                "data": {
                    "ip": response.json().get("origin", "未知"),
                    "proxy_url": request.proxy_url
                }
            }
        else:
            return {
                "success": False,
                "message": f"代理连接测试失败，状态码: {response.status_code}"
            }
            
    except requests.exceptions.ProxyError:
        return {
            "success": False,
            "message": "代理连接失败，请检查代理地址是否正确"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "代理连接超时，请检查网络连接"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "无法连接到代理服务器"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"代理测试失败: {str(e)}"
        }
