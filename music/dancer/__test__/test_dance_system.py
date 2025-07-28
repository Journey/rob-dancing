from music.dancer.dance_system import DanceSystem
# 配置机器人参数
robot_config = {
    'joint_limits': {
        'head_yaw': {'min': -90, 'max': 90},
        'head_pitch': {'min': -45, 'max': 45},
        # ... 其他关节限制
    },
    'balance_center': [0, 0, 0.5],  # 重心位置
    'support_polygon': [[-0.1, -0.1], [0.1, -0.1], [0.1, 0.1], [-0.1, 0.1]]
}

# 创建舞蹈系统
dance_system = DanceSystem(robot_config)

# 从音乐文件创建舞蹈
dance_data = dance_system.create_dance_from_music('examples/molihua.mp4')

# 保存舞蹈序列
dance_system.save_dance_sequence(dance_data, 'molihua_dance.json')

# 可视化舞蹈
dance_system.visualize_dance(dance_data)