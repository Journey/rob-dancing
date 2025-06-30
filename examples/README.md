# 音频可视化示例

这个目录包含了多个音频可视化的示例文件，展示了不同的使用方法。

## 文件说明

### 🎵 `basic_usage.py`
包含所有三个例子的综合示例文件，一次性运行所有示例。

### 🎯 独立示例文件

#### `example1_class_usage.py`
**使用 AudioVisualizer 类**
- 展示面向对象的使用方式
- 可自定义图形大小
- 支持保存和显示选项
- 生成 `example1_waveform.png`

#### `example2_convenience_function.py` 
**使用便捷函数**
- 展示最简单的一行式调用
- 适合快速可视化需求
- 生成 `example2_waveform.png`

#### `example3_step_by_step.py`
**逐步处理方法**
- 展示详细的处理步骤
- 显示音频文件的详细信息（采样率、时长等）
- 适合学习和调试
- 生成 `example3_waveform.png`

## 如何运行

### 运行单个示例
```bash
# 在项目根目录下运行
poetry run python examples/example1_class_usage.py
poetry run python examples/example2_convenience_function.py  
poetry run python examples/example3_step_by_step.py
```

### 运行综合示例
```bash
poetry run python examples/basic_usage.py
```

## 输出文件

每个示例都会生成对应的波形图文件：
- `example1_waveform.png` - 类方法生成的波形图
- `example2_waveform.png` - 便捷函数生成的波形图  
- `example3_waveform.png` - 逐步方法生成的波形图
- `waveform.png` - 综合示例生成的波形图

## 音频文件

示例使用 `molihua.mp4` 作为输入文件。请确保该文件存在于项目根目录中。

## 依赖要求

- Python 3.12+
- librosa
- matplotlib
- numpy
- soundfile (可选，用于更好的音频文件支持) 