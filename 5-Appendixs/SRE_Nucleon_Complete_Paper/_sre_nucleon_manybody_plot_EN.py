# -*- coding: utf-8 -*-
"""英文版第 12 章配图驱动（复用中文脚本的绘图核心，仅切换语言标签）。"""
import sys
import _sre_nucleon_manybody_plot as core

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

if __name__ == "__main__":
    core.main("en")
