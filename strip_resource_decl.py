# -*- coding: utf-8 -*-
"""从全书各章开头的『资源与可用性声明』块中移除重复声明。

分两类处理：
  A 类（含 Zenodo 归档 / 算子开源口径 / 腾讯文档 / Gemini 存档 链接）→ 整块删除
  B 类（仅「本框架构建于…」引语 + DOI 引用清单 + 结尾句）→ 删掉引语与结尾句，
        保留 DOI 引用清单（必要时补一行「相关引用：」标签）

保留文件原有 BOM 状态；仅动前 45 行，并把连续空行收敛为一个。
用法： python _tmp_decl_strip.py            # 干跑，只报告
       python _tmp_decl_strip.py --apply    # 落盘
"""
import pathlib
import re
import sys

APPLY = "--apply" in sys.argv
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MARK = re.compile(
    r"资源\s*[与可]{0,3}\s*可用性声明"
    r"|资源可用性声明"
    r"|资源与可获得性声明"
    r"|[Rr]esources?\s*(?:&|and|、)?\s*[Aa]vailability\s*Statement"
    r"|[Rr]esource\s*[-–]?\s*[Aa]vailability\s*Statement"
    r"|\[Resource and Availability Statement\]"
    r"|全部理论资料(?:均)?(?:归档|存档)于"
    r"|[Tt]heoretical materials\s+[^.]{0,60}(?:archived|Zenodo)"
    r"|本框架(?:基于|构建于)状态.?.?关系熵"
    r"|[Tt]his framework is (?:built|constructed)\s+(?:upon|based)"
    r"|built based on State"
)
TERM = re.compile(r"信息统计学|information statistics")
A_KW = re.compile(r"开源|open.source|Zenodo|腾讯|Tencent|Gemini")
FRAME = re.compile(r"^\s*>?\s*(?:本框架构建于状态|This framework is built upon State)")
CITE = re.compile(
    r"引用基准|历史引用|关联引用|参考文献|Reference baseline|Historical references"
    r"|Related references|Associated references|DOI|doi\.org|https?://",
    re.IGNORECASE,
)
STOP_QUOTE = re.compile(
    r"^\s*>\s*(?:\*\*)?(?:备注|说明|注：|注意|文档用途|Document purpose|Remark|Note|Document scope|"
    r"Document positioning|框架定位|Framework Positioning|阅读提示|Reading Note|方法论声明|"
    r"Methodological Statement)"
)
BLANKISH = re.compile(r"^\s*(?:>\s*)?$")


def is_cite_quote(line: str) -> bool:
    s = line.strip()
    if not s.startswith(">") or STOP_QUOTE.match(line):
        return False
    return bool(CITE.search(s))


def find_region(lines):
    n = len(lines)
    i0 = None
    for i in range(min(25, n)):
        if MARK.search(lines[i]):
            i0 = i
            break
    if i0 is None:
        return None
    while i0 < n and re.search(r"作者|Author|版本|Version", lines[i0]):
        i0 += 1
    i1 = None
    for i in range(i0, min(i0 + 30, n)):
        if TERM.search(lines[i]):
            i1 = i
            break
    if i1 is None:
        return None
    k = i1 + 1
    while k < n:
        if BLANKISH.match(lines[k]):
            k2 = k
            while k2 < n and BLANKISH.match(lines[k2]):
                k2 += 1
            if k2 < n and is_cite_quote(lines[k2]):
                k = k2
                continue
            break
        if is_cite_quote(lines[k]):
            k += 1
            continue
        break
    return i0, k - 1


def strip_file(path: pathlib.Path, report_only=True):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines()
    reg = find_region(lines)
    if reg is None:
        return None
    i0, i1 = reg
    body = "\n".join(lines[i0 : i1 + 1])
    group = "A" if A_KW.search(body) else "B"

    if group == "A":
        new = lines[:i0] + lines[i1 + 1 :]
        note = f"整块删除 L{i0+1}-L{i1+1}（{i1-i0+1} 行）"
    else:
        keep = []
        for i in range(i0, i1 + 1):
            L = lines[i]
            if FRAME.match(L) or TERM.search(L):
                continue
            keep.append(L)
        has_label = any(re.search(r"引用|Reference", L) for L in keep)
        if not has_label:
            cjk = re.search(r"[\u4e00-\u9fff]", body) is not None
            label = "> 相关引用：" if cjk else "> Related references:"
            for idx, L in enumerate(keep):
                if "http" in L:
                    keep.insert(idx, label)
                    break
        # 去掉残留的空引语行 > 与首尾空行
        while keep and BLANKISH.match(keep[0]):
            keep.pop(0)
        while keep and BLANKISH.match(keep[-1]):
            keep.pop()
        new = lines[:i0] + keep + lines[i1 + 1 :]
        note = f"保留引用清单，删引语+结尾句 L{i0+1}-L{i1+1}"

    # 只在前 45 行内收敛连续空行
    out, limit = [], max(45, len(lines[:i0]) + 40)
    for L in new:
        if len(out) < limit and BLANKISH.match(L) and out and BLANKISH.match(out[-1]) and L.strip() == "" and out[-1].strip() == "":
            continue
        out.append(L)
    while out and out[-1] == "":
        out.pop()
    new_text = "\n".join(out) + "\n"

    if new_text != text:
        if APPLY:
            data = ("\ufeff" if bom else "") + new_text
            path.write_bytes(data.encode("utf-8"))
        return group, note, len(lines), len(out)


def main():
    targets = []
    for fn in ("file_order_C.txt", "file_order_E.txt"):
        for raw in pathlib.Path(fn).read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if raw and not raw.startswith("#"):
                targets.append(raw)
    # 湍流论文在附件目录的镜像副本（audit.py 依赖，需与章节逐字节一致）
    targets += [
        "./5-Appendixs/Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence/papers/main_CN.md",
        "./5-Appendixs/Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence/papers/main_EN.md",
    ]

    cnt = {"A": 0, "B": 0}
    changed, skipped = [], []
    for name in targets:
        p = pathlib.Path(name)
        if not p.exists():
            skipped.append((name, "缺失"))
            continue
        r = strip_file(p, report_only=not APPLY)
        if r is None:
            continue
        group, note, before, after = r
        cnt[group] += 1
        changed.append((name, group, note, before, after))
        print(f"[{group}] {name}\n      {note}   行数 {before} -> {after}")

    print()
    for name, why in skipped:
        print(f"[跳过] {name} — {why}")
    tail = "（已落盘）" if APPLY else "（干跑，未落盘）"
    print(f"\n=== A 类 {cnt['A']} 个 / B 类 {cnt['B']} 个，共 {cnt['A'] + cnt['B']} 个文件 {tail} ===")


if __name__ == "__main__":
    main()
