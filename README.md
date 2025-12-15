# 自定义脚本解释器项目 (Custom Script Interpreter Project)

这是一个基于自定义脚本语言的交互式对话系统。它包含编译器、解释器和动作执行模块，支持用户定义对话流程、执行自定义动作（如充值、查询）以及数据持久化。

## 项目结构

*   `compiler.py`: **编译器**。将自定义的脚本文件 (`.txt`) 编译成 JSON 格式的中间表示 (`.json`)，供解释器使用。
*   `interpreter.py`: **解释器**。加载编译后的 JSON 文件，执行对话逻辑，处理用户输入，并调用 `actions.py` 中的函数。支持基于规则和 LLM (DeepSeek) 的意图识别。
*   `actions.py`: **动作库**。包含具体的业务逻辑函数，如登录、充值、查询等。它还负责管理用户数据的持久化 (`userinfo.txt`)。
*   `script1.txt`: **示例脚本**。定义了一个完整的电信服务对话流程（登录、充话费、充流量、变更套餐、查询）。
*   `userinfo.txt`: **用户数据文件**。存储用户的余额、流量和套餐信息（自动生成）。

## 快速开始

### 1. 编写/修改脚本
在 `script1.txt` 中定义你的对话流程。

### 2. 编译脚本
使用 `compiler.py` 将文本脚本编译为 JSON 格式：

```bash
python compiler.py script1.txt script1.json
```

### 3. 运行解释器
使用 `interpreter.py` 运行编译后的脚本：

```bash
python interpreter.py script1.json
```

## 脚本语法说明

脚本由多个 **Step** 组成，每个 Step 包含一系列指令。

*   `Step <Name>`: 定义一个步骤。
*   `Speak "<Message>"`: 机器人输出消息。支持变量替换 (如 `$username`)。
*   `Listen`: 等待用户输入。
*   `Action <Function> [Args]`: 调用 `actions.py` 中的函数。
    *   `Action user_login "user_input"`: 使用用户输入作为参数调用登录函数。
*   `Branch "<Intent>" <NextStep>`: 根据用户意图跳转到指定步骤。
    *   支持数值比较：`Branch ">0" successStep`
*   `Silence <NextStep>`: 用户输入超时或为空时的跳转步骤。
*   `Default <NextStep>`: 默认跳转步骤（当没有匹配的分支时）。
*   `Exit`: 结束对话。

## 可用动作 (Actions)

在 `actions.py` 中定义了以下动作，可以直接在脚本中调用：

*   `user_login`: 用户登录。如果用户不存在会自动创建。
*   `charge_bill`: 充值话费。
*   `charge_data`: 充值流量。
*   `change_combo`: 变更套餐 (套餐1, 套餐2, 套餐3)。
*   `check_status`: 查询当前账户状态（余额、流量、套餐）。
*   `place_order`: 下单（示例功能）。
*   `check_order_from_input`: 查询订单（示例功能）。

## 数据存储

用户信息存储在 `userinfo.txt` 中，格式为 JSON。系统会自动读取和保存数据，无需手动干预。

## 依赖

*   Python 3.x
*   (可选) DeepSeek API Key: 在 `interpreter.py` 中配置，用于增强意图识别能力（当前代码中已包含基本的数值和关键词匹配，可在无 API key 情况下运行基础流程）。
