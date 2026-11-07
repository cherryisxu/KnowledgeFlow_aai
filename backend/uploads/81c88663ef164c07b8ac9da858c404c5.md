# Python 工具库（第三方库）安装方法

Python 绝大多数实用工具库（如 `matplotlib`、`pandas`、`numpy`）**不是自带的**，需要手动安装，最核心、最常用的安装工具是 **`pip`**，下面用最简单、最实用的方式教你安装。

---

## 一、最常用：pip 安装（万能方法）

`pip` 是 Python 官方的包管理工具，**安装、卸载、更新库**都靠它，几乎所有库都能用 pip 安装。

### 1. 检查是否能用 pip

打开电脑的 **命令提示符（CMD）** 或 **终端（Terminal）**，输入：

```bash
pip --version
```

出现版本号就说明可用，没有就先安装 Python（安装时勾选 **Add Python to PATH**）。

---

## 二、最基础安装命令

### 安装某个库

```bash
pip install 库名
```

### 常用库安装示例

```bash
# 数据可视化
pip install matplotlib

# 数据分析
pip install pandas

# 数值计算
pip install numpy

# 爬虫
pip install requests
pip install beautifulsoup4

# 机器学习
pip install scikit-learn
```

安装成功会显示：`Successfully installed xxx`

---

## 三、常用实用技巧

### 1. 安装指定版本

```bash
pip install matplotlib==3.7.0
```

### 2. 升级库到最新版

```bash
pip install --upgrade matplotlib
```

### 3. 卸载库

```bash
pip uninstall matplotlib
```

### 4. 查看已安装的库

```bash
pip list
```

---

## 四、安装慢/失败？用国内镜像加速（超级好用）

国内直接用 pip 下载很慢，**切换国内源** 速度快10倍以上。

### 临时使用（推荐）

```bash
pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple
```

常用国内源：

- 清华源（最快）
- 阿里源
- 豆瓣源

---

## 五、conda 安装（适合数据分析/AI 用户）

如果你用 **Anaconda** 或 **Miniconda**，可以用 conda 安装：

```bash
conda install matplotlib
conda install pandas
```

---

## 六、最关键总结（3 条记住就够）

1. **99% 的库用 `pip install 库名` 安装**
2. **安装慢就加 `-i 清华源`**
3. **安装成功看提示 `Successfully`**

---
