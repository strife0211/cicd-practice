# CI/CD 练习项目

一个最小的 Python 计算器项目，配一条 GitHub Actions 流水线，用来亲手体验 CI：
推送代码 → 机器自动检查和测试 → 结果显示为 ✅ 或 ❌。

## 准备工作

- Python 3.12 或更高版本（CI 会在 3.12 / 3.13 / 3.14 上测试）
- Git
- 一个 GitHub 账号

## 项目结构

```
.github/workflows/ci.yml   ← 流水线配置（CI 的核心，每行都有注释）
calculator.py              ← 业务代码
tests/test_calculator.py   ← 测试
requirements.txt           ← 依赖（pytest 测试框架、ruff 代码检查），版本已固定
pyproject.toml             ← pytest 和 ruff 的设置
```

`calculator.py` 提供四个函数：

| 函数 | 作用 |
| --- | --- |
| `add(a, b)` | 返回 a + b |
| `subtract(a, b)` | 返回 a - b |
| `multiply(a, b)` | 返回 a × b |
| `divide(a, b)` | 返回 a ÷ b；b 为 0 时抛出 `ValueError` |

## 流水线做了什么

**什么时候运行**（`ci.yml` 里的 `on:`）：

- 推送到 `main` 分支时
- 开 Pull Request、或往已有的 PR 里推新提交时
- 在 Actions 页面手动点 **Run workflow** 时

**运行哪些任务**：

1. **lint**：用 ruff 检查代码有没有问题（比如 import 了却没用）
2. **test**：lint 通过后，在 Python 3.12 / 3.13 / 3.14 上同时跑测试

lint 失败时 test 根本不会运行，因为配置里写了 `needs: lint`。

## 第 1 步：在本地跑一遍

CI 做的事情，本地都能手动做。先在本地跑通，再交给机器。

Windows（PowerShell）：

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m pytest -v
```

macOS / Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest -v
```

看到 `All checks passed!` 和 `5 passed` 就说明一切正常。

> 小技巧：ruff 报的问题如果带 `[*]` 标记，可以加 `--fix` 自动修复，例如
> `.venv\Scripts\python -m ruff check . --fix`。

## 第 2 步：推送到 GitHub

1. 打开 https://github.com/new ，仓库名填 `cicd-practice`，**不要**勾选 "Add a README"，点 Create repository
2. 在这个文件夹里运行（把 `<你的用户名>` 换成你的 GitHub 用户名）：

   ```powershell
   git add .
   git commit -m "第一次提交：计算器 + CI 流水线"
   git remote add origin https://github.com/<你的用户名>/cicd-practice.git
   git push -u origin main
   ```

3. 打开仓库页面的 **Actions** 标签，就能看到流水线在跑了。点进去可以看每一步的日志。

`.venv/` 和各种缓存目录已经写进 `.gitignore`，`git add .` 不会把它们传上去。

可选：把下面这行加到 README 最上面，仓库首页就会显示 CI 状态徽章：

```markdown
![CI](https://github.com/<你的用户名>/cicd-practice/actions/workflows/ci.yml/badge.svg)
```

## 第 3 步：练习

### 练习 1：让测试失败（看它变红 ❌）

把 `calculator.py` 里 `add` 的 `return a + b` 改成 `return a - b`，然后：

```powershell
git commit -am "故意写错 add"
git push
```

去 Actions 看：三个 Python 版本的 test 任务都失败了。点开「运行测试」那一步，读懂报错信息。
改回来再推送一次，看它变回绿色 ✅。

### 练习 2：让 lint 失败

在 `calculator.py` 第一行下面加一行 `import os`（导入了但没用），推送。
这次 **lint** 失败（报错 `F401 os imported but unused`），而 **test** 根本没运行，因为配置里写了 `needs: lint`。

### 练习 3：用 Pull Request 的方式工作（真实团队的做法）

```powershell
git switch -c add-power
```

在 `calculator.py` 加一个 `power(a, b)` 函数（返回 a 的 b 次方），在测试文件里加对应的测试，然后：

```powershell
git add .
git commit -m "新增 power 函数"
git push -u origin add-power
```

在 GitHub 上为这个分支开一个 Pull Request，PR 页面底部会显示 CI 检查结果。

注意：光推送 `add-power` 分支不会触发 CI（流水线只监听推送到 `main`），要等开了 PR 才会运行。

<details>
<summary>参考答案</summary>

`calculator.py`：

```python
def power(a: float, b: float) -> float:
    """返回 a 的 b 次方。"""
    return a**b
```

`tests/test_calculator.py`（别忘了在顶部的 import 里加上 `power`）：

```python
def test_power():
    assert power(2, 3) == 8
```

</details>

### 练习 4：测试不过就不许合并

仓库 **Settings → Branches → Add branch ruleset**（或 Add classic branch protection rule）：
目标分支选 `main`，勾选 **Require status checks to pass**，把下面这些检查都加进去：

- `lint`
- `test (3.12)`
- `test (3.13)`
- `test (3.14)`

test 用了矩阵，所以每个 Python 版本是一个独立的检查。这些名字要等流水线至少跑过一次之后才搜得到。

之后任何 PR 只要 CI 没通过，合并按钮就是灰的。这就是 CI 真正保护代码质量的方式。

## 常见问题

**`python` 命令找不到？**
Windows 上从 https://www.python.org 安装时要勾选 "Add python.exe to PATH"；或者把 `python` 换成 `py`。

**`git push` 要求输入密码？**
GitHub 不接受账号密码推送。Windows 版 Git 一般会弹出浏览器让你登录；如果没弹，到 GitHub 的
**Settings → Developer settings → Personal access tokens** 创建一个 token，在要求输入密码时粘贴它。

**`git push` 被拒绝（rejected）？**
通常是建仓库时勾了 "Add a README"，远程已经有一个提交。最简单的办法：删掉这个 GitHub 仓库，按第 2 步重新建一个。

**本地通过，CI 却失败？**
先看是哪个 Python 版本失败。本地通常只装了一个版本，而 CI 在三个版本上跑。点开失败的那一步，日志和本地报错一样能读。

## 下一步：加上 CD

CI 跑通以后，可以试着加一个部署任务，比如：

- 用 GitHub Pages 自动发布一个网页
- 打包成 Docker 镜像推送到 GitHub Container Registry
- 用 `environment` 设置"部署到生产前需要人工批准"
