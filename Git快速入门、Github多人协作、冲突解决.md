作为 Git 新人，掌握以下核心操作就能满足日常使用，按「初始化→日常操作→协作」三个阶段来学：


### 一、基础准备
1. **安装 Git**  
   官网下载对应系统版本（[git-scm.com](https://git-scm.com)），安装时一路默认即可。  
   验证：打开终端（Windows 用 PowerShell，Mac/Linux 用终端），输入 `git --version` 能看到版本号就说明成功。

2. **首次配置身份**  
   每次提交代码时，Git 会记录你的身份，必须配置一次：  
   ```bash
   git config --global user.name "你的名字"  # 比如 "Zhang San"
   git config --global user.email "你的邮箱"  # 比如 "zhangsan@example.com"
   ```


### 二、本地仓库操作（自己玩代码）
#### 1. 新建本地仓库（从无到有）
```bash
# 1. 新建一个文件夹（比如叫 myproject），进入该文件夹
mkdir myproject
cd myproject

# 2. 初始化 Git 仓库（会生成一个隐藏的 .git 文件夹，管理版本记录）
git init
```

#### 2. 日常代码管理（核心！）
假设你在文件夹里新建了 `hello.py` 等文件，按以下步骤管理：

```bash
# 1. 查看文件状态（哪些文件被修改/新增）
git status
# 输出会显示：红色文件=未暂存，绿色文件=已暂存

# 2. 暂存文件（把修改放入"待提交区"）
git add 文件名  # 暂存单个文件，比如 git add hello.py
git add .       # 暂存所有修改（推荐日常用这个）

# 3. 提交到本地仓库（生成一个版本记录，必须写备注说明改了啥）
git commit -m "第一次提交：添加了hello.py"
# 备注要清晰，比如"修复登录bug"、"新增用户列表功能"
```

#### 3. 查看历史记录
```bash
git log  # 查看所有提交记录（按 q 退出）
git log --oneline  # 简洁显示（一行一个提交）
```

#### 4. 撤销操作（新手必学）
```bash
# 撤销工作区的修改（比如改乱了 hello.py，想回到上次提交的状态）
git checkout -- hello.py

# 撤销暂存区的文件（比如 add 错了，想放回工作区）
git reset HEAD 文件名

# 回到某个历史版本（commit_id 是 git log 里看到的版本号前几位）
git reset --hard 1a2b3c
```


### 三、远程仓库协作（和 GitHub 配合）
#### 1. 关联远程仓库（以 GitHub 为例）
- 先在 GitHub 新建一个仓库（点右上角「+」→「New repository」），名字和本地文件夹一致（比如 myproject），不要勾选「Initialize this repository with a README」。
- 把本地仓库和远程仓库关联：  
  ```bash
  # 关联远程仓库并命名为origin（远程仓库地址在 GitHub 上复制，是 https 或 git 开头的链接）
  git remote add origin https://github.com/你的账号/myproject.git
  # 将本地仓库的主分支改名为main
  git branch -M main			
  ```

#### 2. 推送到远程仓库
```bash
# 第一次推送本地代码到远程（-u 表示关联分支，后续推送可简化）
git push -u origin main
# 后续推送只需用：git push

# 如果远程仓库有README等文件，本地没有，推送前先拉取合并
git pull origin main --allow-unrelated-histories
```

#### 3. 从远程仓库拉取代码（比如换电脑工作）
```bash
# 克隆远程仓库到本地（第一次获取）
git clone https://github.com/你的账号/myproject.git

# 后续远程有更新，拉取到本地
git pull origin main
```


### 四、分支操作（多人协作必备）
```bash
# 1. 查看所有分支（当前分支前有 *）
git branch

# 2. 新建并切换到分支（比如开发新功能）
git checkout -b feature/新功能

# 3. 在新分支上修改、提交后，推送到远程
git push -u origin feature/新功能

# 4. 功能完成后，切回主分支，合并新分支
git checkout main
git merge feature/新功能
git push origin main

# 5. 删除本地已合并的分支（可选）
git branch -d feature/新功能
```


### 核心流程总结
1. 写代码 → 2. `git add .` → 3. `git commit -m "备注"` → 4. `git push`（推到远程）  
遇到问题先看 `git status` 提示，新手初期多练习这几个命令，熟练后再学进阶功能（如冲突解决、标签管理）。


### 一、关联分支（本地与远程分支建立联系）
关联分支是指让本地分支与远程仓库的某个分支“绑定”，方便后续使用 `git pull`/`git push` 时省略分支名（无需每次写 `origin 分支名`），本质是建立跟踪关系。

#### 1. 关联分支的3种场景
##### （1）本地新建分支后，首次推送到远程并关联
```bash
# 本地新建分支
git checkout -b feature/login

# 首次推送时，用 -u 参数自动关联（-u = --set-upstream）
git push -u origin feature/login
```
执行后，本地 `feature/login` 分支会与远程 `origin/feature/login` 分支关联，后续推送/拉取可简化：
```bash
git push  # 等价于 git push origin feature/login
git pull  # 等价于 git pull origin feature/login
```

##### （2）本地已有分支，关联远程已存在的分支
如果远程已有 `dev` 分支，本地新建 `dev` 分支后手动关联：
```bash
git checkout -b dev  # 本地新建dev分支
git branch --set-upstream-to=origin/dev dev  # 关联远程dev分支
```

##### （3）查看关联关系
```bash
git branch -vv  # 查看所有分支的关联状态
# 输出示例：
#  main    a1b2c3 [origin/main] 上次提交备注
#* dev     d4e5f6 [origin/dev]  开发中
```


### 二、多人协作完整流程（以 GitHub 为例）
假设团队多人共同开发一个项目，核心原则是：**各自在分支开发，通过 Pull Request 合并到主分支**，避免直接修改主分支。

#### 1. 前期准备
- 项目负责人创建主仓库（`upstream`），并添加成员为协作者（Settings → Collaborators）。
- 每位开发者 **Fork** 主仓库到自己账号（得到 `origin` 远程仓库），并克隆到本地：
  ```bash
  git clone https://github.com/自己账号/项目名.git
  cd 项目名
  # 添加主仓库为上游（方便同步最新代码）
  git remote add upstream https://github.com/原作者账号/项目名.git
  ```


#### 2. 日常协作步骤（以开发者 A 为例）
##### （1）同步主仓库最新代码
开始开发前，先确保本地主分支与 `upstream` 同步：
```bash
git checkout main  # 切到主分支
git fetch upstream  # 拉取主仓库最新更新
git merge upstream/main  # 合并到本地主分支
```

##### （2）新建分支开发功能
```bash
# 从主分支新建功能分支（命名格式：feature/功能名 或 fix/问题名）
git checkout -b feature/用户注册
```

##### （3）本地开发与提交
```bash
# 写代码...
git add .  # 暂存修改
git commit -m "完成用户注册表单验证"  # 提交到本地
```

##### （4）推送到自己的远程仓库（origin）
```bash
# 首次推送该分支，关联远程
git push -u origin feature/用户注册
# 后续修改推送，直接用 git push
```

##### （5）发起 Pull Request（PR）
- 打开自己 GitHub 仓库页面，会看到“Compare & pull request”按钮，点击进入。
- 填写 PR 描述（改了什么、解决了什么问题），选择合并到主仓库的 `main` 分支，提交。


#### 3. 处理代码审核与冲突
- **审核反馈**：主仓库维护者会审核代码，可能提出修改意见。开发者 A 需在本地修改后，再次 `git push`（会自动更新 PR）。
- **解决冲突**：如果多人修改了同一文件，PR 会提示冲突，需在本地解决：
  ```bash
  # 拉取主仓库最新代码到本地主分支
  git checkout main
  git fetch upstream
  git merge upstream/main
  
  # 切回功能分支，合并主分支的更新（触发冲突解决）
  git checkout feature/用户注册
  git merge main
  
  # 打开冲突文件，找到 <<<<<<< HEAD 标记的冲突部分，手动编辑保留正确代码
  # 编辑后提交
  git add .
  git commit -m "解决与主分支的冲突"
  git push  # 更新PR
  ```


#### 4. 合并代码与清理
- 审核通过后，维护者会合并 PR 到主仓库的 `main` 分支。
- 开发者 A 清理本地和远程分支：
  ```bash
  # 切回主分支，同步最新代码
  git checkout main
  git pull upstream main
  
  # 删除本地功能分支
  git branch -d feature/用户注册
  
  # （可选）删除远程功能分支
  git push origin --delete feature/用户注册
  ```


### 三、核心原则总结
1. **分支隔离**：功能开发、bug修复都在独立分支进行，不碰主分支。
2. **频繁同步**：定期从主仓库（`upstream`）拉取更新，减少冲突。
3. **PR 审核**：通过 PR 让代码经过审核再合并，保证主分支质量。
4. **清晰命名**：分支名、提交备注要明确（如 `fix/login-validation`），方便团队理解。

熟练这套流程后，多人协作会非常顺畅，即使团队规模扩大也能保持代码管理有序。


当多人修改了同一文件的同一部分内容时，Git 无法自动判断保留哪部分修改，就会产生**冲突**。此时 PR（Pull Request）会显示冲突状态，无法直接合并，必须在本地手动解决。以下是详细的冲突产生原因、识别方式和解决流程：

### 一、冲突产生的本质
假设场景：
- 开发者 A 和开发者 B 同时从主分支（`main`）创建了自己的功能分支（`feature/A` 和 `feature/B`）。
- 两人都修改了 `user.js` 文件的第 10 行（比如 A 改成“张三”，B 改成“李四”）。
- 开发者 A 先完成 PR 并合并到 `main` 分支。
- 当开发者 B 提交 PR 时，Git 发现 `main` 分支的 `user.js` 第 10 行已被 A 修改，与 B 的修改冲突，无法自动合并。


### 二、如何识别冲突
1. **PR 页面提示**：在 GitHub/GitLab 的 PR 页面会显示类似 “This branch has conflicts that must be resolved” 的提示，无法点击“Merge”按钮。
   
2. **本地拉取时提示**：当你在本地合并主分支到自己的功能分支时，Git 会在终端显示冲突文件，例如：
   ```
   Auto-merging user.js
   CONFLICT (content): Merge conflict in user.js
   Automatic merge failed; fix conflicts and then commit the result.
   ```


### 三、本地解决冲突的完整步骤
以开发者 B 解决冲突为例：

#### 步骤 1：确保本地分支是最新的功能分支
```bash
# 切换到自己的功能分支（比如 feature/B）
git checkout feature/B
```

#### 步骤 2：拉取主仓库（upstream）的最新代码
```bash
# 拉取主仓库（upstream）的 main 分支最新更新
git fetch upstream
```

#### 步骤 3：合并主分支到自己的功能分支（触发冲突）
```bash
# 合并 upstream/main 到当前分支（feature/B）
git merge upstream/main
```
此时 Git 会尝试自动合并，冲突文件会被标记，终端会提示哪些文件有冲突（如 `user.js`）。


#### 步骤 4：手动编辑冲突文件
打开冲突文件（如 `user.js`），会看到 Git 自动添加的冲突标记，格式如下：
```javascript
// 冲突部分的代码
<<<<<<< HEAD  // 你的修改（当前分支 feature/B 的内容）
let username = "李四";
=======  // 分隔线（上方是你的修改，下方是主分支的修改）
let username = "张三";
>>>>>>> upstream/main  // 主分支（upstream/main）的修改
```

- **解决逻辑**：根据实际需求，保留正确的代码，删除冲突标记（`<<<<<<<`、`=======`、`>>>>>>>`）。  
  例如，最终决定用“张三”，则修改为：
  ```javascript
  let username = "张三";
  ```


#### 步骤 5：提交解决后的代码
```bash
# 暂存已解决冲突的文件
git add user.js  # 或 git add .（提交所有修改）

# 提交合并结果（备注需说明“解决冲突”）
git commit -m "解决与 upstream/main 的冲突：统一 username 为张三"
```


#### 步骤 6：推送到自己的远程仓库（更新 PR）
```bash
git push origin feature/B
```
推送后，PR 页面会自动更新，冲突状态会消失，此时维护者可以正常合并。


### 四、关键注意事项
1. **冲突只在“同一部分”产生**：如果两人修改的是同一文件的不同位置（如 A 改第 10 行，B 改第 20 行），Git 会自动合并，不会产生冲突。

2. **沟通优先**：解决冲突前，最好和相关开发者沟通，确认保留哪部分代码，避免误删重要修改。

3. **小步提交减少冲突**：频繁提交代码、及时同步主分支更新（每天至少一次），可以减少冲突的概率和复杂度。

4. **工具辅助**：复杂冲突可以用可视化工具（如 VS Code 的冲突解决界面、GitKraken），更直观地对比和选择代码。


通过以上步骤，就能清晰地识别并解决多人协作中的代码冲突，确保团队代码的一致性。冲突是协作中的正常现象，核心是通过规范流程和沟通高效解决。