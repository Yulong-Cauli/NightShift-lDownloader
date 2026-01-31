# NightShift-lDownloader

一个基于时间窗口的智能下载管理器，专为夜间下载优化。

A time-window based intelligent download manager optimized for nighttime downloads.

## 特性 (Features)

- ⏰ **时间窗口控制**: 仅在凌晨 03:00-08:00 执行下载任务 (Time window control: Downloads only between 03:00-08:00)
- 📺 **Telegram 视频下载**: 使用 Telethon 库支持断点续传 (Telegram video download with resumable support)
- 🎬 **通用视频下载**: 基于 yt-dlp，支持 X/Twitter、YouTube 等平台 (Universal video download via yt-dlp for X/Twitter, YouTube, etc.)
- 📦 **库安装任务**: 支持 Shell 命令和 Docker 容器内执行 (Library installation via shell commands or inside Docker containers)
- 💾 **任务持久化**: JSON 格式存储任务状态 (Task persistence with JSON storage)
- 🔄 **断点续传**: 自动保存下载进度，超出时间窗口自动暂停 (Resume support with automatic pause outside time window)

## 安装 (Installation)

### 方式 1: 使用 pip 安装 (Option 1: Install with pip)

```bash
git clone https://github.com/Yulong-Cauli/NightShift-lDownloader.git
cd NightShift-lDownloader
pip install -e .
```

安装后可以使用 `nightshift` 命令：

After installation, you can use the `nightshift` command:

```bash
nightshift --help
```

### 方式 2: 手动安装依赖 (Option 2: Manual installation)

### 1. 克隆仓库 (Clone the repository)

```bash
git clone https://github.com/Yulong-Cauli/NightShift-lDownloader.git
cd NightShift-lDownloader
```

### 2. 安装依赖 (Install dependencies)

```bash
pip install -r requirements.txt
```

### 3. (可选) Telegram 配置 (Optional: Telegram Configuration)

如果需要下载 Telegram 视频，需要获取 API 凭据：

To download Telegram videos, you need to obtain API credentials:

1. 访问 https://my.telegram.org/apps
2. 创建应用获取 `api_id` 和 `api_hash`
3. 设置环境变量：

```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export TELEGRAM_PHONE="+1234567890"
```

## 使用方法 (Usage)

### 命令行界面 (Command Line Interface)

使用 `nightshift` 命令（如果已通过 pip 安装）或 `python3 cli.py`：

Use the `nightshift` command (if installed via pip) or `python3 cli.py`:

#### 添加任务 (Add tasks)

```bash
# 添加视频下载任务 (Add video download task)
nightshift add-video "https://www.youtube.com/watch?v=example"
nightshift add-video "https://x.com/user/status/123456789"

# 添加 Telegram 视频任务 (Add Telegram video task)
nightshift add-telegram "https://t.me/channel/123"

# 添加库安装任务 (Add library installation task)
nightshift add-install "pip install torch"

# 在 Docker 容器中安装库 (Install library in Docker container)
nightshift add-docker my_container "pip install requests"
```

#### 查看任务 (List tasks)

```bash
nightshift list
```

#### 启动下载管理器 (Start the download manager)

```bash
nightshift run
```

#### 自定义配置 (Custom configuration)

```bash
# 使用自定义任务文件和下载目录
nightshift --tasks-file my_tasks.json --download-dir my_downloads run
```

### Python API

也可以直接使用 Python API：

You can also use the Python API directly:

```python
from download_manager import DownloadManager, TaskType

# 创建下载管理器实例
manager = DownloadManager()

# 添加视频下载任务
manager.add_task(
    TaskType.VIDEO_DOWNLOAD.value,
    {"url": "https://www.youtube.com/watch?v=example"}
)

# 添加 Telegram 视频下载任务
manager.add_task(
    TaskType.TELEGRAM_VIDEO.value,
    {"url": "https://t.me/channel/123"}
)

# 添加库安装任务
manager.add_task(
    TaskType.LIBRARY_INSTALL.value,
    {"command": "pip install torch"}
)

# 启动下载管理器
manager.run()
```

### 示例脚本 (Example Script)

运行示例脚本添加任务：

Run the example script to add tasks:

```bash
python3 example_usage.py
```

然后启动下载管理器：

Then start the download manager:

```bash
python3 download_manager.py
```

## 任务类型 (Task Types)

### 1. 视频下载 (Video Download)

支持 YouTube, X/Twitter, Instagram 等平台：

Supports YouTube, X/Twitter, Instagram, and more:

```python
manager.add_task(
    TaskType.VIDEO_DOWNLOAD.value,
    {
        "url": "https://x.com/user/status/123456789",
        # 可选：为 X/Twitter 提供 cookie 文件
        "cookie_file": "/path/to/cookies.txt"
    }
)
```

### 2. Telegram 视频下载 (Telegram Video Download)

```python
manager.add_task(
    TaskType.TELEGRAM_VIDEO.value,
    {
        "url": "https://t.me/channel_name/message_id",
        # 如果未设置环境变量，可以在这里提供
        "api_id": "YOUR_API_ID",
        "api_hash": "YOUR_API_HASH",
        "phone": "+1234567890"
    }
)
```

### 3. 库安装 (Library Installation)

普通 Shell 命令：

Regular shell command:

```python
manager.add_task(
    TaskType.LIBRARY_INSTALL.value,
    {"command": "pip install requests"}
)
```

在 Docker 容器中执行：

Execute inside Docker container:

```python
manager.add_task(
    TaskType.LIBRARY_INSTALL.value,
    {
        "container_name": "my_container",
        "command": "pip install torch"
    }
)
```

## 配置 (Configuration)

### 时间窗口 (Time Window)

默认时间窗口为凌晨 03:00 - 08:00。可以在 `download_manager.py` 中修改 `is_within_window()` 函数：

Default time window is 03:00 - 08:00. You can modify the `is_within_window()` function in `download_manager.py`:

```python
def is_within_window(self) -> bool:
    current_time = datetime.now().time()
    start_time = datetime.strptime("03:00", "%H:%M").time()  # 修改开始时间
    end_time = datetime.strptime("08:00", "%H:%M").time()    # 修改结束时间
    return start_time <= current_time <= end_time
```

### 下载目录 (Download Directory)

```python
manager = DownloadManager(
    tasks_file="tasks.json",
    download_dir="my_downloads"  # 自定义下载目录
)
```

### 检查间隔 (Check Interval)

```python
manager.run(check_interval=30)  # 每 30 秒检查一次（默认 60 秒）
```

## 任务持久化 (Task Persistence)

所有任务都保存在 `tasks.json` 文件中，包含以下信息：

All tasks are saved in `tasks.json` file with the following information:

- `id`: 任务唯一标识符 (Unique task identifier)
- `type`: 任务类型 (Task type)
- `payload`: 任务数据 (Task data)
- `status`: 任务状态 (Task status: pending, in_progress, completed, failed, paused)
- `progress`: 下载进度 (Download progress)
- `created_at`: 创建时间 (Creation time)
- `updated_at`: 更新时间 (Update time)

## 工作原理 (How It Works)

1. 主循环每分钟检查一次当前时间
2. 如果在时间窗口内（03:00-08:00）：
   - 从任务列表中取出待处理任务
   - 执行任务（下载视频、安装库等）
   - 在执行过程中持续检查时间窗口
   - 如果超出时间窗口，立即暂停任务并保存进度
3. 如果不在时间窗口内：
   - 挂起所有任务，等待下一个时间窗口

Working principle:

1. Main loop checks current time every minute
2. If within time window (03:00-08:00):
   - Pick pending tasks from task list
   - Execute tasks (download videos, install libraries, etc.)
   - Continuously check time window during execution
   - If outside window, immediately pause task and save progress
3. If outside time window:
   - Suspend all tasks, wait for next time window

## 高级用法 (Advanced Usage)

### 自定义任务检查函数

```python
class CustomDownloadManager(DownloadManager):
    def is_within_window(self) -> bool:
        # 自定义逻辑，例如根据网络状况判断
        return super().is_within_window() and self.check_network_idle()
    
    def check_network_idle(self) -> bool:
        # 检查网络是否空闲
        return True
```

### 添加任务回调

```python
def on_task_complete(task_id):
    print(f"Task {task_id} completed!")

# 在任务完成后调用回调
# (需要修改 process_task 方法)
```

## 故障排查 (Troubleshooting)

### Telethon 相关错误

如果遇到 Telegram 登录问题：

1. 确保 API 凭据正确
2. 首次运行需要手机验证码
3. 检查 `session` 文件权限

### yt-dlp 下载失败

1. 更新 yt-dlp: `pip install -U yt-dlp`
2. 对于 X/Twitter，尝试提供浏览器 cookies
3. 检查网络连接和代理设置

### Docker 执行失败

1. 确保 Docker 容器正在运行
2. 确保有足够的权限执行 `docker exec`
3. 检查容器名称是否正确

## 依赖项 (Dependencies)

- `yt-dlp`: 通用视频下载器
- `telethon`: Telegram 客户端库
- `python-dateutil`: 日期时间处理

## 贡献 (Contributing)

欢迎提交 Issue 和 Pull Request！

Issues and Pull Requests are welcome!

## 许可证 (License)

MIT License

## 作者 (Author)

Yulong-Cauli

## 致谢 (Acknowledgments)

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Universal video downloader
- [Telethon](https://github.com/LonamiWebs/Telethon) - Pure Python 3 MTProto API Telegram client library