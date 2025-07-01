"""详细演示 tempo 和 beats 的含义和数据结构"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

# 配置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号


def analyze_tempo_and_beats(audio_file="molihua.mp4"):
    """详细分析音频的 tempo 和 beats"""
    
    print("🎵 音频节拍分析演示")
    print("=" * 50)
    
    # 加载音频
    try:
        y, sr = librosa.load(audio_file, duration=60)  # 只分析前60秒
        print(f"📁 加载音频文件: {audio_file}")
        print(f"📊 采样率: {sr} Hz")
        print(f"⏱️  音频长度: {len(y)/sr:.2f} 秒")
        print()
        
    except FileNotFoundError:
        print(f"❌ 找不到文件: {audio_file}")
        return
    
    # 1. 节拍检测
    print("🔍 正在进行节拍检测...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    
    # 将节拍帧位置转换为时间
    beats = librosa.frames_to_time(beat_frames, sr=sr)
    
    print("\n📈 节拍检测结果:")
    print("-" * 30)
    
    # 2. Tempo 分析
    # 提取tempo值（librosa返回的可能是数组）
    tempo_value = tempo if isinstance(tempo, (int, float)) else tempo[0]
    
    print(f"🥁 Tempo (节拍速度):")
    print(f"   类型: {type(tempo)}")
    print(f"   值: {tempo_value:.2f} BPM")
    print(f"   含义: 每分钟 {tempo_value:.1f} 拍")
    
    # 计算拍间间隔
    beat_interval = 60.0 / tempo_value
    print(f"   拍间间隔: {beat_interval:.3f} 秒")
    
    # Tempo 分类
    if tempo_value < 60:
        tempo_class = "极慢 (Largo)"
    elif tempo_value < 80:
        tempo_class = "慢速 (Adagio/Andante)"
    elif tempo_value < 120:
        tempo_class = "中速 (Moderato)"
    elif tempo_value < 160:
        tempo_class = "快速 (Allegro)"
    else:
        tempo_class = "极快 (Presto)"
    
    print(f"   分类: {tempo_class}")
    print()
    
    # 3. Beats 分析
    print(f"🎯 Beats (拍点位置):")
    print(f"   原始帧索引类型: {type(beat_frames)}")
    print(f"   原始帧索引形状: {beat_frames.shape}")
    print(f"   拍点总数: {len(beat_frames)} 个")
    print(f"   时间范围: {beats[0]:.3f}s ~ {beats[-1]:.3f}s")
    print(f"   帧位置范围: {beat_frames[0]} ~ {beat_frames[-1]} 帧")
    
    # 显示前10个拍点的时间和帧位置
    print(f"   前10个拍点 (时间 | 帧位置):")
    for i, (beat_time, beat_frame) in enumerate(zip(beats[:10], beat_frames[:10])):
        print(f"     拍{i+1}: {beat_time:.3f}s | 第{beat_frame}帧")
    
    if len(beats) > 10:
        print(f"     ... (还有 {len(beats)-10} 个拍点)")
    
    print()
    print("💡 说明: librosa.beat.beat_track() 返回帧索引，我们将其转换为时间")
    
    # 4. 节拍规律性分析
    print("📊 节拍规律性分析:")
    print("-" * 30)
    
    # 计算相邻拍点间隔
    if len(beats) > 1:
        beat_intervals = np.diff(beats)
        avg_interval = np.mean(beat_intervals)
        std_interval = np.std(beat_intervals)
        
        print(f"   平均拍间间隔: {avg_interval:.3f}s")
        print(f"   标准差: {std_interval:.3f}s")
        print(f"   规律性: {'高' if std_interval < 0.05 else '中' if std_interval < 0.1 else '低'}")
        
        # 理论拍间间隔 vs 实际拍间间隔
        theoretical_interval = 60.0 / tempo_value
        print(f"   理论拍间间隔: {theoretical_interval:.3f}s")
        print(f"   误差: {abs(avg_interval - theoretical_interval):.3f}s")
    
    print()
    
    # 5. 保存beats信息到JSON文件
    print("💾 保存beats信息到JSON文件...")
    
    # 准备要保存的数据
    beats_data = {
        "audio_file": audio_file,
        "metadata": {
            "sample_rate": int(sr),
            "audio_duration_seconds": float(len(y) / sr),
            "analysis_timestamp": str(np.datetime64('now'))
        },
        "tempo": {
            "value": float(tempo_value),
            "classification": tempo_class,
            "beat_interval_seconds": float(beat_interval)
        },
        "beats": {
            "total_count": int(len(beats)),
            "time_positions": beats.tolist(),  # 转换为Python list
            "frame_positions": beat_frames.tolist(),  # 转换为Python list
            "time_range": {
                "start": float(beats[0]) if len(beats) > 0 else None,
                "end": float(beats[-1]) if len(beats) > 0 else None
            }
        },
        "analysis": {
            "beat_intervals": {
                "values": beat_intervals.tolist() if len(beats) > 1 else [],
                "average": float(avg_interval) if len(beats) > 1 else None,
                "standard_deviation": float(std_interval) if len(beats) > 1 else None,
                "regularity": "高" if len(beats) > 1 and std_interval < 0.05 else "中" if len(beats) > 1 and std_interval < 0.1 else "低" if len(beats) > 1 else None
            },
            "theoretical_vs_actual": {
                "theoretical_interval": float(theoretical_interval),
                "actual_average_interval": float(avg_interval) if len(beats) > 1 else None,
                "error": float(abs(avg_interval - theoretical_interval)) if len(beats) > 1 else None
            }
        }
    }
    
    # 生成JSON文件名
    audio_name = Path(audio_file).stem
    json_filename = f"{audio_name}_beats_analysis.json"
    
    # 保存JSON文件
    try:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(beats_data, f, indent=2, ensure_ascii=False)
        print(f"✅ beats信息已保存到: {json_filename}")
        print(f"📊 保存的数据包括:")
        print(f"   - Tempo: {tempo_value:.2f} BPM")
        print(f"   - 拍点数量: {len(beats)} 个")
        print(f"   - 时间位置: {len(beats)} 个时间点")
        print(f"   - 帧位置: {len(beat_frames)} 个帧索引")
        print(f"   - 分析统计数据")
    except Exception as e:
        print(f"❌ 保存JSON文件时出错: {e}")
    
    print()
    
    # 6. 可视化
    print("🎨 生成可视化图表...")
    
    # 创建图表
    fig, axes = plt.subplots(4, 1, figsize=(12, 14))
    
    # 子图1: 波形和拍点 (时间视图)
    time_axis = np.linspace(0, len(y)/sr, len(y))
    axes[0].plot(time_axis, y, alpha=0.6, color='blue', linewidth=0.5)
    axes[0].vlines(beats, -1, 1, color='red', alpha=0.8, linewidth=2, label=f'Beats ({len(beats)}个)')
    axes[0].set_title(f'音频波形与检测到的拍点 (时间视图)\nTempo: {tempo_value:.1f} BPM')
    axes[0].set_xlabel('时间 (秒)')
    axes[0].set_ylabel('振幅')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 子图2: 波形和拍点 (帧视图)
    frame_axis = np.arange(len(y))
    axes[1].plot(frame_axis, y, alpha=0.6, color='blue', linewidth=0.5)
    axes[1].vlines(beat_frames, -1, 1, color='red', alpha=0.8, linewidth=2, label=f'Beat Frames ({len(beat_frames)}个)')
    axes[1].set_title(f'音频波形与检测到的拍点 (帧视图)\n帧率: {sr} Hz, 帧范围: 0-{len(y)-1}')
    axes[1].set_xlabel('帧位置')
    axes[1].set_ylabel('振幅')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # 子图3: 拍间间隔分布
    if len(beats) > 1:
        beat_intervals = np.diff(beats)
        axes[2].plot(beat_intervals, 'o-', color='green', markersize=4)
        axes[2].axhline(y=avg_interval, color='red', linestyle='--', 
                       label=f'平均间隔: {avg_interval:.3f}s')
        axes[2].axhline(y=theoretical_interval, color='orange', linestyle=':', 
                       label=f'理论间隔: {theoretical_interval:.3f}s')
        axes[2].set_title('相邻拍点间隔变化')
        axes[2].set_xlabel('拍点序号')
        axes[2].set_ylabel('间隔 (秒)')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
    
    # 子图4: 拍点密度直方图
    if len(beats) > 1:
        axes[3].hist(beat_intervals, bins=20, alpha=0.7, color='purple', edgecolor='black')
        axes[3].axvline(x=avg_interval, color='red', linestyle='--', 
                       label=f'平均: {avg_interval:.3f}s')
        axes[3].axvline(x=theoretical_interval, color='orange', linestyle=':', 
                       label=f'理论: {theoretical_interval:.3f}s')
        axes[3].set_title('拍间间隔分布直方图')
        axes[3].set_xlabel('间隔 (秒)')
        axes[3].set_ylabel('频次')
        axes[3].legend()
        axes[3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('beat_analysis_visualization.png', dpi=300, bbox_inches='tight')
    print("💾 可视化图表已保存为: beat_analysis_visualization.png")
    plt.show()
    
    # 7. 实际应用示例
    print("\n🛠️  实际应用场景:")
    print("-" * 30)
    print("1. 🎧 音乐播放器: 自动BPM显示")
    print("2. 🎹 音乐制作: 节拍对齐、量化")
    print("3. 💃 舞蹈应用: 动作同步")
    print("4. 🎵 音乐推荐: 基于节奏的歌曲匹配")
    print("5. 📊 音乐分析: 风格分类、情绪识别")
    
    return tempo_value, beats, beat_frames


def compare_different_music_styles():
    """比较不同音乐风格的节拍特征"""
    print("\n\n🎭 不同音乐风格的典型 Tempo 范围:")
    print("=" * 50)
    
    music_styles = {
        "古典慢板 (Adagio)": "60-80 BPM",
        "民谣/抒情": "70-90 BPM", 
        "流行音乐": "80-120 BPM",
        "摇滚": "100-140 BPM",
        "嘻哈": "70-100 BPM",
        "电子舞曲": "120-140 BPM",
        "重金属": "120-180 BPM",
        "爵士乐": "60-200 BPM (变化很大)",
    }
    
    for style, bpm_range in music_styles.items():
        print(f"🎵 {style:<15}: {bpm_range}")


def demonstrate_beat_tracking_accuracy():
    """演示节拍检测的准确性"""
    print("\n\n🎯 节拍检测算法说明:")
    print("=" * 50)
    print("📋 librosa.beat.beat_track() 使用的方法:")
    print("1. 🔊 提取频谱特征")
    print("2. 📈 计算频谱通量 (onset strength)")
    print("3. 🔄 自相关分析找出周期性")
    print("4. 🎯 动态规划确定最佳拍点序列")
    print()
    print("⚠️  可能的挑战:")
    print("• 复杂节拍 (如爵士乐)")
    print("• 渐变 tempo")
    print("• 多层次节奏")
    print("• 背景噪音")


if __name__ == "__main__":
    # 主要演示
    tempo, beats, beat_frames = analyze_tempo_and_beats()
    
    # 额外信息
    compare_different_music_styles()
    demonstrate_beat_tracking_accuracy()
    
    print(f"\n\n🎉 分析完成！")
    print(f"检测到的 Tempo: {tempo:.2f} BPM")
    print(f"检测到的拍点: {len(beats)} 个")
    print(f"检测到的拍点帧位置: {len(beat_frames)} 个") 