#!usrbinenv python3
import os
import re
import subprocess
import sys

def check_markdown_heading_warnings(filepath str)
    扫描md，输出标题风险警告，不修改源文件
    with open(filepath, r, encoding=utf‑8) as f
        content = f.read()
    h1_pattern = re.compile(r^#s+, re.MULTILINE)
    h1_hits = h1_pattern.findall(content)
    cnt = len(h1_hits)
    warns = []
    if cnt == 0
        warns.append(f⚠️ {os.path.basename(filepath)}  文件未发现一级标题 # )
    if cnt  1
        warns.append(f⚠️ {os.path.basename(filepath)}  文件内部检测到 {cnt} 个 # H1，一个章节只允许1个H1！)
    for w in warns
        print(w)
    return warns

def main()
    order_list_file = file_order_C.txt
    output_pdf = SRE‑Dynamics‑Book‑v1.0.pdf
    template_file = eisvogel.latex

    # 读取章节顺序
    md_inputs = []
    with open(order_list_file, r, encoding=utf‑8) as f
        for line in f
            line = line.strip()
            if not line or line.startswith(#)
                continue
            md_inputs.append(line)

    # 校验文件存在 + 标题检查
    missing = []
    for fn in md_inputs
        if not os.path.exists(fn)
            missing.append(fn)
        else
            check_markdown_heading_warnings(fn)
    if missing
        print(n❌ 以下输入文件找不到：)
        for f in missing
            print(f   {f})
        sys.exit(1)

    if not os.path.exists(template_file)
        print(fn❌ 找不到模板文件 {template_file}，请放到当前目录！)
        sys.exit(1)

    print(fn✅ 将编译 {len(md_inputs)} 个章节，输出 → {output_pdf})
    print(-60)

    # 构造 pandoc 命令
    cmd = [
        pandoc,
        md_inputs,
        -o, output_pdf,
        --pdf-engine=xelatex,
        f--template={template_file},
        --toc,
        --toc-depth=3,
        --number‑sections,
        -V, CJKmainfont=Noto Sans CJK SC,
        -V, mainfont=Noto Sans CJK SC,
        -V, fontsize=11pt,
        -V, geometrymargin=2.2cm,
        -V, book=true,
        -V, title=Status‑Relational‑Entropy Dynamics — The Book of the Void,
        -V, author=Yue Lu,
        -V, date=2026‑08‑28,
        --listings,
        --highlight‑style=tango
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0
        print(n❌ Pandoc编译失败！)
        print(==== STDERR ====)
        print(result.stderr)
        sys.exit(result.returncode)
    else
        print(fn🎉 编译成功！输出文件：{output_pdf})

if __name__ == __main__
    main()
