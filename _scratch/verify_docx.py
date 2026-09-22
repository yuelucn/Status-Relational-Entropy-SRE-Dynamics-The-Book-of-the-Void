# -*- coding: utf-8 -*-
"""验证docx内容"""
import io, os
from docx import Document

p = r'C:\mywork\SRE-Dynamics\状态-关系熵（SRE）动力学_整理版.docx'
print('文件大小: %.1f KB' % (os.path.getsize(p) / 1024))

doc = Document(p)
paras = doc.paragraphs
print('段落数:', len(paras))
print('表格数:', len(doc.tables))

# 统计标题
headings = [pa for pa in paras if pa.style.name.startswith('Heading')]
print('标题数:', len(headings))
for h in headings[:25]:
    print(f'  [{h.style.name}] {h.text[:60]}')

# 检查数学公式（OMML）数量
import re
xml = doc.element.xml
math_count = xml.count('m:oMath')
print('OMML公式数:', math_count)

# 检查图片
inline_shapes = doc.inline_shapes
print('内嵌图片数:', len(inline_shapes))

# 统计文字量
total_chars = sum(len(pa.text) for pa in paras)
print('正文总字符:', total_chars)
