"""详细解释音频振幅的计算和表示"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
from datetime import datetime

# 配置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def explain_amplitude_calculation(audio_file="molihua.mp4"):
    """详细解释音频振幅的计算过程"""
    
    print("🎵 音频振幅计算详解")
    print("=" * 60)
    
    # 1. 加载音频文件
    print("📖 步骤1: 音频文件加载")
    print("-" * 30)
    
    try:
        # 加载原始音频数据
        y, sr = librosa.load(audio_file, duration=60, sr=None)  # 保持原始采样率
        print(f"📁 音频文件: {audio_file}")
        print(f"📊 原始采样率: {sr} Hz")
        print(f"⏱️  音频长度: {len(y)/sr:.3f} 秒")
        print(f"🔢 样本点数量: {len(y):,} 个")
        print(f"📏 数据类型: {y.dtype}")
        print()
        
        # 重新加载为标准采样率进行对比
        y_std, sr_std = librosa.load(audio_file, duration=60)  # librosa默认22050Hz
        print(f"🔄 标准化后采样率: {sr_std} Hz")
        print(f"🔢 标准化后样本点: {len(y_std):,} 个")
        print()
        
    except FileNotFoundError:
        print(f"❌ 找不到文件: {audio_file}")
        return
    
    # 2. 振幅的数学定义
    print("📐 步骤2: 振幅的数学定义")
    print("-" * 30)
    print("🔬 振幅 = 声音波形偏离平衡位置的最大距离")
    print("📊 在数字音频中:")
    print("   • 振幅范围: [-1.0, +1.0] (librosa归一化后)")
    print("   • +1.0 = 最大正向位移")
    print("   • -1.0 = 最大负向位移") 
    print("   •  0.0 = 平衡位置")
    print()
    
    # 3. 分析振幅数据
    print("📈 步骤3: 振幅数据分析")
    print("-" * 30)
    
    # 统计信息
    amplitude_max = np.max(y)
    amplitude_min = np.min(y)
    amplitude_mean = np.mean(y)
    amplitude_std = np.std(y)
    amplitude_rms = np.sqrt(np.mean(y**2))  # RMS振幅
    
    print(f"📊 振幅统计:")
    print(f"   最大值: {amplitude_max:.6f}")
    print(f"   最小值: {amplitude_min:.6f}") 
    print(f"   平均值: {amplitude_mean:.6f}")
    print(f"   标准差: {amplitude_std:.6f}")
    print(f"   RMS值: {amplitude_rms:.6f}")
    print()
    
    # 峰值分析
    peak_positive = np.max(y)
    peak_negative = np.min(y)
    peak_to_peak = peak_positive - peak_negative
    
    print(f"🎯 峰值分析:")
    print(f"   正峰值: {peak_positive:.6f}")
    print(f"   负峰值: {peak_negative:.6f}")
    print(f"   峰峰值: {peak_to_peak:.6f}")
    print()
    
    # 4. 采样和量化过程
    print("🔄 步骤4: 采样和量化过程")
    print("-" * 30)
    print("📡 模拟信号 → 数字信号 转换:")
    print("   1️⃣ 采样 (Sampling): 按固定时间间隔测量信号值")
    print(f"      • 采样率: {sr} Hz = 每秒{sr:,}次测量")
    print(f"      • 采样间隔: {1/sr*1000:.3f} 毫秒")
    print("   2️⃣ 量化 (Quantization): 将连续值转为离散数字")
    print("      • 16位: 65,536个离散级别")
    print("      • 24位: 16,777,216个离散级别")
    print("   3️⃣ 归一化: librosa将值缩放到[-1, +1]范围")
    print()
    
    # 5. 时域中的振幅表示
    print("⏰ 步骤5: 时域中的振幅")
    print("-" * 30)
    
    # 提取一小段数据进行详细分析
    segment_start = sr * 2  # 从第2秒开始
    segment_length = int(sr * 0.1)  # 0.1秒长度
    segment = y[segment_start:segment_start + segment_length]
    time_segment = np.linspace(2, 2.1, len(segment))
    
    print(f"🔍 分析片段: 第2.0-2.1秒 ({len(segment)}个样本)")
    print(f"   片段最大振幅: {np.max(segment):.6f}")
    print(f"   片段最小振幅: {np.min(segment):.6f}")
    print(f"   片段平均振幅: {np.mean(segment):.6f}")
    print()
    
    # 显示前20个样本的具体数值
    print("📋 前20个样本的振幅值:")
    for i in range(min(20, len(segment))):
        time_point = time_segment[i]
        amplitude_val = segment[i]
        print(f"   t={time_point:.4f}s: {amplitude_val:+.6f}")
    print()
    
    # 6. 不同振幅表示方法
    print("📊 步骤6: 振幅的不同表示方法")
    print("-" * 30)
    
    # dB表示
    amplitude_db = 20 * np.log10(np.abs(y) + 1e-10)  # 避免log(0)
    amplitude_db_max = np.max(amplitude_db)
    
    print("🔊 分贝(dB)表示:")
    print(f"   最大dB值: {amplitude_db_max:.2f} dB")
    print("   dB = 20 * log10(|amplitude|)")
    print("   • 0 dB = 振幅 1.0 (最大)")
    print("   • -6 dB ≈ 振幅 0.5")
    print("   • -20 dB ≈ 振幅 0.1")
    print()
    
    # 功率表示
    power = y**2
    power_avg = np.mean(power)
    
    print("⚡ 功率表示:")
    print(f"   平均功率: {power_avg:.6f}")
    print("   功率 = 振幅²")
    print("   功率反映信号的能量强度")
    print()
    
    # 7. 可视化
    print("🎨 生成振幅分析可视化...")
    
    fig, axes = plt.subplots(4, 1, figsize=(15, 12))
    
    # 子图1: 完整波形
    time_full = np.linspace(0, len(y)/sr, len(y))
    axes[0].plot(time_full, y, alpha=0.7, color='blue', linewidth=0.5)
    axes[0].set_title(f'完整音频波形\n振幅范围: [{amplitude_min:.3f}, {amplitude_max:.3f}]')
    axes[0].set_xlabel('时间 (秒)')
    axes[0].set_ylabel('振幅')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0, color='red', linestyle='--', alpha=0.5, label='零线')
    axes[0].legend()
    
    # 子图2: 详细片段
    axes[1].plot(time_segment, segment, 'o-', color='green', markersize=3, linewidth=1)
    axes[1].set_title(f'详细片段分析 (第2.0-2.1秒)\n采样率: {sr} Hz, 样本间隔: {1/sr*1000:.3f}ms')
    axes[1].set_xlabel('时间 (秒)')
    axes[1].set_ylabel('振幅')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    
    # 子图3: 振幅分布直方图
    axes[2].hist(y, bins=100, alpha=0.7, color='purple', edgecolor='black')
    axes[2].axvline(x=amplitude_mean, color='red', linestyle='--', label=f'平均值: {amplitude_mean:.4f}')
    axes[2].axvline(x=amplitude_rms, color='orange', linestyle=':', label=f'RMS: {amplitude_rms:.4f}')
    axes[2].set_title('振幅分布直方图')
    axes[2].set_xlabel('振幅值')
    axes[2].set_ylabel('频次')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    # 子图4: dB表示
    time_db = time_full[::100]  # 降采样显示
    amplitude_db_display = amplitude_db[::100]
    axes[3].plot(time_db, amplitude_db_display, color='red', alpha=0.7, linewidth=0.8)
    axes[3].set_title(f'振幅的分贝表示\n最大值: {amplitude_db_max:.1f} dB')
    axes[3].set_xlabel('时间 (秒)')
    axes[3].set_ylabel('振幅 (dB)')
    axes[3].grid(True, alpha=0.3)
    axes[3].set_ylim([-80, 0])  # 限制dB范围便于显示
    
    plt.tight_layout()
    plt.savefig('amplitude_analysis.png', dpi=300, bbox_inches='tight')
    print("💾 振幅分析图表已保存为: amplitude_analysis.png")
    plt.show()
    
    # 8. 实际应用
    print("\n🛠️  振幅在音频处理中的应用:")
    print("-" * 30)
    print("1. 🔊 音量控制: 乘以缩放因子调整响度")
    print("2. 🎚️ 动态范围压缩: 减小音量变化范围")
    print("3. 🔇 噪声门限: 低于阈值的信号置零")
    print("4. 📊 音频分析: 检测静音、爆音等")
    print("5. 🎵 音效处理: 失真、混响等基于振幅")
    
    # 9. 保存振幅数据为JSON
    print("\n💾 保存振幅分析结果...")
    save_amplitude_to_json(audio_file, y, sr, {
        'max': amplitude_max,
        'min': amplitude_min,
        'mean': amplitude_mean,
        'std': amplitude_std,
        'rms': amplitude_rms,
        'peak_to_peak': peak_to_peak
    })
    
    return y, sr, {
        'max': amplitude_max,
        'min': amplitude_min,
        'mean': amplitude_mean,
        'std': amplitude_std,
        'rms': amplitude_rms,
        'peak_to_peak': peak_to_peak
    }


def save_amplitude_to_json(audio_file, amplitude_data, sample_rate, stats, 
                           downsample_factor=100, output_file=None):
    """
    将振幅数据保存为JSON格式
    
    参数:
    - audio_file: 音频文件路径
    - amplitude_data: 振幅数据数组
    - sample_rate: 采样率
    - stats: 统计信息字典
    - downsample_factor: 降采样因子(默认100，减少文件大小)
    - output_file: 输出文件名(可选)
    """
    
    if output_file is None:
        audio_name = Path(audio_file).stem
        output_file = f"{audio_name}_amplitude_analysis.json"
    
    # 降采样以减少文件大小
    downsampled_data = amplitude_data[::downsample_factor]
    downsampled_time = np.linspace(0, len(amplitude_data)/sample_rate, len(downsampled_data))
    
    # 计算更多统计信息
    percentiles = np.percentile(amplitude_data, [1, 5, 10, 25, 50, 75, 90, 95, 99])
    
    # 计算dB值
    amplitude_db = 20 * np.log10(np.abs(amplitude_data) + 1e-10)
    
    # 检测峰值点 (超过RMS 3倍的点)
    peak_threshold = stats['rms'] * 3
    peak_indices = np.where(np.abs(amplitude_data) > peak_threshold)[0]
    peak_times = peak_indices / sample_rate
    peak_values = amplitude_data[peak_indices]
    
    # 检测静音段 (低于RMS 0.1倍的连续段)
    silence_threshold = stats['rms'] * 0.1
    silence_mask = np.abs(amplitude_data) < silence_threshold
    
    # 构建JSON数据结构
    amplitude_json = {
        "metadata": {
            "audio_file": audio_file,
            "analysis_timestamp": datetime.now().isoformat(),
            "sample_rate": int(sample_rate),
            "audio_duration_seconds": float(len(amplitude_data) / sample_rate),
            "total_samples": int(len(amplitude_data)),
            "downsample_factor": downsample_factor,
            "downsampled_samples": len(downsampled_data)
        },
        
        "amplitude_statistics": {
            "maximum": float(stats['max']),
            "minimum": float(stats['min']),
            "mean": float(stats['mean']),
            "standard_deviation": float(stats['std']),
            "rms": float(stats['rms']),
            "peak_to_peak": float(stats['peak_to_peak']),
            "maximum_db": float(np.max(amplitude_db)),
            "minimum_db": float(np.min(amplitude_db[amplitude_db > -np.inf])),
            "mean_db": float(np.mean(amplitude_db[amplitude_db > -np.inf]))
        },
        
        "percentiles": {
            "p01": float(percentiles[0]),
            "p05": float(percentiles[1]),
            "p10": float(percentiles[2]),
            "p25": float(percentiles[3]),
            "p50": float(percentiles[4]),  # 中位数
            "p75": float(percentiles[5]),
            "p90": float(percentiles[6]),
            "p95": float(percentiles[7]),
            "p99": float(percentiles[8])
        },
        
        "peak_analysis": {
            "peak_threshold": float(peak_threshold),
            "peak_count": int(len(peak_indices)),
            "peak_times": peak_times[:50].tolist() if len(peak_times) > 0 else [],  # 前50个峰值
            "peak_values": peak_values[:50].tolist() if len(peak_values) > 0 else []
        },
        
        "silence_analysis": {
            "silence_threshold": float(silence_threshold),
            "silence_percentage": float(np.sum(silence_mask) / len(silence_mask) * 100),
            "total_silence_samples": int(np.sum(silence_mask))
        },
        
        "downsampled_data": {
            "time_points": downsampled_time.tolist(),
            "amplitude_values": downsampled_data.tolist(),
            "amplitude_db_values": (20 * np.log10(np.abs(downsampled_data) + 1e-10)).tolist()
        },
        
        "amplitude_distribution": {
            "histogram_bins": 50,
            "histogram_counts": np.histogram(amplitude_data, bins=50)[0].tolist(),
            "histogram_edges": np.histogram(amplitude_data, bins=50)[1].tolist()
        }
    }
    
    # 保存JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(amplitude_json, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 振幅分析数据已保存为: {output_file}")
    print(f"📊 文件大小信息:")
    print(f"   • 原始数据点: {len(amplitude_data):,}")
    print(f"   • 降采样后: {len(downsampled_data):,} (降采样因子: {downsample_factor})")
    print(f"   • 检测到峰值: {len(peak_indices)} 个")
    print(f"   • 静音比例: {np.sum(silence_mask) / len(silence_mask) * 100:.1f}%")
    
    return output_file


def load_amplitude_from_json(json_file):
    """
    从JSON文件加载振幅分析数据
    
    参数:
    - json_file: JSON文件路径
    
    返回:
    - 振幅分析数据字典
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📂 成功加载振幅分析数据: {json_file}")
        print(f"🎵 音频文件: {data['metadata']['audio_file']}")
        print(f"📊 采样率: {data['metadata']['sample_rate']} Hz")
        print(f"⏱️  时长: {data['metadata']['audio_duration_seconds']:.2f} 秒")
        print(f"🔢 总样本数: {data['metadata']['total_samples']:,}")
        
        return data
        
    except FileNotFoundError:
        print(f"❌ 找不到文件: {json_file}")
        return None
    except json.JSONDecodeError:
        print(f"❌ JSON文件格式错误: {json_file}")
        return None


def demonstrate_amplitude_calculations():
    """演示振幅计算的数学公式"""
    print("\n\n🧮 振幅计算公式详解:")
    print("=" * 60)
    
    print("📐 基本公式:")
    print("   振幅 A(t) = 信号在时刻t的瞬时值")
    print("   峰值振幅 = max(|A(t)|)")
    print("   RMS振幅 = sqrt(mean(A(t)²))")
    print("   平均绝对振幅 = mean(|A(t)|)")
    print()
    
    print("🔄 单位转换:")
    print("   振幅 → dB: 20 * log10(|amplitude|)")
    print("   dB → 振幅: 10^(dB/20)")
    print("   功率 = 振幅²")
    print("   功率dB = 10 * log10(功率)")
    print()
    
    print("📊 常见振幅值对照:")
    amplitudes = [1.0, 0.5, 0.1, 0.01, 0.001]
    for amp in amplitudes:
        db = 20 * np.log10(amp)
        print(f"   振幅 {amp:5.3f} = {db:6.1f} dB")


if __name__ == "__main__":
    # 执行振幅解释
    amplitude_data, sample_rate, stats = explain_amplitude_calculation()
    
    # 数学公式演示
    demonstrate_amplitude_calculations()
    
    print(f"\n\n🎉 振幅分析完成！")
    print(f"样本总数: {len(amplitude_data):,}")
    print(f"振幅统计: {stats}")
    
    # 演示JSON加载功能
    print("\n📂 JSON文件加载演示:")
    print("-" * 30)
    json_filename = f"{Path('molihua.mp4').stem}_amplitude_analysis.json"
    if Path(json_filename).exists():
        loaded_data = load_amplitude_from_json(json_filename)
        if loaded_data:
            print("✅ JSON数据加载成功！")
            print(f"🔍 可用的数据字段: {list(loaded_data.keys())}")
    else:
        print(f"⚠️  JSON文件不存在: {json_filename}")
    
    print("\n📝 使用说明:")
    print("  • 振幅分析结果已保存为JSON格式")
    print("  • 可使用 load_amplitude_from_json() 函数重新加载数据")
    print("  • JSON文件包含完整的统计信息、降采样数据和分析结果") 