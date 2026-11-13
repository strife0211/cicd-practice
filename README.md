# CI/CD 练习项目

一个最小的 Python 计算器项目，配一条 GitHub Actions 流水线，用来亲手体验 CI/CD：

- **CI**：推送代码 → 机器自动检查和测试 → 结果显示为 ✅ 或 ❌
- **CD**：测试通过 → 自动生成网页 → 自动发布到网上

第 1～3 步练 CI，第 4～7 步练 CD。

## 准备工作

- Python 3.12 或更高版本（CI 会在 3.12 / 3.13 / 3.14 上测试）
- Git
- 一个 GitHub 账号

## 项目结构

```
.github/workflows/ci.yml   ← 流水线配置（CI/CD 的核心，每行都有注释）
calculator.py              ← 业务代码
tests/test_calculator.py   ← 测试
build_site.py              ← 构建脚本：生成要发布的网页（CD 用）
requirements.txt           ← 依赖（pytest 测试框架、ruff 代码检查），版本已固定
pyproject.toml             ← pytest 和 ruff 的设置
```

`calculator.py` 提供五个函数：

| 函数 | 作用 |
| --- | --- |
| `add(a, b)` | 返回 a + b |
| `subtract(a, b)` | 返回 a - b |
| `multiply(a, b)` | 返回 a × b |
| `divide(a, b)` | 返回 a ÷ b；b 为 0 时抛出 `ValueError` |
| `power(a, b)` | 返回 a 的 b 次方（练习 3 加的） |

## 流水线做了什么

**什么时候运行**（`ci.yml` 里的 `on:`）：

- 推送到 `main` 分支时
- 开 Pull Request、或往已有的 PR 里推新提交时
- 在 Actions 页面手动点 **Run workflow** 时

**运行哪些任务**：

| 任务 | 做什么 | 属于 |
| --- | --- | --- |
| **lint** | 用 ruff 检查代码有没有问题（比如 import 了却没用） | CI |
| **test** | 在 Python 3.12 / 3.13 / 3.14 上同时跑测试 | CI |
| **build** | 运行 `build_site.py` 生成网页，打包成构建产物 | CD |
| **deploy** | 把网页发布到 GitHub Pages（只在 `main` 分支上） | CD |

每个任务都要等前一个通过才会运行，因为配置里写了 `needs`。比如 lint 失败，后面三个任务都不会运行。

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

看到 `All checks passed!` 和 `6 passed` 就说明一切正常。

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

## 第 3 步：CI 练习

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

> 免费账号的**私有仓库**用不了这个功能。要先把仓库改成公开，方法见第 5 步。

---

## CD：让通过测试的代码自动上线

CI 回答的是"这次改动有没有问题"。CD 更进一步：**没问题的代码，自动送到用户面前**，不需要人手动上传。

在这个项目里，要"上线"的是一个网页。`build_site.py` 用计算器算出几个例子，生成 `site/index.html`；
流水线再把它发布到 **GitHub Pages**（GitHub 提供的免费网站托管）。

**两道关卡，保证坏代码上不了线：**

1. **前面全部通过才部署。** build 写了 `needs: test`，deploy 写了 `needs: build`。
   任何一步失败，后面的都不运行，线上网站保持上一个正常的版本。
2. **只有 main 分支才部署。** deploy 写了 `if: github.ref == 'refs/heads/main'`。
   PR 只跑到 build（证明网页能正常生成），不会上线。

**三个新概念**（都能在 `ci.yml` 里找到，有注释）：

- **构建产物（artifact）**：build 生成的 `site/` 文件夹会被打包上传，deploy 直接拿这个包去发布。
  上线的正是测试通过后构建出来的那一份。构建产物每次都重新生成，所以 `site/` 写进了 `.gitignore`，不放进仓库。
- **环境（environment）**：deploy 部署到一个名叫 `github-pages` 的环境。环境可以设规则，比如"上线前要人批准"（练习 8）。
- **权限（permissions）**：流水线默认只能读代码，deploy 单独申请了发布网页需要的两个权限。
  只给必需的权限，叫**最小权限原则**。

## 第 4 步：在本地构建一次

和 CI 一样，先在本地跑通：

```powershell
.venv\Scripts\python build_site.py
start site\index.html
```

macOS / Linux 用 `.venv/bin/python build_site.py`，再用 `open site/index.html`（Linux 用 `xdg-open`）打开。

浏览器里看到的，就是将来线上的样子。页面底部的版本显示"本地构建"；
在流水线里构建时，这里会显示提交编号，点它能跳到对应的提交。

## 第 5 步：设置 GitHub 仓库（只需做一次）

**1. 把仓库改成公开**

免费账号只能给公开仓库开 GitHub Pages。练习 4 的分支规则、练习 8 的人工审批也一样要求公开。

仓库 **Settings → General**，拉到最底部的 **Danger Zone**，点 **Change visibility → Change to public**。

这个练习仓库里没有密码之类的敏感信息，公开没关系。但要记住：真实项目里，
**密码、token 绝不能写进代码**，要放到仓库的 **Settings → Secrets and variables → Actions** 里。

**2. 开启 GitHub Pages**

**Settings → Pages**，在 **Build and deployment** 下面的 **Source** 选 **GitHub Actions**。

⚠️ 这一步要在推送之前做好，否则 deploy 会因为 Pages 没开启而失败。

## 第 6 步：推送，看它自动上线

```powershell
git add .
git commit -m "加上 CD：自动构建并发布网页"
git push
```

打开 Actions 页面，这次能看到四个任务依次运行。全部变绿后，在这次运行的流程图里，
deploy 任务下方会出现网址，形如：

```
https://<你的用户名>.github.io/cicd-practice/
```

点开就是你的网站。以后每一次部署，都会记录在仓库首页右侧栏的 **Deployments** 里。

> 如果你做了练习 4 的分支规则，直接 `git push` 到 main 会被拒绝。那就像练习 3 一样：
> 开分支、提 PR、合并。合并后 main 收到新提交，就会自动部署。

## 第 7 步：CD 练习

### 练习 5：改一行，网站自动更新

把 `build_site.py` 顶部的 `TITLE` 改成你喜欢的标题，提交并推送。
你什么都不用做，等流水线跑完，刷新网页，标题就变了。

再对比网页底部的版本号和 `git log --oneline -1` 显示的提交编号，两者应该一样。
这能确认线上跑的正是你刚推送的那一版。线上出问题时，第一件事往往就是查"现在线上是哪个版本"。

### 练习 6：坏代码上不了线（CD 最重要的一课）

和练习 1 一样，把 `add` 改成 `return a - b`，推送。

- test 失败 → build 和 deploy 都被跳过
- 刷新网站，`2 + 3` 的结果仍然是 `5`

如果没有测试这道关卡，用户就会看到 `2 + 3 = -1`。**CD 敢自动上线，靠的就是 CI 把关。**
看完记得改回来再推送。

### 练习 7：PR 只构建、不部署

开一个分支，在 `build_site.py` 的 `examples()` 里加一行例子，比如：

```python
        ("7 × 8", multiply(7, 8)),
```

推送分支并开 PR。PR 底部的检查里，build 通过了，而 deploy 显示为跳过（skipped）。
点 **Merge pull request** 合并后，main 收到新提交，这时才会部署，网站上多出一行。

### 练习 8：上线前要人工批准

**Settings → Environments → github-pages**，勾选 **Required reviewers**，把自己加进去，点 **Save protection rules**。

再推送一次。build 完成后，deploy 会停下来等待审批。点运行页面上的 **Review deployments**，
勾选 `github-pages`，再点 **Approve and deploy**，才会真正上线。

> 不一定会收到邮件或通知，像这里这样自己推送、自己审批时尤其如此。不用等通知，
> 直接到 Actions 打开那次运行，页面上会提示正在等待审批，**Review deployments** 按钮就在那里。

这就是 CD 的两种含义：

| 设置 | 测试通过之后 | 叫法 |
| --- | --- | --- |
| 不设审批 | 自动上线 | 持续部署（Continuous Deployment） |
| 设了审批 | 随时可以上线，但要有人点头 | 持续交付（Continuous Delivery） |

做完后可以把审批去掉，免得每次都要点。

### 练习 9：回滚

上线的版本有问题时，最稳妥的办法是撤销那次提交，让流水线再部署一次。
试试撤销练习 5 改标题的那次提交：

```powershell
git log --oneline                  # 找到改标题那次提交的编号，比如 a1b2c3d
git revert --no-edit a1b2c3d       # 生成一个"反向"提交，把那次改动撤销
git push
```

`--no-edit` 表示直接使用默认的提交说明，不打开编辑器。流水线跑完，网站标题就变回原样了。

`git revert` 不删除历史，而是新增一个提交，所以不会影响其他人。回滚走的也是同一条流水线：
lint → test → build → deploy。上线和回滚都是自动的、可重复的，这正是 CD 的价值。

---

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

**deploy 失败，日志里说找不到 Pages（Not Found）？**
Pages 还没开启。按第 5 步把 Source 设为 **GitHub Actions**，然后在失败的运行页面点 **Re-run jobs** 重跑。

**Settings → Pages 提示要升级（Upgrade）？**
仓库还是私有的。按第 5 步改成公开。

**deploy 成功了，网站却还是旧的？**
多半是浏览器缓存。按 Ctrl+F5 强制刷新，或者等一两分钟再看。

## 下一步

CI/CD 的基本功到这里就齐了。还可以继续尝试：

- **发布版本**：推送 `v1.0.0` 这样的标签（tag）时，自动打包并创建 GitHub Release
- **Docker**：把程序打包成镜像，推送到 GitHub Container Registry
- **多环境**：先部署到 staging（测试环境），验证没问题再部署到 production（正式环境）
