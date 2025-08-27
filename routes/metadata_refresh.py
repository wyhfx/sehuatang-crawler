# routes/metadata_refresh.py
import re, json
from fastapi import APIRouter, HTTPException
from db import SessionLocal
from models import CodeMetadata
from utils.translator import Translator

router = APIRouter()

def norm_code(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", s.upper())

@router.post("/api/metadata/{code}/refresh-translate")
def refresh_translate(code: str):
    db = SessionLocal()
    try:
        row = db.query(CodeMetadata).filter(CodeMetadata.code_norm == norm_code(code)).first()
        if not row: raise HTTPException(status_code=404, detail="not found")
        trans = Translator()

        # 只翻译缺失的中文字段
        def has_cjk(s): 
            import re as _re
            return bool(s and _re.search(r"[\u3040-\u30ff\u4e00-\u9fa5]", s))

        if hasattr(row,"title_cn") and (not row.title_cn) and has_cjk(row.title):
            row.title_cn = trans.translate(row.title, src="ja", tgt="zh")
        if hasattr(row,"studio_cn") and (not row.studio_cn) and has_cjk(row.studio or ""):
            row.studio_cn = trans.translate(row.studio, src="ja", tgt="zh")

        # tags
        tags = []
        try: tags = json.loads(row.tags or "[]")
        except: pass
        if hasattr(row,"tags_cn"):
            if not row.tags_cn:
                tags_cn = trans.translate_list(tags, src="ja", tgt="zh")
                row.tags_cn = json.dumps(tags_cn or [], ensure_ascii=False)

        db.commit()
        return {"ok": True}
    finally:
        db.close()
