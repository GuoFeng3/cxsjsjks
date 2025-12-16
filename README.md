# 自定义脚本解释器项目 (Custom Script Interpreter Project)

这是一个基于自定义脚本语言的交互式对话系统。它包含编译器、解释器和动作执行模块，支持用户定义对话流程、执行自定义动作（如充值、查询）以及数据持久化。

## 项目结构

*   `src/`: 源代码目录
    *   `core/`: 核心逻辑模块
        *   `compiler.py`: **编译器**。将自定义的脚本文件 (`.txt`) 编译成 JSON 格式的中间表示 (`.json`)。
        *   `interpreter.py`: **解释器**。加载编译后的 JSON 文件，执行对话逻辑。
        *   `actions.py`: **动作库**。包含具体的业务逻辑函数，如登录、充值、查询等。
    *   `llm/`: 大模型交互模块
        *   `client.py`: 处理 DeepSeek API 调用。
        *   `prompts.py`: 存储提示词模板。
*   `scripts/`: 脚本文件目录
    *   `script1.txt`: 示例脚本源码。
    *   `script1.json`: 编译后的脚本。
*   `data/`: 数据存储目录
    *   `userinfo.txt`: 用户数据文件。
*   `main.py`: **入口脚本**。统一管理编译和运行任务。
*   `README.md`: 项目说明文档。

## 快速开始

### 1. 编写/修改脚本
在 `scripts/script1.txt` 中定义你的对话流程。

### 2. 编译脚本
使用 `main.py` 编译脚本：

```bash
python main.py compile scripts/script1.txt scripts/script1.json
```

### 3. 运行解释器
使用 `main.py` 运行编译后的脚本：

```bash
python main.py run scripts/script1.json
```

## 脚本语法说明

脚本由多个 **Step** 组成，每个 Step 包含一系列指令。

*   `Step <Name>`: 定义一个步骤。
*   `Speak "<Message>"`: 机器人输出消息。支持变量替换 (如 `$username`)。
*   `Listen`: 等待用户输入。
*   `Action <Function> [Args]`: 调用 `actions.py` 中的函数。
*   `Branch "<Intent>" <NextStep>`: 根据用户意图跳转到指定步骤。
*   `Silence <NextStep>`: 用户输入超时或为空时的跳转步骤。
*   `Default <NextStep>`: 默认跳转步骤。
*   `Exit`: 结束对话。

## 数据存储

用户信息存储在 `data/userinfo.txt` 中，格式为 JSON。

## 依赖

*   Python 3.x
*   DeepSeek API Key (配置在 `src/core/interpreter.py` 中)
