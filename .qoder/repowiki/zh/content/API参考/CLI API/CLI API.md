# CLI API

<cite>
**本文档中引用的文件**  
- [\_main.py](file://rez-3.3.0\src\rez\cli\_main.py)
- [build.py](file://rez-3.3.0\src\rez\cli\build.py)
- [config.py](file://rez-3.3.0\src\rez\cli\config.py)
- [context.py](file://rez-3.3.0\src\rez\cli\context.py)
- [env.py](file://rez-3.3.0\src\rez\cli\env.py)
- [help.py](file://rez-3.3.0\src\rez\cli\help.py)
- [status.py](file://rez-3.3.0\src\rez\cli\status.py)
- [search.py](file://rez-3.3.0\src\rez\cli\search.py)
- [test.py](file://rez-3.3.0\src\rez\cli\test.py)
- [view.py](file://rez-3.3.0\src\rez\cli\view.py)
- [bundle.py](file://rez-3.3.0\src\rez\cli\bundle.py)
- [cp.py](file://rez-3.3.0\src\rez\cli\cp.py)
- [depends.py](file://rez-3.3.0\src\rez\cli\depends.py)
- [diff.py](file://rez-3.3.0\src\rez\cli\diff.py)
- [forward.py](file://rez-3.3.0\src\rez\cli\forward.py)
</cite>

## 目录
1. [简介](#简介)
2. [核心命令](#核心命令)
3. [环境管理命令](#环境管理命令)
4. [包管理命令](#包管理命令)
5. [构建与发布命令](#构建与发布命令)
6. [实用工具命令](#实用工具命令)
7. [错误处理与日志](#错误处理与日志)
8. [性能优化建议](#性能优化建议)
9. [故障排查指南](#故障排查指南)

## 简介

Rez系统提供了一套强大的命令行接口（CLI）API，用于管理软件包和环境。CLI API通过`_main.py`作为入口点，动态加载各个命令模块，实现了灵活的命令扩展机制。用户可以通过`rez <command>`或`rez-<command>`两种形式调用命令，系统会自动解析并执行相应的功能。

CLI API的设计遵循模块化原则，每个命令都有独立的模块负责其参数解析和执行逻辑。核心功能包括环境创建、包搜索、依赖分析、构建发布等，满足了软件开发生命周期中的各种需求。

**Section sources**
- [\_main.py](file://rez-3.3.0\src\rez\cli\_main.py#L1-L201)

## 核心命令

### rez config

`rez config`命令用于显示当前的Rez配置信息。

**参数：**
- `--json`：以JSON格式输出字典或列表字段值
- `--search-list`：列出搜索的配置文件
- `--source-list`：列出已加载的配置文件
- `FIELD`：指定要显示的特定配置项

**使用示例：**
```bash
# 显示所有配置
rez config

# 显示特定配置项
rez config default_shell

# 以JSON格式显示
rez config --json default_packages
```

**Section sources**
- [config.py](file://rez-3.3.0\src\rez\cli\config.py#L1-L66)

### rez help

`rez help`命令用于显示包的帮助信息。

**参数：**
- `-m, --manual`：打开Rez技术用户手册
- `-e, --entries`：仅打印帮助条目
- `PKG`：包名称
- `SECTION`：要查看的帮助部分（1..N）

**使用示例：**
```bash
# 显示包的帮助
rez help python

# 打开用户手册
rez help --manual

# 查看特定部分
rez help maya 2
```

**Section sources**
- [help.py](file://rez-3.3.0\src\rez\cli\help.py#L1-L64)

### rez status

`rez status`命令用于报告环境的当前状态。

**参数：**
- `-t, --tools`：列出可见的工具
- `OBJECT`：要查询的对象（工具、包、上下文或套件）

**使用示例：**
```bash
# 显示当前环境摘要
rez status

# 列出所有工具
rez status --tools

# 查询特定包
rez status python-3.7
```

**Section sources**
- [status.py](file://rez-3.3.0\src\rez\cli\status.py#L1-L35)

### rez search

`rez search`命令用于搜索包。

**参数：**
- `-t, --type`：搜索资源类型（package, family, variant, auto）
- `--nl, --no-local`：不搜索本地包
- `--validate`：验证找到的每个资源
- `--paths`：设置包搜索路径
- `-f, --format`：格式化包输出
- `--no-newlines`：将换行符打印为'\n'
- `-l, --latest`：仅显示每个包的最新版本
- `--errors`：仅打印包含错误的包
- `--nw, --no-warnings`：抑制警告
- `--before`：仅显示在给定时间之前发布的包
- `--after`：仅显示在给定时间之后发布的包
- `PKG`：要搜索的包，支持通配符模式

**使用示例：**
```bash
# 搜索python包
rez search python

# 搜索最新版本
rez search --latest maya

# 格式化输出
rez search --format='{qualified_name} | {description}' python
```

**Section sources**
- [search.py](file://rez-3.3.0\src\rez\cli\search.py#L1-L121)

## 环境管理命令

### rez env

`rez env`命令用于打开一个Rez配置的shell。

**参数：**
- `--shell`：目标shell类型
- `--rcfile`：替代标准启动脚本
- `--norc`：跳过启动脚本加载
- `-c, --command`：在Rez环境中执行命令后退出
- `-s, --stdin`：从标准输入读取命令
- `--ni, --no-implicit`：不添加隐式包到请求中
- `--nl, --no-local`：不加载本地包
- `-b, --build`：创建构建环境
- `--paths`：设置包搜索路径
- `-t, --time`：忽略在给定时间后发布的包
- `--max-fails`：配置失败尝试次数超过N时中止
- `--time-limit`：解析时间超过SECS时中止
- `-o, --output`：将上下文存储到rxt文件
- `-i, --input`：使用之前保存的上下文
- `--exclude`：添加包排除过滤器
- `--include`：添加包包含过滤器
- `--no-filters`：关闭包过滤器
- `-p, --patch`：修补当前上下文创建新上下文
- `--strict`：严格修补
- `--patch-rank`：修补等级
- `--no-cache`：不获取缓存的解析
- `-q, --quiet`：静默模式运行
- `--fail-graph`：如果构建环境解析失败，显示解析图
- `--new-session`：在新进程组中启动shell
- `--detached`：打开单独的终端
- `--no-passive`：仅打印影响求解的操作
- `--stats`：打印高级求解器统计信息
- `--no-pkg-cache`：禁用包缓存
- `--pkg-cache-mode`：覆盖rezconfig的package_cache_async键
- `--pre-command`：预命令
- `PKG`：要在目标环境中使用的包
- `--N0`：--后的参数

**使用示例：**
```bash
# 创建包含Python 3.7和Maya 2022的环境
rez-env python-3.7 maya-2022 -- python

# 使用输入文件创建环境
rez env --input my_context.rxt

# 创建构建环境
rez env --build python-3.7 cmake
```

**Section sources**
- [env.py](file://rez-3.3.0\src\rez\cli\env.py#L1-L279)

### rez context

`rez context`命令用于打印当前Rez上下文或给定上下文文件的信息。

**参数：**
- `--req, --print-request`：仅打印请求列表
- `--res, --print-resolve`：仅打印解析列表
- `--so, --source-order`：按源顺序打印解析包
- `--su, --show-uris`：列出解析包的URI
- `-t, --tools`：打印可用工具列表
- `--which`：在上下文中定位程序
- `-g, --graph`：以图像形式显示解析图
- `-d, --dependency-graph`：显示（更简单的）依赖图
- `--pg, --print-graph`：以字符串形式打印解析图
- `--wg, --write-graph`：将解析图写入文件
- `--pp, --prune-package`：将图修剪到指定包
- `-i, --interpret`：解释上下文并打印结果代码
- `-f, --format`：以给定格式打印解释输出
- `-s, --style`：设置代码输出样式
- `--no-env`：在空环境中解释上下文
- `--diff`：将当前上下文与给定上下文进行比较
- `--fetch`：将当前上下文与重新解析的副本进行比较
- `RXT`：Rez上下文文件

**使用示例：**
```bash
# 显示当前上下文信息
rez context

# 显示解析列表
rez context --print-resolve

# 比较两个上下文
rez context --diff old_context.rxt
```

**Section sources**
- [context.py](file://rez-3.3.0\src\rez\cli\context.py#L1-L196)

## 包管理命令

### rez view

`rez view`命令用于查看包的内容。

**参数：**
- `-f, --format`：打印包的格式
- `-a, --all`：显示所有包数据
- `-b, --brief`：不打印多余信息
- `-c, --current`：显示当前上下文中的包
- `PKG`：要查看的包

**使用示例：**
```bash
# 查看Python包
rez view python

# 以Python格式查看
rez view --format=py maya
```

**Section sources**
- [view.py](file://rez-3.3.0\src\rez\cli\view.py#L1-L77)

### rez depends

`rez depends`命令用于执行反向包依赖查找。

**参数：**
- `-d, --depth`：依赖树深度限制
- `--paths`：设置包搜索路径
- `-b, --build-requires`：包含构建依赖
- `-p, --private-build-requires`：包含私有构建依赖
- `-g, --graph`：以图像形式显示依赖树
- `--pg, --print-graph`：以字符串形式打印依赖树
- `--wg, --write-graph`：将依赖树写入文件
- `-q, --quiet`：不打印进度条或深度指示器
- `PKG`：其他包依赖的包

**使用示例：**
```bash
# 查找依赖Python的包
rez depends python

# 显示依赖图
rez depends --graph maya
```

**Section sources**
- [depends.py](file://rez-3.3.0\src\rez\cli\depends.py#L1-L84)

### rez diff

`rez diff`命令用于比较两个包的源代码。

**参数：**
- `PKG1`：要比较的包
- `PKG2`：要比较的包，如果未提供，则使用下一个最高版本的包

**使用示例：**
```bash
# 比较两个版本的Python
rez diff python-3.7 python-3.8

# 比较相邻版本
rez diff python-3.7
```

**Section sources**
- [diff.py](file://rez-3.3.0\src\rez\cli\diff.py#L1-L36)

### rez cp

`rez cp`命令用于将包从一个仓库复制到另一个仓库。

**参数：**
- `--dest-path`：包仓库目标路径
- `--paths`：设置包搜索路径
- `--nl, --no-local`：不搜索本地包
- `--reversion`：复制到不同的包版本
- `--rename`：复制到不同的包名称
- `-o, --overwrite`：覆盖现有包/变体
- `-s, --shallow`：执行浅层复制
- `--follow-symlinks`：复制符号链接指向的内容
- `-k, --keep-timestamp`：保持源包的时间戳
- `-f, --force`：即使包不可重定位也复制
- `--allow-empty`：允许复制到空的目标仓库
- `--dry-run`：干运行模式
- `--variants`：选择要复制的变体
- `--variant-uri`：复制具有给定URI的变体
- `PKG`：要复制的包

**使用示例：**
```bash
# 复制包
rez cp --dest-path /new/repo python-3.7

# 重命名复制
rez cp --rename mypython python-3.7
```

**Section sources**
- [cp.py](file://rez-3.3.0\src\rez\cli\cp.py#L1-L219)

### rez bundle

`rez bundle`命令用于将上下文及其包捆绑到可重定位目录中。

**参数：**
- `-s, --skip-non-relocatable`：跳过不可重定位的包
- `-f, --force`：即使包不可重定位也捆绑
- `-n, --no-lib-patch`：不在捆绑中应用库修补
- `RXT`：要捆绑的上下文
- `DEST_DIR`：创建捆绑的目录，必须不存在

**使用示例：**
```bash
# 捆绑上下文
rez bundle my_context.rxt /path/to/bundle
```

**Section sources**
- [bundle.py](file://rez-3.3.0\src\rez\cli\bundle.py#L1-L55)

## 构建与发布命令

### rez build

`rez build`命令用于从源代码构建包。

**参数：**
- `-c, --clean`：在重新构建前清除当前构建
- `-i, --install`：安装构建到本地包路径
- `-p, --prefix`：安装到自定义包仓库路径
- `--fail-graph`：如果构建环境解析失败，显示解析图
- `-s, --scripts`：创建构建脚本而不是执行完整构建
- `--view-pre`：仅查看预处理的包定义并退出
- `--process`：使用的构建过程
- `--build-system`：使用的构建系统
- `--variants`：选择要构建的变体
- `--ba, --build-args`：传递给构建系统的参数
- `--cba, --child-build-args`：传递给子构建系统的参数

**使用示例：**
```bash
# 构建包
rez build --install

# 创建构建脚本
rez build --scripts

# 构建特定变体
rez build --variants 0 1
```

**Section sources**
- [build.py](file://rez-3.3.0\src\rez\cli\build.py#L1-L174)

### rez test

`rez test`命令用于运行包定义文件中列出的测试。

**参数：**
- `-l, --list`：列出包的测试并退出
- `--dry-run`：干运行模式
- `-s, --stop-on-fail`：在第一次测试失败时停止
- `--inplace`：在当前环境中运行测试
- `--extra-packages`：向测试环境添加额外包
- `--paths`：设置包搜索路径
- `--nl, --no-local`：不加载本地包
- `PKG`：要运行测试的包
- `TEST`：要运行的测试

**使用示例：**
```bash
# 运行包测试
rez test mypackage

# 列出测试
rez test --list mypackage

# 运行特定测试
rez test mypackage mytest
```

**Section sources**
- [test.py](file://rez-3.3.0\src\rez\cli\test.py#L1-L121)

## 实用工具命令

### rez forward

`rez forward`命令用于创建转发脚本。

**参数：**
- `YAML`：YAML文件
- `ARG`：参数

**使用示例：**
```bash
# 创建转发脚本
rez forward myscript.yaml arg1 arg2
```

**Section sources**
- [forward.py](file://rez-3.3.0\src\rez\cli\forward.py#L1-L74)

## 错误处理与日志

Rez系统的CLI API采用统一的错误处理策略。当命令执行失败时，系统会返回非零退出码，并将错误信息输出到标准错误流。错误信息通常包含错误类型和详细描述，帮助用户快速定位问题。

日志输出遵循verbosity级别，用户可以通过`-v`或`--verbose`参数增加输出的详细程度。调试信息可以通过`--debug`参数启用。日志格式清晰，包含时间戳、日志级别和消息内容，便于问题排查。

**Section sources**
- [\_main.py](file://rez-3.3.0\src\rez\cli\_main.py#L167-L196)

## 性能优化建议

1. **使用缓存**：启用包缓存可以显著提高解析速度，避免重复下载和解析包。
2. **限制搜索路径**：通过`--paths`参数指定精确的包搜索路径，减少不必要的搜索。
3. **使用最新版本**：在搜索时使用`--latest`参数，避免处理大量历史版本。
4. **合理设置超时**：通过`--time-limit`参数设置合理的解析超时，避免长时间等待。
5. **异步包缓存**：使用`--pkg-cache-mode async`参数启用异步包缓存，提高响应速度。

**Section sources**
- [env.py](file://rez-3.3.0\src\rez\cli\env.py#L123-L126)

## 故障排查指南

### 命令未找到

如果遇到"command not found"错误，请检查：
1. Rez是否已正确安装并添加到PATH
2. 是否使用了正确的命令名称
3. 环境变量是否正确设置

### 参数错误

对于参数错误，请参考以下步骤：
1. 检查参数拼写和大小写
2. 确认参数是否需要值
3. 查看命令的帮助信息`rez <command> --help`
4. 检查参数的互斥性，某些参数不能同时使用

### 环境解析失败

当环境解析失败时：
1. 使用`--fail-graph`参数查看解析图，定位冲突
2. 检查包版本约束是否过于严格
3. 验证包依赖关系是否正确
4. 检查包仓库路径是否正确配置

**Section sources**
- [env.py](file://rez-3.3.0\src\rez\cli\env.py#L236-L246)
- [build.py](file://rez-3.3.0\src\rez\cli\build.py#L162-L173)