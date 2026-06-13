LabQC — Windows 安装指南
==========================

LabQC 是凯思康（KSC）出品的医学实验室室内质控管理系统。
支持质控监测、Sigma 分析、方法验证、审计追踪、室间质评、LIS 对接等功能。

系统要求
--------
- Windows 10/11 64位
- （如果从源码运行）Python 3.10+
- （如果构建安装包）Inno Setup 6（可选）

快速开始（二选一）
------------------

方式一：直接运行（Python 已安装）
  1. 解压 LabQC.zip
  2. 双击 run_labqc.py 或在终端运行：
     pip install -r requirements.txt
     python run_labqc.py
  3. 浏览器自动打开 http://localhost:8000
  4. 默认管理员：admin / admin123

方式二：打包为 EXE（无需 Python）
  1. 确保已安装 Python 3.10+
  2. 双击 build_windows.bat 或终端运行：
     build_windows.bat
  3. 等待构建完成（约 3-5 分钟）
  4. 在 dist\LabQC\ 中找到 LabQC.exe，双击运行
  5. 浏览器自动打开 http://localhost:8000

方式三：制作安装包（需要 Inno Setup 6）
  1. 先执行方式二生成 EXE
  2. 安装 Inno Setup 6：https://jrsoftware.org/isinfo.php
  3. 在安装目录打开 installer.iss → 编译
  4. 在 Output\ 中找到 LabQC_Setup_1.0.0.exe
  5. 分发此安装包给最终用户

默认用户
--------
  管理员：admin / admin123
  可在系统设置 → 用户管理中创建更多用户

命令行参数
----------
  python run_labqc.py --port 8080          # 指定端口
  python run_labqc.py --no-browser         # 不自动打开浏览器
  python run_labqc.py --host 0.0.0.0       # 允许局域网访问

技术支持
--------
  在线版：http://selivis.vip.cpolar.cn/labqc/
