# -*- coding: utf-8 -*-
"""
fix_gamma_latency.py —— 修复 SRE 引力管线中 GAMMA_LATENCY 的数值不一致
============================================================================
排查结论（2026-10）：
  - 论文与全项目其它代码统一取 γ = 0.0585（= 1/(2πe) ≈ 0.058550）；
  - 唯一离群点是引力数值管线 sre_full_framework.py 的配置常量
        "GAMMA_LATENCY": 0.05
    本脚本把该常量就地修正为 0.0585，使代码与论文一致。

安全约束（严格遵守“主仓库只读”硬约束）：
  - 默认 dry-run：只读、只打印 diff，绝不落盘；
  - 仅当显式传入 --apply 时才写回仓库文件；
  - 无论何种模式，都会在脚本所在目录生成 gamma_latency_fix.patch（可用 git apply）；
  - 全程只改这一个 .py 常量，不触碰任何 .md 论文文件。

用法：
  python fix_gamma_latency.py            # 预演：显示将发生的改动（默认）
  python fix_gamma_latency.py --apply    # 真正写回仓库文件
"""

import re
import sys
import argparse
import difflib
from pathlib import Path

# ---- 目标文件（位于主仓库内；只读约束下默认不写） ----
REPO_ROOT = Path(r"d:\mywork\Status-Relational-Entropy-SRE-Dynamics-The-Book-of-the-Void")
TARGET_REL = (
    "5-Appendixs/Emergence_of_Multidimensional_Spacetime_and_Dynamical_Gravity_"
    "via_Regularized_Causal_Information_Networks/sre_full_framework.py"
)
TARGET = REPO_ROOT / TARGET_REL

# ---- 修复目标 ----
KEY = '"GAMMA_LATENCY"'
NEW_VALUE = "0.0585"  # = 1/(2πe)，与论文及全项目一致
# 匹配： 行首空白 "GAMMA_LATENCY" : 数值
PATTERN = re.compile(r'(^[ \t]*"GAMMA_LATENCY"[ \t]*:[ \t]*)([0-9]+(?:\.[0-9]+)?)', re.M)

PATCH_OUT = Path(__file__).with_name("gamma_latency_fix.patch")


def load_text(path: Path) -> str:
    """读取文本：newline='' 关闭换行翻译，原样保留 CRLF/LF，写回时不破坏行尾。"""
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def make_patch(old: str, new: str) -> str:
    """生成统一 diff（LF 行尾，a/ b/ 前缀，git apply -p1 可直接用）。"""
    diff = difflib.unified_diff(
        old.splitlines(),
        new.splitlines(),
        fromfile="a/" + TARGET_REL,
        tofile="b/" + TARGET_REL,
        lineterm="",
    )
    return "\n".join(diff) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="修复 GAMMA_LATENCY 数值不一致")
    ap.add_argument("--apply", action="store_true", help="真正写回仓库文件（默认仅预演）")
    args = ap.parse_args()

    # 1) 前置校验
    if not TARGET.is_file():
        print(f"[FAIL] 目标文件不存在：{TARGET}")
        return 2

    text = load_text(TARGET)

    # 2) 定位赋值行
    hits = list(PATTERN.finditer(text))
    if len(hits) == 0:
        if KEY in text and NEW_VALUE in text:
            print(f"[OK] 未发现旧值，且已含 {NEW_VALUE}：无需修复。")
            return 0
        print("[FAIL] 未找到 GAMMA_LATENCY 赋值行，脚本终止（避免误改）。")
        return 2
    if len(hits) > 1:
        print(f"[FAIL] 发现 {len(hits)} 处 GAMMA_LATENCY 赋值，超出预期，终止。")
        return 2

    m = hits[0]
    cur_value = m.group(2)
    line_no = text[: m.start()].count("\n") + 1
    print(f"[INFO] 命中第 {line_no} 行：{KEY} = {cur_value}")

    # 3) 幂等检查
    if cur_value == NEW_VALUE:
        print(f"[OK] 已是目标值 {NEW_VALUE}，无需修复。")
        return 0

    # 4) 生成新文本与补丁
    new_text = text[: m.start(2)] + NEW_VALUE + text[m.end(2):]
    patch = make_patch(text, new_text)
    with open(PATCH_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(patch)
    print(f"[INFO] 补丁已写出：{PATCH_OUT}")
    print("-" * 64)
    print(patch.rstrip("\n"))
    print("-" * 64)

    # 5) 落盘（仅在 --apply 时执行）
    if not args.apply:
        print("[DRY-RUN] 未写回仓库；加 --apply 才会真正修改。")
        print("SUCCESS: dry-run 完成（补丁已生成，仓库未被改动）")
        return 0

    with open(TARGET, "w", encoding="utf-8", newline="") as f:
        f.write(new_text)

    # 6) 回读校验
    check = load_text(TARGET)
    fixed = (
        len(PATTERN.findall(check)) == 1
        and f'{KEY}: {cur_value}' not in check
        and NEW_VALUE in check
    )
    if fixed:
        print(f"[OK] 已写回并校验通过：{KEY} = {NEW_VALUE}")
        print("SUCCESS: 修复完成，仓库文件已更新（建议先 git diff 复核再提交）")
        return 0
    print("[FAIL] 写回后校验未通过，请人工检查。")
    return 3


if __name__ == "__main__":
    sys.exit(main())