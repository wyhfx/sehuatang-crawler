#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sehuatang 帖子解析器
从 Sehuatang 帖子页面提取番号、标题、容量、是否有码、图片、磁力链接等信息
"""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from utils.translator import Translator
from enrichment.providers.provider_metatube import MetaTubeProvider

class SehuatangParser:
    def __init__(self, settings_manager=None):
        self.settings_manager = settings_manager
        self.translator = Translator(settings_manager)
        self.metatube_provider = MetaTubeProvider(settings_manager=settings_manager)
    
    def contains_chinese(self, text: str) -> bool:
        """判断文本是否包含中文"""
        return bool(re.search(r"[\u4e00-\u9fff]", text or ""))
    
    def parse_post(self, html: str, source_url: str = "") -> Dict:
        """解析 Sehuatang 帖子页面"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 提取标题
        title_elem = soup.find("title")
        title = title_elem.text.strip() if title_elem else ""
        
        # 提取正文
        post_body = soup.find("td", {"class": "t_f"})
        text = post_body.get_text(" ", strip=True) if post_body else ""
        
        # 提取番号
        code = self._extract_code(title + " " + text)
        
        # 提取容量
        size = self._extract_size(text)
        
        # 判断是否有码
        is_uncensored = self._is_uncensored(title + " " + text)
        
        # 提取图片
        images = self._extract_images(post_body)
        
        # 提取磁力链接
        magnets = self._extract_magnets(text)
        
        # 构建基础结果
        result = {
            "code": code,
            "title": title,
            "size": size,
            "is_uncensored": is_uncensored,
            "images": images,
            "magnets": magnets,
            "source_url": source_url,
            "raw_text": text[:500] + "..." if len(text) > 500 else text  # 保存部分原始文本用于调试
        }
        
        # 进行中文化处理
        result = self._enrich_metadata(result)
        
        return result
    
    def _extract_code(self, text: str) -> Optional[str]:
        """提取番号"""
        # 匹配常见的番号格式
        patterns = [
            r"([A-Z]{2,10}-\d{2,5})",  # 标准格式：ABP-123
            r"([A-Z]{2,10}\s+\d{2,5})",  # 空格分隔：ABP 123
            r"([A-Z]{2,10}_\d{2,5})",   # 下划线分隔：ABP_123
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                code = match.group(1)
                # 标准化格式
                code = re.sub(r"[\s_]", "-", code.upper())
                return code
        
        return None
    
    def _extract_size(self, text: str) -> Optional[str]:
        """提取文件大小"""
        # 匹配 GB/MB 格式
        size_match = re.search(r"(\d+(?:\.\d+)?)\s*(GB|MB|G|M)", text, re.IGNORECASE)
        if size_match:
            size = size_match.group(1)
            unit = size_match.group(2).upper()
            # 标准化单位
            if unit in ["G", "GB"]:
                return f"{size}GB"
            elif unit in ["M", "MB"]:
                return f"{size}MB"
        return None
    
    def _is_uncensored(self, text: str) -> bool:
        """判断是否为无码"""
        uncensored_keywords = [
            "无码", "無碼", "uncensored", "无修正", "無修正",
            "流出", "破解", "破解版", "破解版流出"
        ]
        return any(keyword in text for keyword in uncensored_keywords)
    
    def _extract_images(self, post_body) -> List[str]:
        """提取图片链接"""
        images = []
        if post_body:
            for img in post_body.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src and src.startswith(("http://", "https://")):
                    images.append(src)
        return images
    
    def _extract_magnets(self, text: str) -> List[str]:
        """提取磁力链接"""
        # 匹配磁力链接
        magnet_pattern = r"(magnet:\?xt=urn:btih:[0-9A-Fa-f]{40,})"
        magnets = re.findall(magnet_pattern, text, re.IGNORECASE)
        return list(set(magnets))  # 去重
    
    def _enrich_metadata(self, parsed: Dict) -> Dict:
        """中文化处理：优先使用中文，否则从数据源获取，最后翻译"""
        code = parsed.get("code")
        title = parsed.get("title", "")
        
        if not code:
            return parsed
        
        # 如果标题已经包含中文，直接使用
        if self.contains_chinese(title):
            parsed["title_cn"] = title
            return parsed
        
        # 从 MetaTube 获取元数据
        try:
            meta = self.metatube_provider.lookup(code)
            if meta:
                # 优先使用中文字段
                parsed["title_cn"] = getattr(meta, "_title_cn", None) or meta.title
                parsed["studio"] = meta.studio
                parsed["studio_cn"] = getattr(meta, "_studio_cn", None)
                parsed["actresses"] = meta.actresses
                parsed["actresses_cn"] = getattr(meta, "_actresses_cn", None)
                parsed["tags"] = meta.tags
                parsed["tags_cn"] = getattr(meta, "_tags_cn", None)
                parsed["release_date"] = meta.release_date
                parsed["cover_url"] = meta.cover_url
                parsed["source"] = "metatube"
                
                # 如果 MetaTube 返回的标题也不是中文，尝试翻译
                if not self.contains_chinese(parsed["title_cn"]):
                    translated_title = self.translator.translate(parsed["title_cn"], src="ja", tgt="zh")
                    if translated_title and translated_title != parsed["title_cn"]:
                        parsed["title_cn"] = translated_title
                
                # 翻译标签
                if parsed.get("tags") and not any(self.contains_chinese(t) for t in parsed["tags"]):
                    translated_tags = self.translator.translate_list(parsed["tags"], src="ja", tgt="zh")
                    if translated_tags:
                        parsed["tags_cn"] = translated_tags
                
                # 翻译厂牌
                if parsed.get("studio") and not self.contains_chinese(parsed["studio"]):
                    translated_studio = self.translator.translate(parsed["studio"], src="ja", tgt="zh")
                    if translated_studio and translated_studio != parsed["studio"]:
                        parsed["studio_cn"] = translated_studio
            else:
                # MetaTube 没有数据，直接翻译原始标题
                if title:
                    translated_title = self.translator.translate(title, src="ja", tgt="zh")
                    if translated_title and translated_title != title:
                        parsed["title_cn"] = translated_title
                    else:
                        parsed["title_cn"] = title
        except Exception as e:
            # 出错时，尝试直接翻译原始标题
            if title:
                translated_title = self.translator.translate(title, src="ja", tgt="zh")
                if translated_title and translated_title != title:
                    parsed["title_cn"] = translated_title
                else:
                    parsed["title_cn"] = title
        
        return parsed

def parse_sehuatang_post(html: str, source_url: str = "", settings_manager=None) -> Dict:
    """便捷函数：解析 Sehuatang 帖子"""
    parser = SehuatangParser(settings_manager)
    return parser.parse_post(html, source_url)
