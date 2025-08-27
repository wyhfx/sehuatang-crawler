# utils/translator.py
import os, time, hashlib, random
from typing import Optional, List

class Translator:
    """多后端可选；没配任何密钥时，translate() 直接返回原文"""
    def __init__(self, settings_manager=None):
        if settings_manager:
            # 从设置管理器获取配置
            translate_config = settings_manager.get_translate_config()
            self.provider = translate_config.get("trans_provider", "") if translate_config.get("translate_enabled", "false") == "true" else ""
            self.baidu_appid = translate_config.get("baidu_appid", "")
            self.baidu_key = translate_config.get("baidu_key", "")
        else:
            # 回退到环境变量
            self.provider = os.getenv("TRANS_PROVIDER", "")
            self.baidu_appid = os.getenv("BAIDU_APPID", "")
            self.baidu_key = os.getenv("BAIDU_KEY", "")
        # 你也可以按需添加其它家的密钥

    def translate(self, text: Optional[str], src="ja", tgt="zh") -> Optional[str]:
        if not text: return text
        if self.provider == "baidu" and self.baidu_appid and self.baidu_key:
            try:
                import requests
                salt = str(random.randint(10000, 99999))
                sign = (self.baidu_appid + text + salt + self.baidu_key).encode("utf-8")
                sign = hashlib.md5(sign).hexdigest()
                r = requests.post(
                    "https://fanyi-api.baidu.com/api/trans/vip/translate",
                    data={"q": text, "from": src, "to": tgt,
                          "appid": self.baidu_appid, "salt": salt, "sign": sign},
                    timeout=8,
                )
                js = r.json()
                if "trans_result" in js and js["trans_result"]:
                    return js["trans_result"][0].get("dst") or text
            except Exception:
                return text
        # 未配置或失败 -> 原文
        return text

    def translate_list(self, items: Optional[List[str]], src="ja", tgt="zh") -> Optional[List[str]]:
        if not items: return items
        out = []
        for s in items:
            t = self.translate(s, src, tgt)
            if t: out.append(t)
        return out
