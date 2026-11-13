"""构建脚本：用计算器算出几个例子，生成静态网页 site/index.html。

CD 流水线会运行这个脚本，再把 site/ 文件夹发布到 GitHub Pages。
本地也可以直接运行：python build_site.py
"""

import html
import os
from datetime import UTC, datetime
from pathlib import Path

from calculator import add, divide, multiply, power, subtract

# 网页标题（CD 练习 5：改这里，推送后看网站自动更新）
TITLE = "我的 CI/CD 计算器"

# 网页输出到项目根目录下的 site/ 文件夹
OUTPUT_DIR = Path(__file__).parent / "site"


def examples() -> list[tuple[str, float]]:
    """网页上展示的例子：(算式, 计算结果)。"""
    return [
        ("2 + 3", add(2, 3)),
        ("10 - 4", subtract(10, 4)),
        ("3 × 4", multiply(3, 4)),
        ("7 × 8", multiply(7, 8)),
        ("10 ÷ 4", divide(10, 4)),
        ("20 ÷ 5", divide(20, 5)),
        ("2 的 10 次方", power(2, 10)),
    ]


def version_html() -> str:
    """显示这个网页是从哪一次提交构建出来的。"""
    # GITHUB_SHA 等环境变量由 GitHub Actions 自动提供，本地运行时没有
    sha = os.environ.get("GITHUB_SHA")
    if not sha:
        return "本地构建"
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    return f'<a href="{server}/{repo}/commit/{sha}">{sha[:7]}</a>'


def build_html() -> str:
    """生成整个网页的 HTML。"""
    rows = "\n".join(
        f"        <tr><td>{html.escape(expr)}</td><td>{result}</td></tr>"
        for expr, result in examples()
    )
    built_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    title = html.escape(TITLE)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      max-width: 36rem;
      margin: 3rem auto;
      padding: 0 1rem;
      color: #222;
    }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
    footer {{ margin-top: 2rem; color: #666; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p>这个网页由 GitHub Actions 自动构建并发布：每次推送到 main，而且测试全部通过，它就会自动更新。</p>
  <table>
    <thead>
      <tr><th>算式</th><th>结果</th></tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
  <footer>版本：{version_html()} · 构建时间：{built_at}（UTC）</footer>
</body>
</html>
"""


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    output = OUTPUT_DIR / "index.html"
    output.write_text(build_html(), encoding="utf-8")
    print(f"已生成 {output}")


if __name__ == "__main__":
    main()
