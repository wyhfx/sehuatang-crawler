#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaTube HTTP 适配器：
- 支持多候选搜索端点（不同部署/版本路径可能不同）
- 支持多字段名容错（title_cn / title_zh / title …）
- 仅依赖后端的只读查询，无需改动 MetaTube
"""

import os, re, requests
from typing import Optional, Dict, Any, List

class MetaResult:
    def __init__(self, **kw): self.__dict__.update(kw)

def _strip(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", s.upper())

def _to_display(code_norm: str) -> str:
    m = re.match(r"([A-Z]{2,8})(\d+)$", code_norm)
    return f"{m.group(1)}-{m.group(2)}" if m else code_norm

class MetaTubeProvider:
    name = "metatube"

    def __init__(self, base_url: Optional[str] = None, timeout: int = 12, settings_manager=None):
        self.base = (base_url or os.getenv("METATUBE_URL") or "http://localhost:8080").rstrip("/")
        self.timeout = timeout
        self.movies_path = "/v1/movies/search"
        self.actors_path = "/v1/actors/search"
        
        # 从设置管理器获取配置
        if settings_manager:
            datasource_config = settings_manager.get_datasource_config()
            self.base = (base_url or datasource_config.get("metatube_url") or "http://localhost:8080").rstrip("/")
            self.provider = datasource_config.get("metatube_provider", "")
            self.fallback = datasource_config.get("metatube_fallback", "true").lower() == "true"
        else:
            # 回退到环境变量
            self.provider = os.getenv("METATUBE_PROVIDER", "")
            self.fallback = os.getenv("METATUBE_FALLBACK", "true").lower() == "true"

        self.session = requests.Session()
        self.session.trust_env = True  # NO_PROXY 生效

    def _get(self, path: str, params: dict) -> dict:
        url = f"{self.base}{path}"
        # 附带可选 provider/fallback
        if self.provider: params.setdefault("provider", self.provider)
        params.setdefault("fallback", str(self.fallback).lower())
        r = self.session.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {}

    def _parse_names(self, arr) -> (List[str], List[str]):
        cn, en = [], []
        if isinstance(arr, str):
            arr = re.split(r"[，,;/\s]+", arr.strip())
        for a in (arr or []):
            if isinstance(a, dict):
                c = a.get("name_cn") or a.get("cn") or a.get("zh") or a.get("name_zh")
                e = a.get("name") or a.get("name_en") or a.get("en")
            else:
                s = str(a)
                c = s if re.search(r"[\u4e00-\u9fa5]", s) else None
                e = None if c else s
            if c: cn.append(c.strip())
            if e: en.append(e.strip())
        return list(dict.fromkeys(cn)), list(dict.fromkeys(en))

    def _parse_tags(self, arr) -> (List[str], List[str]):
        cn, en = [], []
        for t in (arr or []):
            if isinstance(t, dict):
                c = t.get("name_cn") or t.get("cn") or t.get("zh")
                e = t.get("name") or t.get("name_en") or t.get("en")
            else:
                s = str(t)
                c = s if re.search(r"[\u4e00-\u9fa5]", s) else None
                e = None if c else s
            if c: cn.append(c)
            if e: en.append(e)
        return list(dict.fromkeys(cn)), list(dict.fromkeys(en))

    def lookup(self, code_norm: str) -> Optional[MetaResult]:
        code_norm = _strip(code_norm)
        terms = [code_norm]
        m = re.match(r"([A-Z]{2,8})(\d+)$", code_norm)
        if m:
            terms += [f"{m.group(1)}-{m.group(2)}",
                      f"{m.group(1)}-{m.group(2).zfill(4)}",
                      f"{m.group(1)} {m.group(2)}"]

        for q in dict.fromkeys(terms):
            js = self._get(self.movies_path, {"q": q})
            items = js.get("data") if isinstance(js, dict) else None
            if not items:
                continue

            # 简单打分：标题/别名包含番号优先
            def score(it: Dict[str, Any]) -> int:
                t = " ".join([str(it.get("title_cn") or ""),
                              str(it.get("title") or ""),
                              str(it.get("aliases") or "")])
                return 5 if code_norm in _strip(t) else 1
            items.sort(key=score, reverse=True)
            item = items[0]

            title_cn = item.get("title_cn") or item.get("title_zh") or item.get("title_chs") or item.get("title_chi")
            title = item.get("title") or item.get("title_en") or title_cn
            studio_cn = item.get("studio_cn") or item.get("label_cn")
            studio = item.get("studio") or item.get("studio_en") or studio_cn

            acts_cn, acts_en = self._parse_names(item.get("performers") or item.get("actors") or item.get("cast"))
            tags_cn, tags_en = self._parse_tags(item.get("tags") or item.get("genres"))

            cover = (item.get("cover_url") or item.get("poster_url") or
                     (item.get("images", {}).get("poster") if isinstance(item.get("images"), dict) else None))
            release_date = item.get("release_date") or item.get("date") or item.get("publish_date")

            res = MetaResult(
                code_norm=_strip(code_norm),
                code_display=_to_display(code_norm),
                title=title,                     # 英文/日文
                actresses=acts_en or None,       # 英文
                studio=studio,
                release_date=release_date,
                tags=tags_en or None,            # 英文
                cover_url=cover,
                source="metatube",
            )
            # ✅ 中文字段，如果后端提供
            res._title_cn = title_cn
            res._actresses_cn = acts_cn
            res._tags_cn = tags_cn
            res._studio_cn = studio_cn
            return res

        return None

