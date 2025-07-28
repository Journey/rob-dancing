"""分析 beats 数组的实际数据结构和单位"""

import librosa
import numpy as np


def analyze_beats_structure(audio_file="molihua.mp4"):
    """详细分析beats数组的数据结构"""
    
    print("🔍 Beats 数组结构分析")
    print("=" * 60)
    
    try:
        # 加载音频
        y, sr = librosa.load(audio_file)
        duration = len(y) / sr
        
        print(f"📁 音频文件: {audio_file}")
        print(f"⏱️  音频时长: {duration:.2f} 秒 ({duration/60:.2f} 分钟)")
        print(f"📊 采样率: {sr} Hz")
        print(f"🎵 音频样本数: {len(y):,}")
        print()
        
        # 进行节拍检测
        print("🎯 进行节拍检测...")
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        print("\n📈 原始返回值分析:")
        print("-" * 40)
        tempo_float = float(tempo) if hasattr(tempo, '__iter__') else tempo
        print(f"🥁 Tempo: {tempo_float:.2f} BPM")
        print(f"🎯 Beats 类型: {type(beats)}")
        print(f"🎯 Beats 形状: {beats.shape}")
        print(f"🎯 Beats 数据类型: {beats.dtype}")
        print()
        
        # 关键发现：beats 是帧索引，不是时间！
        print("❗ 重要发现：beats 数组的真实含义")
        print("-" * 40)
        print(f"🔢 Beats 最小值: {beats.min()}")
        print(f"🔢 Beats 最大值: {beats.max()}")
        print(f"🔢 Beats 总数: {len(beats)}")
        
        # 检查默认帧参数
        hop_length = 512  # librosa默认值
        frame_rate = sr / hop_length
        total_frames = len(y) // hop_length
        
        print(f"\n🎼 音频帧分析:")
        print("-" * 40)
        print(f"📏 Hop length: {hop_length} 样本")
        print(f"📊 帧率: {frame_rate:.2f} 帧/秒")
        print(f"🎵 总帧数: {total_frames:,}")
        print(f"⏱️  每帧时长: {hop_length/sr*1000:.2f} 毫秒")
        
        # 验证：最大beats值是否合理
        print(f"\n✅ 验证分析:")
        print("-" * 40)
        print(f"🔍 最大beats值 {beats.max()} 是否 < 总帧数 {total_frames}？")
        print(f"   结果: {'是' if beats.max() < total_frames else '否'}")
        
        # 转换为时间
        print(f"\n🕒 转换为时间戳:")
        print("-" * 40)
        
        # 方法1：使用 librosa.frames_to_time
        beats_time_method1 = librosa.frames_to_time(beats, sr=sr, hop_length=hop_length)
        
        # 方法2：手动计算
        beats_time_method2 = beats * hop_length / sr
        
        print(f"📋 转换方法对比:")
        print(f"   方法1 (librosa.frames_to_time): 前5个时间戳")
        for i in range(min(5, len(beats_time_method1))):
            print(f"     拍{i+1}: {beats_time_method1[i]:.3f}s")
        
        print(f"   方法2 (手动计算): 前5个时间戳")
        for i in range(min(5, len(beats_time_method2))):
            print(f"     拍{i+1}: {beats_time_method2[i]:.3f}s")
        
        print(f"\n📊 时间范围检查:")
        print(f"   最早拍点: {beats_time_method1[0]:.3f}s")
        print(f"   最晚拍点: {beats_time_method1[-1]:.3f}s")
        print(f"   是否在音频范围内: {'是' if beats_time_method1[-1] <= duration else '否'}")
        
        # 显示为什么会有7388这样的大数值
        print(f"\n🤔 为什么 beats 值这么大？")
        print("-" * 40)
        print(f"💡 解释：")
        print(f"   • beats 数组存储的是帧索引（frame indices），不是时间")
        print(f"   • 每帧代表 {hop_length} 个音频样本")
        print(f"   • 帧索引 {beats.max()} 对应时间: {beats.max() * hop_length / sr:.2f}s")
        print(f"   • 这在 {duration:.0f}秒 的音频中是合理的")
        
        # 对比说明
        print(f"\n📝 数据转换总结:")
        print("-" * 40)
        print(f"🎯 原始 beats (帧索引): [0 ~ {beats.max()}]")
        print(f"🕒 转换后 beats (时间): [0.0s ~ {beats_time_method1[-1]:.2f}s]")
        print(f"🎵 平均拍间间隔: {np.mean(np.diff(beats_time_method1)):.3f}s")
        print(f"🥁 理论拍间间隔: {60/tempo:.3f}s")
        
        return beats, beats_time_method1, tempo
        
    except FileNotFoundError:
        print(f"❌ 找不到文件: {audio_file}")
        return None, None, None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None, None, None


def demonstrate_frame_to_time_conversion():
    """演示帧索引到时间的转换"""
    print(f"\n\n🎓 帧索引 ↔ 时间转换教程")
    print("=" * 60)
    
    print("📚 基本概念:")
    print("   • 音频被分割成连续的帧（frames）")
    print("   • 每帧包含固定数量的样本（hop_length）")
    print("   • 帧索引从0开始计数")
    print()
    
    print("🔢 转换公式:")
    print("   时间(秒) = 帧索引 × hop_length ÷ 采样率")
    print("   帧索引 = 时间(秒) × 采样率 ÷ hop_length")
    print()
    
    # 示例计算
    sr = 22050
    hop_length = 512
    
    print("💡 示例计算 (采样率=22050Hz, hop_length=512):")
    examples = [100, 1000, 7388]
    
    for frame_idx in examples:
        time_sec = frame_idx * hop_length / sr
        print(f"   帧索引 {frame_idx:>4} → 时间 {time_sec:>6.3f}秒")


def fix_common_misconceptions():
    """澄清常见误解"""
    print(f"\n\n❌ 常见误解 vs ✅ 正确理解")
    print("=" * 60)
    
    misconceptions = [
        {
            "wrong": "beats 数组直接表示时间戳",
            "correct": "beats 数组表示帧索引，需要转换为时间"
        },
        {
            "wrong": "beats 的大数值（如7388）表示7388秒",
            "correct": "7388是帧索引，对应约16.8秒（7388×512÷22050）"
        },
        {
            "wrong": "3分钟音频不可能有7388个拍点",
            "correct": "3分钟音频可能有约1000帧索引为7388的拍点"
        },
        {
            "wrong": "librosa.beat.beat_track 返回错误结果",
            "correct": "返回结果正确，只是需要理解数据格式"
        }
    ]
    
    for i, item in enumerate(misconceptions, 1):
        print(f"{i}. ❌ 误解: {item['wrong']}")
        print(f"   ✅ 正确: {item['correct']}")
        print()


def show_correct_usage():
    """展示正确的使用方法"""
    print(f"\n\n🛠️  正确使用 beats 的方法")
    print("=" * 60)
    
    code_example = '''
# ✅ 正确的做法
import librosa

# 1. 获取节拍信息
tempo, beats_frames = librosa.beat.beat_track(y=audio, sr=sr)

# 2. 转换为时间戳
beats_time = librosa.frames_to_time(beats_frames, sr=sr)

# 3. 现在可以使用时间戳了
print(f"第一拍在: {beats_time[0]:.3f}秒")
print(f"最后一拍在: {beats_time[-1]:.3f}秒")

# 4. 计算拍间间隔
intervals = np.diff(beats_time)
print(f"平均拍间间隔: {np.mean(intervals):.3f}秒")
'''
    
    print("💻 代码示例:")
    print(code_example)


if __name__ == "__main__":
    # 主要分析
    beats_frames, beats_time, tempo = analyze_beats_structure()
    
    # 教程部分
    demonstrate_frame_to_time_conversion()
    fix_common_misconceptions()
    show_correct_usage()
    
    if beats_frames is not None:
        print(f"\n\n🎉 分析结论:")
        print(f"您看到的 beats 最大值 {beats_frames.max()} 是帧索引")
        print(f"对应的实际时间是: {beats_time[-1]:.2f}秒")
        print(f"这在 3分钟的音频中是完全正常的！") 