function robtic() {
        let scene, camera, renderer, head, body, leftArm, rightArm, leftLeg, rightLeg;
        let upperTorso, waist; // 身体部分变量
        let leftThigh, rightThigh; // 大腿变量
        let bodyGroup; // 身体组
        let spotLight1, spotLight2; // 全局光源变量
        let mouseX = 0, mouseY = 0;
        let isMouseDown = false;
        let cameraAngleX = 0, cameraAngleY = 0;
        
        // FBX模型相关变量
        let fbxModel = null;
        let fbxLoader = null;
        
        // 舞蹈数据相关变量
        let danceData = null;
        let currentDanceIndex = 0;
        let danceStartTime = 0;
        let isDanceMode = false;
        let danceModeEnabled = true;
        
        // 音频和节拍相关变量
        let audioPlayer;
        let beatSyncEnabled = true;
        let currentBeatIndex = 0;
        let beatAnimation = {
            isAnimating: false,
            startTime: 0,
            duration: 0.3, // 摆动持续时间
            amplitude: 0.3  // 摆动幅度
        };
        let armAnimation = {
            isAnimating: false,
            startTime: 0,
            duration: 0.4, // 手臂摆动持续时间
            amplitude: 0.5, // 手臂摆动幅度
            isLeftArm: true // 当前是否为左臂摆动
        };
        
        // 创建安全的材质
        function createSafeMaterial(originalMaterial) {
            // 创建基础材质作为后备
            const safeMaterial = new THREE.MeshPhongMaterial({
                color: 0xCCCCCC,
                shininess: 30,
                specular: 0x222222
            });
            
            // 如果原始材质有效，尝试复制其属性
            if (originalMaterial) {
                try {
                    if (originalMaterial.color) {
                        safeMaterial.color.copy(originalMaterial.color);
                    }
                    if (originalMaterial.map && originalMaterial.map.image) {
                        safeMaterial.map = originalMaterial.map;
                    }
                } catch (error) {
                    console.warn('材质复制失败，使用默认材质:', error);
                }
            }
            
            return safeMaterial;
        }
        
        // FBX加载函数
        function loadFBXModel(url, onLoad, onProgress, onError) {
            if (!fbxLoader) {
                fbxLoader = new THREE.FBXLoader();
            }
            
            fbxLoader.load(
                url,
                function(object) {
                    console.log('FBX模型加载成功:', object);
                    
                    // 调整模型大小和位置
                    object.scale.set(0.01, 0.01, 0.01); // 缩小模型
                    object.position.set(0, 0, 0); // 居中放置
                    
                    // 启用阴影并修复材质
                    object.traverse(function(child) {
                        if (child.isMesh) {
                            child.castShadow = true;
                            child.receiveShadow = true;
                            
                            // 修复材质问题
                            if (child.material) {
                                try {
                                    // 检查材质是否有效
                                    if (!child.material.color || 
                                        (child.material.map && !child.material.map.image) ||
                                        (child.material.normalMap && !child.material.normalMap.image) ||
                                        (child.material.specularMap && !child.material.specularMap.image)) {
                                        
                                        // 使用安全材质替换有问题的材质
                                        child.material = createSafeMaterial(child.material);
                                    } else {
                                        // 清理无效的纹理引用
                                        if (child.material.map && !child.material.map.image) {
                                            child.material.map = null;
                                        }
                                        if (child.material.normalMap && !child.material.normalMap.image) {
                                            child.material.normalMap = null;
                                        }
                                        if (child.material.specularMap && !child.material.specularMap.image) {
                                            child.material.specularMap = null;
                                        }
                                        
                                        // 设置默认材质属性
                                        child.material.shininess = 30;
                                        child.material.specular = 0x222222;
                                        child.material.needsUpdate = true;
                                    }
                                } catch (error) {
                                    console.warn('材质处理失败，使用默认材质:', error);
                                    child.material = createSafeMaterial(null);
                                }
                            }
                        }
                    });
                    
                    // 移除现有的FBX模型（如果存在）
                    if (fbxModel) {
                        scene.remove(fbxModel);
                    }
                    
                    // 添加新模型到场景
                    fbxModel = object;
                    scene.add(fbxModel);
                    
                    // 设置初始可见性
                    const fbxModelCheckbox = document.getElementById('showFBXModel');
                    if (fbxModelCheckbox) {
                        fbxModel.visible = fbxModelCheckbox.checked;
                    }
                    
                    if (onLoad) onLoad(object);
                },
                function(progress) {
                    console.log('FBX加载进度:', (progress.loaded / progress.total * 100) + '%');
                    if (onProgress) onProgress(progress);
                },
                function(error) {
                    console.error('FBX加载失败:', error);
                    if (onError) onError(error);
                }
            );
        }
        
        // 加载Uzi FBX模型
        function loadUziModel() {
            // 设置纹理加载管理器来处理缺失的纹理
            const textureLoader = new THREE.TextureLoader();
            textureLoader.crossOrigin = 'anonymous';
            
            loadFBXModel(
                'statics/murder-drones-uzi-plushie/source/Uzi.fbx',
                function(object) {
                    console.log('Uzi模型加载完成');
                    
                    // 调整模型位置和大小
                    object.scale.set(0.02, 0.02, 0.02); // 稍微放大一点
                    object.position.set(0, 1, 0); // 调整位置到合适高度
                    
                    // 确保模型面向相机
                    object.rotation.y = Math.PI;
                    
                    // 最终材质检查和修复
                    object.traverse(function(child) {
                        if (child.isMesh && child.material) {
                            // 确保所有材质都是有效的
                            if (!child.material.color) {
                                child.material = createSafeMaterial(null);
                            }
                        }
                    });
                    
                    // 可以在这里添加特定的动画或调整
                },
                function(progress) {
                    console.log('加载进度:', Math.round(progress.loaded / progress.total * 100) + '%');
                },
                function(error) {
                    console.error('加载失败:', error);
                    // 如果FBX加载失败，确保自定义角色可见
                    if (bodyGroup) {
                        bodyGroup.visible = true;
                    }
                    // 隐藏FBX模型复选框
                    const fbxModelCheckbox = document.getElementById('showFBXModel');
                    if (fbxModelCheckbox) {
                        fbxModelCheckbox.checked = false;
                        fbxModelCheckbox.disabled = true;
                    }
                }
            );
        }

        function amplitude_data_producer() {
           let counter = 0;
           let val = Math.random();

           return function() {
            if(counter === 2) {
                val = Math.max(0.3, Math.random());
                counter = 0;
            } else {
                counter++;
            }

            return val;
           }
        }

        let amplitude_data = amplitude_data_producer();

        function init() {
            // 创建场景
            scene = new THREE.Scene();
            // 创建舞台背景的渐变效果
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 512;
            const context = canvas.getContext('2d');
            const gradient = context.createLinearGradient(0, 0, 0, canvas.height);
            gradient.addColorStop(0, '#2C1810'); // 深褐色顶部
            gradient.addColorStop(0.5, '#4A2C47'); // 紫色中间
            gradient.addColorStop(1, '#1A1A2E'); // 深蓝色底部
            context.fillStyle = gradient;
            context.fillRect(0, 0, canvas.width, canvas.height);
            const texture = new THREE.CanvasTexture(canvas);
            scene.background = texture;
            
            // 创建相机
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 3, 10);
            camera.lookAt(0, 3, 0);
            
            // 创建渲染器
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            document.getElementById('container').appendChild(renderer.domElement);
            
            // 改进的光照系统
            // 环境光 - 模拟舞台的基础照明
            const ambientLight = new THREE.AmbientLight(0x4A4A6A, 0.3);
            scene.add(ambientLight);
            
            // 主聚光灯 - 模拟舞台聚光灯
            spotLight1 = new THREE.SpotLight(0xFFFFFF, 1.5, 30, Math.PI / 4, 0.3, 1);
            spotLight1.position.set(5, 12, 8);
            spotLight1.target.position.set(0, 3, 0);
            spotLight1.castShadow = true;
            spotLight1.shadow.mapSize.width = 2048;
            spotLight1.shadow.mapSize.height = 2048;
            spotLight1.shadow.camera.near = 0.1;
            spotLight1.shadow.camera.far = 50;
            scene.add(spotLight1);
            scene.add(spotLight1.target);
            
            // 侧光 - 增加立体感
            spotLight2 = new THREE.SpotLight(0xFF9999, 0.8, 25, Math.PI / 3, 0.5, 1);
            spotLight2.position.set(-8, 8, 5);
            spotLight2.target.position.set(0, 3, 0);
            spotLight2.castShadow = true;
            spotLight2.shadow.mapSize.width = 1024;
            spotLight2.shadow.mapSize.height = 1024;
            scene.add(spotLight2);
            scene.add(spotLight2.target);
            
            // 背光 - 轮廓光效果
            const rimLight = new THREE.DirectionalLight(0x9999FF, 0.6);
            rimLight.position.set(-5, 5, -8);
            scene.add(rimLight);
            
            // 点光源 - 增加氛围
            const pointLight = new THREE.PointLight(0xFFAA77, 0.4, 15);
            pointLight.position.set(3, 6, -3);
            scene.add(pointLight);
            
            // 创建人物模型
            createCharacter();
            
            // 创建专业舞台地板
            const stageGeometry = new THREE.PlaneGeometry(40, 40);
            
            // 创建木质地板纹理
            const stageCanvas = document.createElement('canvas');
            stageCanvas.width = 512;
            stageCanvas.height = 512;
            const stageContext = stageCanvas.getContext('2d');
            
            // 绘制木质纹理
            stageContext.fillStyle = '#8B4513';
            stageContext.fillRect(0, 0, 512, 512);
            
            // 添加木板条纹
            for (let i = 0; i < 20; i++) {
                const y = i * 25.6;
                stageContext.fillStyle = i % 2 === 0 ? '#A0522D' : '#8B4513';
                stageContext.fillRect(0, y, 512, 25.6);
                
                // 添加木纹细节
                stageContext.strokeStyle = '#654321';
                stageContext.lineWidth = 1;
                stageContext.beginPath();
                stageContext.moveTo(0, y + 12.8);
                stageContext.lineTo(512, y + 12.8);
                stageContext.stroke();
            }
            
            // 添加光泽效果
            const stageTexture = new THREE.CanvasTexture(stageCanvas);
            stageTexture.wrapS = THREE.RepeatWrapping;
            stageTexture.wrapT = THREE.RepeatWrapping;
            stageTexture.repeat.set(2, 2);
            
            const stageMaterial = new THREE.MeshPhongMaterial({ 
                map: stageTexture,
                shininess: 80,
                specular: 0x333333
            });
            
            const stage = new THREE.Mesh(stageGeometry, stageMaterial);
            stage.rotation.x = -Math.PI / 2;
            stage.receiveShadow = true;
            stage.position.y = -0.5;
            scene.add(stage);
            
            // 添加舞台边框装饰
            const borderGeometry = new THREE.BoxGeometry(42, 0.3, 42);
            const borderMaterial = new THREE.MeshPhongMaterial({ 
                color: 0x2C1810,
                shininess: 60 
            });
            const border = new THREE.Mesh(borderGeometry, borderMaterial);
            border.position.y = -0.65;
            border.receiveShadow = true;
            scene.add(border);
            
            // 初始化音频
            initAudio();
            
            // 加载舞蹈数据
            loadDanceData().then(success => {
                if (success) {
                    console.log('舞蹈数据加载完成');
                }
            });
            
            // 加载FBX模型（带错误处理）
            try {
                //loadUziModel();
            } catch (error) {
                console.error('FBX加载初始化失败:', error);
                // 禁用FBX功能
                const fbxModelCheckbox = document.getElementById('showFBXModel');
                if (fbxModelCheckbox) {
                    fbxModelCheckbox.checked = false;
                    fbxModelCheckbox.disabled = true;
                }
            }
            
            // 添加事件监听器
            setupEventListeners();
            
            // 开始渲染
            animate();
        }
        
        // 加载舞蹈数据
        async function loadDanceData() {
            try {
                const response = await fetch('data/molihua_dance.json');
                //const response = await fetch('data/sjg_dance.json');
                danceData = await response.json();
                console.log('舞蹈数据加载成功:', danceData);
                return true;
            } catch (error) {
                console.error('加载舞蹈数据失败:', error);
                return false;
            }
        }
        
        // 开始舞蹈模式
        function startDanceMode() {
            if (!danceData) {
                console.warn('舞蹈数据未加载');
                return;
            }
            isDanceMode = true;
            currentDanceIndex = 0;
            danceStartTime = performance.now();
            console.log('开始舞蹈模式');
        }
        
        // 停止舞蹈模式
        function stopDanceMode() {
            isDanceMode = false;
            currentDanceIndex = 0;
            console.log('停止舞蹈模式');
        }
        
        // 更新舞蹈动画
        function updateDanceAnimation() {
            if (!isDanceMode || !danceModeEnabled || !danceData || !danceData.dance_sequence) return;
            
            const currentTime = (performance.now() - danceStartTime) / 1000;
            const sequence = danceData.dance_sequence;
            
            // 查找当前时间对应的舞蹈动作
            while (currentDanceIndex < sequence.length) {
                const move = sequence[currentDanceIndex];
                const moveEndTime = move.time + move.duration;
                console.log(currentTime, moveEndTime);
                if (currentTime <= moveEndTime) {
                    // 应用当前舞蹈动作
                    applyDanceMove(move, currentTime - move.time, move.duration);
                    break;
                }
                currentDanceIndex++;
            }
            
            // 如果所有动作都完成了，重新开始
            if (currentDanceIndex >= sequence.length) {
                currentDanceIndex = 0;
                danceStartTime = performance.now();
            }
        }
        
        // 应用舞蹈动作
        function applyDanceMove(move, elapsed, duration) {
            //if (!head || !leftArm || !rightArm || !leftLeg || !rightLeg || !leftThigh || !rightThigh) return;
            
            const progress = Math.min(elapsed / duration, 1);
            console.log(progress);
            const intensity = move.intensity || 0.5;
            
            // 增强动作幅度
            const amplitudeMultiplier = 3.0; // 增加动作幅度xx
            // 根据关节类型应用动作
            switch (move.joint) {
                case 'head_yaw':
                    head.rotation.y = THREE.MathUtils.degToRad(move.target_angle * progress * intensity * amplitudeMultiplier);
                    break;
                case 'head_pitch':
                    head.rotation.x = THREE.MathUtils.degToRad(move.target_angle * progress * intensity * amplitudeMultiplier);
                    break;
                case 'shoulder_left':
                    // 手臂摆动 - 前后摆动
                    leftArm.rotation.x = THREE.MathUtils.degToRad(move.target_angle * progress * intensity * amplitudeMultiplier);
                    // 添加一些侧向摆动
                    leftArm.rotation.y = THREE.MathUtils.degToRad(move.target_angle * 0.5 * progress * intensity * amplitudeMultiplier);
                    break;
                case 'shoulder_right':
                    // 手臂摆动 - 前后摆动
                    rightArm.rotation.x = THREE.MathUtils.degToRad(move.target_angle * progress * intensity * amplitudeMultiplier);
                    // 添加一些侧向摆动
                    rightArm.rotation.y = THREE.MathUtils.degToRad(-move.target_angle * 0.5 * progress * intensity * amplitudeMultiplier);
                    break;
                case 'hip_left':
                    // 大腿摆动 - 前后摆动
                    leftThigh.rotation.x = THREE.MathUtils.degToRad(move.target_angle * progress * intensity * amplitudeMultiplier);
                    break;
                case 'hip_right':
                    // 大腿摆动 - 前后摆动
                    rightThigh.rotation.x = THREE.MathUtils.degToRad(move.target_angle * progress * intensity * amplitudeMultiplier);
                    break;
                case 'knee_left':
                    // 膝盖弯曲
                    leftLeg.rotation.z = THREE.MathUtils.degToRad(move.target_angle * progress * intensity * amplitudeMultiplier);
                    break;
                case 'knee_right':
                    // 膝盖弯曲
                    rightLeg.rotation.z = THREE.MathUtils.degToRad(move.target_angle * progress * intensity * amplitudeMultiplier);
                    break;
                case 'ankle_left':
                    // 脚踝动作
                    if (leftLeg.parent && leftLeg.parent.parent) {
                        leftLeg.parent.parent.rotation.z = THREE.MathUtils.degToRad(move.target_angle * 0.8 * progress * intensity * amplitudeMultiplier);
                    }
                    break;
                case 'ankle_right':
                    // 脚踝动作
                    if (rightLeg.parent && rightLeg.parent.parent) {
                        rightLeg.parent.parent.rotation.z = THREE.MathUtils.degToRad(move.target_angle * 0.8 * progress * intensity * amplitudeMultiplier);
                    }
                    break;
            }
        }
        
        function initAudio() {
            audioPlayer = document.getElementById('audioPlayer');
            
            audioPlayer.addEventListener('loadedmetadata', function() {
                updateTimeDisplay();
            });
            
            audioPlayer.addEventListener('timeupdate', function() {
                updateTimeDisplay();
                updateProgress();
                checkBeatSync();
            });
            
            audioPlayer.addEventListener('ended', function() {
                document.getElementById('playPauseBtn').textContent = '播放';
                document.getElementById('playPauseBtn').classList.remove('playing');
                currentBeatIndex = 0;
            });
        }
        
        function togglePlayPause() {
            const btn = document.getElementById('playPauseBtn');
            if (audioPlayer.paused) {
                audioPlayer.play();
                btn.textContent = '暂停';
                btn.classList.add('playing');
                // 开始舞蹈模式
                startDanceMode();
            } else {
                audioPlayer.pause();
                btn.textContent = '播放';
                btn.classList.remove('playing');
                // 停止舞蹈模式
                stopDanceMode();
            }
        }
        
            function stopAudio() {
             audioPlayer.pause();
             audioPlayer.currentTime = 0;
             document.getElementById('playPauseBtn').textContent = '播放';
             document.getElementById('playPauseBtn').classList.remove('playing');
             currentBeatIndex = 0;
             
             // 停止舞蹈模式
             stopDanceMode();
             
             // 重置所有动画状态
             beatAnimation.isAnimating = false;
             armAnimation.isAnimating = false;
             if (leftArm) {
                 leftArm.rotation.set(Math.PI / 12, 0, 0);
             }
             if (rightArm) {
                 rightArm.rotation.set(-Math.PI / 12, 0, 0);
             }
         }
        
        function updateTimeDisplay() {
            const current = formatTime(audioPlayer.currentTime);
            const duration = formatTime(audioPlayer.duration);
            document.getElementById('timeDisplay').textContent = `${current} / ${duration}`;
        }
        
        function updateProgress() {
            if (audioPlayer.duration) {
                const percent = (audioPlayer.currentTime / audioPlayer.duration) * 100;
                document.getElementById('progress').style.width = percent + '%';
            }
        }
        
        function formatTime(seconds) {
            if (isNaN(seconds)) return '00:00';
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        
        function checkBeatSync() {
            if (!beatSyncEnabled || !data.beats || !data.beats.time_positions) return;
            
            const currentTime = audioPlayer.currentTime;
            const beatTimes = data.beats.time_positions;
            
            // 检查是否接近下一个节拍点
            if (currentBeatIndex < beatTimes.length) {
                const nextBeatTime = beatTimes[currentBeatIndex];
                const timeDiff = Math.abs(currentTime - nextBeatTime);
                
                // 如果在节拍点附近（±0.05秒），触发摆动
                 if (timeDiff <= 0.05 && !beatAnimation.isAnimating) {
                     triggerBeatAnimation();
                     triggerArmAnimation();
                     currentBeatIndex++;
                     
                     // 显示节拍指示器
                     const indicator = document.getElementById('beat-indicator');
                     indicator.classList.add('active');
                     setTimeout(() => {
                         indicator.classList.remove('active');
                     }, 200);
                 }
            }
            
            // 重置节拍索引如果播放位置跳跃
            let closestBeatIndex = 0;
            for (let i = 0; i < beatTimes.length; i++) {
                if (beatTimes[i] <= currentTime) {
                    closestBeatIndex = i + 1;
                } else {
                    break;
                }
            }
            currentBeatIndex = Math.max(currentBeatIndex, closestBeatIndex);
        }
        
        function triggerBeatAnimation() {
             beatAnimation.isAnimating = true;
             beatAnimation.startTime = performance.now();
         }
         
         function triggerArmAnimation() {
             armAnimation.isAnimating = true;
             armAnimation.startTime = performance.now();
             // 交替左右手
             armAnimation.isLeftArm = !armAnimation.isLeftArm;
         }
        
        function updateBeatAnimation() {
             if (!beatAnimation.isAnimating) return;
             
             const elapsed = (performance.now() - beatAnimation.startTime) / 1000;
             const progress = elapsed / beatAnimation.duration;
             
             if (progress >= 1) {
                 beatAnimation.isAnimating = false;
                 return;
             }
             
             // 使用正弦波产生平滑的前后摆动
             const angle = Math.sin(progress * Math.PI * 2) * amplitude_data();
             
             // 只在启用节拍同步且没有手动控制时应用
             if (beatSyncEnabled && document.getElementById('headPitch').value == 0) {
                 head.rotation.x = angle;
             }
         }
         
         function updateArmAnimation() {
             if (!armAnimation.isAnimating) return;
             
             const elapsed = (performance.now() - armAnimation.startTime) / 1000;
             const progress = elapsed / armAnimation.duration;
             
             if (progress >= 1) {
                 armAnimation.isAnimating = false;
                 // 重置手臂到原始位置
                 leftArm.rotation.x = 0;
                 rightArm.rotation.x = 0;
                 leftArm.rotation.y = 0;
                 rightArm.rotation.y = 0;
                 return;
             }
             
             // 使用正弦波产生平滑的摆动，先快速上升再缓慢下降
             const angle = Math.sin(progress * Math.PI) * amplitude_data();
             
             if (beatSyncEnabled) {
                 if (armAnimation.isLeftArm) {
                     // 左臂向前摆动
                     //leftArm.rotation.x = -angle;
                     leftArm.rotation.y = angle * 0.5;
                    //  // 右臂稍微后摆保持平衡
                    //  rightArm.rotation.x = angle * 0.3;
                    //  rightArm.rotation.y = -angle * 0.2;
                 } else {
                     // 右臂向前摆动
                     //rightArm.rotation.x = -angle;
                     rightArm.rotation.y = -angle * 0.5;
                     // 左臂稍微后摆保持平衡
                    //  leftArm.rotation.x = angle * 0.3;
                    //  leftArm.rotation.y = angle * 0.2;
                 }
             }
         }
        
        function createCharacter() {
            // 材质定义 - 优化材质
            const skinMaterial = new THREE.MeshPhongMaterial({ color: 0xFFE4B5, shininess: 40, specular: 0x222222 });
            const metalMaterial = new THREE.MeshPhongMaterial({ 
                color: 0xC0C0C0, // 更自然的银色
                shininess: 40,   // 降低光泽度
                specular: 0x222222 
            });
            const hairMaterial = new THREE.MeshPhongMaterial({ color: 0x1A1A1A, shininess: 80 });
            const redMaterial = new THREE.MeshPhongMaterial({ color: 0xB22222, shininess: 25 }); // 更深的红色
            const blueMaterial = new THREE.MeshPhongMaterial({ color: 0x1E3A8A, shininess: 20 }); // 更深的蓝色
            const blackMaterial = new THREE.MeshPhongMaterial({ color: 0x2F2F2F, shininess: 50 });

            // 1. 整体组 - 建立正确的层级结构
            bodyGroup = new THREE.Group();
            bodyGroup.position.y = 0.6;
            scene.add(bodyGroup);

            // 2. 创建骨盆/臀部作为身体中心
            const pelvisGeometry = new THREE.CylinderGeometry(0.35, 0.4, 0.4, 16);
            const pelvis = new THREE.Mesh(pelvisGeometry, skinMaterial);
            pelvis.position.y = 1.0; // 作为身体中心
            pelvis.castShadow = true;
            bodyGroup.add(pelvis);

            // 3. 腿部 - 连接到骨盆
            const thighGeometry = new THREE.CylinderGeometry(0.15, 0.18, 1.0, 12);
            leftThigh = new THREE.Mesh(thighGeometry, skinMaterial);
            leftThigh.position.set(-0.2, -0.3, 0); // 调整连接位置
            leftThigh.castShadow = true;
            pelvis.add(leftThigh);
            
            rightThigh = new THREE.Mesh(thighGeometry, skinMaterial);
            rightThigh.position.set(0.2, -0.3, 0); // 调整连接位置
            rightThigh.castShadow = true;
            pelvis.add(rightThigh);
            
            // 膝关节
            const kneeJointGeometry = new THREE.SphereGeometry(0.12, 12, 8);
            const leftKneeJoint = new THREE.Mesh(kneeJointGeometry, metalMaterial);
            leftKneeJoint.position.set(0, -0.5, 0); // 修正位置
            leftThigh.add(leftKneeJoint);
            
            const rightKneeJoint = new THREE.Mesh(kneeJointGeometry, metalMaterial);
            rightKneeJoint.position.set(0, -0.5, 0); // 修正位置
            rightThigh.add(rightKneeJoint);
            
            // 小腿
            const calfGeometry = new THREE.CylinderGeometry(0.12, 0.15, 0.9, 12);
            leftLeg = new THREE.Mesh(calfGeometry, skinMaterial);
            leftLeg.position.set(0, -0.55, 0);
            leftLeg.castShadow = true;
            leftKneeJoint.add(leftLeg);
            
            rightLeg = new THREE.Mesh(calfGeometry, skinMaterial);
            rightLeg.position.set(0, -0.55, 0);
            rightLeg.castShadow = true;
            rightKneeJoint.add(rightLeg);
            
            // 脚踝关节
            const ankleJointGeometry = new THREE.SphereGeometry(0.1, 12, 8);
            const leftAnkleJoint = new THREE.Mesh(ankleJointGeometry, metalMaterial);
            leftAnkleJoint.position.set(0, -0.55, 0);
            leftLeg.add(leftAnkleJoint);
            
            const rightAnkleJoint = new THREE.Mesh(ankleJointGeometry, metalMaterial);
            rightAnkleJoint.position.set(0, -0.55, 0);
            rightLeg.add(rightAnkleJoint);
            
            // 脚部 - 确保接触地面
            const footGeometry = new THREE.BoxGeometry(0.3, 0.15, 0.6);
            const leftFoot = new THREE.Mesh(footGeometry, skinMaterial);
            leftFoot.position.set(0, -0.075, 0.1); // 确保接触地面
            leftAnkleJoint.add(leftFoot);
            
            const rightFoot = new THREE.Mesh(footGeometry, skinMaterial);
            rightFoot.position.set(0, -0.075, 0.1);
            rightAnkleJoint.add(rightFoot);
            
            // 添加脚趾 - 修正位置和角度
            const toeGeometry = new THREE.CylinderGeometry(0.02, 0.025, 0.08, 8);
            const toeMaterial = new THREE.MeshPhongMaterial({ color: 0xFFE4B5, shininess: 15 });
            
            // 左脚趾 - 修正位置
            for (let i = 0; i < 5; i++) {
                const leftToe = new THREE.Mesh(toeGeometry, toeMaterial);
                leftToe.position.set(-0.1 + i * 0.05, -0.075, 0.3); // 调整间距和位置
                leftToe.rotation.x = Math.PI / 8; // 减小角度
                leftFoot.add(leftToe);
            }
            
            // 右脚趾 - 修正位置
            for (let i = 0; i < 5; i++) {
                const rightToe = new THREE.Mesh(toeGeometry, toeMaterial);
                rightToe.position.set(-0.1 + i * 0.05, -0.075, 0.3); // 调整间距和位置
                rightToe.rotation.x = Math.PI / 8; // 减小角度
                rightFoot.add(rightToe);
            }
            
            // 鞋底 - 修正连接位置
            const soleGeometry = new THREE.BoxGeometry(0.35, 0.08, 0.65);
            const leftSole = new THREE.Mesh(soleGeometry, blackMaterial);
            leftSole.position.set(0, -0.12, 0.02); // 确保与脚部正确连接
            leftFoot.add(leftSole);
            
            const rightSole = new THREE.Mesh(soleGeometry, blackMaterial);
            rightSole.position.set(0, -0.12, 0.02); // 确保与脚部正确连接
            rightFoot.add(rightSole);

            // 4. 躯干下部（蓝色短裤）- 连接到骨盆
            const shortsGeometry = new THREE.CylinderGeometry(0.35, 0.38, 0.4, 16); // 调整比例
            body = new THREE.Mesh(shortsGeometry, blueMaterial);
            body.position.y = 0.45; // 在骨盆上方，紧密连接
            body.castShadow = true;
            pelvis.add(body);

            // 5. 腰部 - 连接到短裤（修正层级结构）
            const waistGeometry = new THREE.CylinderGeometry(0.35, 0.4, 0.25, 16);
            waist = new THREE.Mesh(waistGeometry, skinMaterial);
            waist.position.y = 0.36; // 在短裤上方，紧密连接
            waist.castShadow = true;
            body.add(waist); // 修正：连接到短裤而不是骨盆

            // 6. 躯干上部（红色）- 连接到腰部（修正层级结构）
            const torsoGeometry = new THREE.CylinderGeometry(0.35, 0.4, 0.8, 16); // 调整比例
            upperTorso = new THREE.Mesh(torsoGeometry, redMaterial);
            upperTorso.position.y = 0.4; // 在腰部上方，紧密连接
            upperTorso.castShadow = true;
            waist.add(upperTorso); // 修正：连接到腰部而不是骨盆

            // 添加胸部肌肉轮廓
            const chestGeometry = new THREE.CylinderGeometry(0.35, 0.4, 0.6, 16);
            const chestMaterial = new THREE.MeshPhongMaterial({ color: 0xFFE4B5, shininess: 30 });
            const chest = new THREE.Mesh(chestGeometry, chestMaterial);
            chest.position.y = 0.4;
            chest.castShadow = true;
            upperTorso.add(chest);

            // 添加腹肌轮廓
            const absGeometry = new THREE.BoxGeometry(0.3, 0.4, 0.1);
            const abs = new THREE.Mesh(absGeometry, skinMaterial);
            abs.position.set(0, -0.1, 0.15);
            upperTorso.add(abs);

            // 添加胸肌轮廓
            const pectoralGeometry = new THREE.SphereGeometry(0.25, 16, 12);
            const leftPectoral = new THREE.Mesh(pectoralGeometry, skinMaterial);
            leftPectoral.position.set(-0.2, 0.2, 0.1);
            leftPectoral.scale.set(0.8, 0.6, 0.3);
            upperTorso.add(leftPectoral);
            
            const rightPectoral = new THREE.Mesh(pectoralGeometry, skinMaterial);
            rightPectoral.position.set(0.2, 0.2, 0.1);
            rightPectoral.scale.set(0.8, 0.6, 0.3);
            upperTorso.add(rightPectoral);

            // 添加脊柱结构
            const spineGeometry = new THREE.CylinderGeometry(0.05, 0.05, 1.2, 8);
            const spine = new THREE.Mesh(spineGeometry, skinMaterial);
            spine.position.set(0, 0.6, -0.1);
            upperTorso.add(spine);

            // 添加锁骨 - 新增重要解剖学结构
            const clavicleGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.3, 8);
            const leftClavicle = new THREE.Mesh(clavicleGeometry, skinMaterial);
            leftClavicle.position.set(-0.25, 0.6, 0);
            leftClavicle.rotation.z = Math.PI / 6;
            upperTorso.add(leftClavicle);
            
            const rightClavicle = new THREE.Mesh(clavicleGeometry, skinMaterial);
            rightClavicle.position.set(0.25, 0.6, 0);
            rightClavicle.rotation.z = -Math.PI / 6;
            upperTorso.add(rightClavicle);

            // 添加肩胛骨
            const scapulaGeometry = new THREE.BoxGeometry(0.15, 0.2, 0.05);
            const leftScapula = new THREE.Mesh(scapulaGeometry, skinMaterial);
            leftScapula.position.set(-0.3, 0.3, -0.1);
            leftScapula.rotation.z = Math.PI / 6;
            upperTorso.add(leftScapula);
            
            const rightScapula = new THREE.Mesh(scapulaGeometry, skinMaterial);
            rightScapula.position.set(0.3, 0.3, -0.1);
            rightScapula.rotation.z = -Math.PI / 6;
            upperTorso.add(rightScapula);

            // 7. 颈部 - 连接到躯干（修正层级结构）
            const neckGeometry = new THREE.CylinderGeometry(0.15, 0.18, 0.2, 12);
            const neck = new THREE.Mesh(neckGeometry, skinMaterial);
            neck.position.y = 0.8; // 在躯干上方，紧密连接
            neck.castShadow = true;
            upperTorso.add(neck); // 修正：连接到躯干而不是骨盆

            // 8. 头部 - 连接到颈部（修正层级结构）
            const headGeometry = new THREE.SphereGeometry(0.35, 24, 20); // 减小头部大小
            head = new THREE.Mesh(headGeometry, skinMaterial);
            head.position.set(0, 0.5, 0); // 在颈部上方，紧密连接
            head.scale.set(1, 1.05, 1);
            head.castShadow = true;
            neck.add(head); // 修正：连接到颈部而不是骨盆

            // 添加头发 - 使用更自然的几何体
            const hairGeometry = new THREE.SphereGeometry(0.37, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.7);
            const hairTop = new THREE.Mesh(hairGeometry, hairMaterial);
            hairTop.position.set(0, 0.15, -0.1);
            hairTop.scale.set(1, 1.1, 0.8); // 更自然的形状
            head.add(hairTop);

            // 前发尖 - 使用更自然的形状
            const frontSpikeGeometry = new THREE.ConeGeometry(0.06, 0.25, 8); // 减小尺寸
            const frontSpike1 = new THREE.Mesh(frontSpikeGeometry, hairMaterial);
            frontSpike1.position.set(-0.12, 0.35, 0.3);
            frontSpike1.rotation.x = -Math.PI / 8; // 减小角度
            frontSpike1.rotation.z = -Math.PI / 10;
            head.add(frontSpike1);

            const frontSpike2 = new THREE.Mesh(frontSpikeGeometry, hairMaterial);
            frontSpike2.position.set(0.12, 0.35, 0.3);
            frontSpike2.rotation.x = -Math.PI / 8;
            frontSpike2.rotation.z = Math.PI / 10;
            head.add(frontSpike2);

            // 侧发尖 - 使用更自然的形状
            const sideSpikeGeometry = new THREE.ConeGeometry(0.05, 0.2, 8); // 减小尺寸
            const leftSideSpike = new THREE.Mesh(sideSpikeGeometry, hairMaterial);
            leftSideSpike.position.set(-0.35, 0.2, 0.08);
            leftSideSpike.rotation.z = -Math.PI / 6; // 减小角度
            head.add(leftSideSpike);

            const rightSideSpike = new THREE.Mesh(sideSpikeGeometry, hairMaterial);
            rightSideSpike.position.set(0.35, 0.2, 0.08);
            rightSideSpike.rotation.z = Math.PI / 6;
            head.add(rightSideSpike);

            // 眼睛 - 减小尺寸
            const eyeWhiteGeometry = new THREE.SphereGeometry(0.12, 16, 12); // 从0.18减小到0.12
            const eyeWhiteMaterial = new THREE.MeshPhongMaterial({ 
                color: 0xFFFFFF,
                shininess: 100,
                specular: 0x444444
            });

            const leftEye = new THREE.Mesh(eyeWhiteGeometry, eyeWhiteMaterial);
            leftEye.position.set(-0.18, 0.05, 0.35); // 调整位置
            leftEye.scale.set(1, 1.2, 0.8);
            head.add(leftEye);

            const rightEye = new THREE.Mesh(eyeWhiteGeometry, eyeWhiteMaterial);
            rightEye.position.set(0.18, 0.05, 0.35); // 调整位置
            rightEye.scale.set(1, 1.2, 0.8);
            head.add(rightEye);

            // 瞳孔 - 相应调整
            const pupilGeometry = new THREE.SphereGeometry(0.08, 12, 8); // 从0.12减小到0.08
            const pupilMaterial = new THREE.MeshPhongMaterial({ 
                color: 0x1A1A1A,
                shininess: 100 
            });

            const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial);
            leftPupil.position.set(0, 0, 0.05);
            leftEye.add(leftPupil);

            const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial);
            rightPupil.position.set(0, 0, 0.05);
            rightEye.add(rightPupil);

            // 高光
            const highlightGeometry = new THREE.SphereGeometry(0.02, 8, 6); // 减小尺寸
            const highlightMaterial = new THREE.MeshPhongMaterial({ 
                color: 0xFFFFFF,
                shininess: 200,
                transparent: true,
                opacity: 0.9
            });

            const leftHighlight = new THREE.Mesh(highlightGeometry, highlightMaterial);
            leftHighlight.position.set(-0.01, 0.02, 0.06);
            leftPupil.add(leftHighlight);

            const rightHighlight = new THREE.Mesh(highlightGeometry, highlightMaterial);
            rightHighlight.position.set(-0.01, 0.02, 0.06);
            rightPupil.add(rightHighlight);

            // 鼻子
            const noseGeometry = new THREE.SphereGeometry(0.02, 8, 6);
            const nose = new THREE.Mesh(noseGeometry, skinMaterial);
            nose.position.set(0, -0.08, 0.42); // 调整位置
            head.add(nose);

            // 嘴巴
            const mouthGeometry = new THREE.SphereGeometry(0.04, 8, 6, 0, Math.PI);
            const mouthMaterial = new THREE.MeshPhongMaterial({ color: 0xFF6B6B });
            const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
            mouth.position.set(0, -0.22, 0.4); // 调整位置
            mouth.rotation.x = Math.PI;
            head.add(mouth);

            // 添加眉毛
            const eyebrowGeometry = new THREE.BoxGeometry(0.06, 0.02, 0.02); // 减小尺寸
            const eyebrowMaterial = new THREE.MeshPhongMaterial({ color: 0x1A1A1A });
            const leftEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial);
            leftEyebrow.position.set(-0.18, 0.12, 0.35); // 调整位置
            leftEyebrow.rotation.z = -Math.PI / 12;
            head.add(leftEyebrow);

            const rightEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial);
            rightEyebrow.position.set(0.18, 0.12, 0.35); // 调整位置
            rightEyebrow.rotation.z = Math.PI / 12;
            head.add(rightEyebrow);

            // 添加耳朵
            const earGeometry = new THREE.SphereGeometry(0.06, 12, 8, 0, Math.PI); // 减小尺寸
            const leftEar = new THREE.Mesh(earGeometry, skinMaterial);
            leftEar.position.set(-0.36, 0, 0.15); // 调整位置
            leftEar.rotation.x = Math.PI / 2;
            head.add(leftEar);

            const rightEar = new THREE.Mesh(earGeometry, skinMaterial);
            rightEar.position.set(0.36, 0, 0.15); // 调整位置
            rightEar.rotation.x = Math.PI / 2;
            head.add(rightEar);

            // 9. 手臂系统 - 连接到躯干上部（修正层级结构）
            const shoulderJointGeometry = new THREE.SphereGeometry(0.15, 12, 8);
            const leftShoulderJoint = new THREE.Mesh(shoulderJointGeometry, metalMaterial);
            leftShoulderJoint.position.set(-0.45, 0.4, 0); // 调整位置更贴近身体
            leftShoulderJoint.castShadow = true;
            upperTorso.add(leftShoulderJoint);
            
            const rightShoulderJoint = new THREE.Mesh(shoulderJointGeometry, metalMaterial);
            rightShoulderJoint.position.set(0.45, 0.4, 0); // 调整位置更贴近身体
            rightShoulderJoint.castShadow = true;
            upperTorso.add(rightShoulderJoint);

            // 左上臂 - 调整比例
            const upperArmGeometry = new THREE.CylinderGeometry(0.1, 0.12, 0.7, 12); // 调整比例
            leftArm = new THREE.Mesh(upperArmGeometry, skinMaterial);
            leftArm.position.set(0, -0.35, 0);
            leftArm.castShadow = true;
            leftShoulderJoint.add(leftArm);
            
            // 左肘关节
            const elbowJointGeometry = new THREE.SphereGeometry(0.1, 12, 8);
            const leftElbowJoint = new THREE.Mesh(elbowJointGeometry, metalMaterial);
            leftElbowJoint.position.set(0, -0.45, 0);
            leftArm.add(leftElbowJoint);
            
            // 左前臂
            const forearmGeometry = new THREE.CylinderGeometry(0.08, 0.1, 0.7, 12);
            const leftForearm = new THREE.Mesh(forearmGeometry, skinMaterial);
            leftForearm.position.set(0, -0.45, 0);
            leftForearm.castShadow = true;
            leftElbowJoint.add(leftForearm);
            
            // 左手腕关节
            const wristJointGeometry = new THREE.SphereGeometry(0.08, 12, 8);
            const leftWristJoint = new THREE.Mesh(wristJointGeometry, metalMaterial);
            leftWristJoint.position.set(0, -0.4, 0);
            leftForearm.add(leftWristJoint);
            
            // 左手
            const handGeometry = new THREE.SphereGeometry(0.1, 12, 8);
            const leftHand = new THREE.Mesh(handGeometry, skinMaterial);
            leftHand.position.set(0, -0.2, 0);
            leftHand.scale.set(1, 1.2, 0.8);
            //leftWristJoint.add(leftHand);

            // 添加左手手指 - 修正位置和角度
            const fingerGeometry = new THREE.CylinderGeometry(0.015, 0.02, 0.15, 8);
            const fingerMaterial = new THREE.MeshPhongMaterial({ color: 0xFFE4B5, shininess: 20 });
            
            // 拇指 - 修正位置和角度
            const leftThumb = new THREE.Mesh(fingerGeometry, fingerMaterial);
            leftThumb.position.set(-0.12, -0.2, 0.02); // 调整位置
            leftThumb.rotation.z = Math.PI / 3; // 调整角度
            leftHand.add(leftThumb);
            
            // 食指
            const leftIndex = new THREE.Mesh(fingerGeometry, fingerMaterial);
            leftIndex.position.set(0.05, -0.25, 0.08);
            leftIndex.rotation.z = -Math.PI / 8; // 调整角度
            leftHand.add(leftIndex);
            
            // 中指
            const leftMiddle = new THREE.Mesh(fingerGeometry, fingerMaterial);
            leftMiddle.position.set(0, -0.27, 0.1);
            leftHand.add(leftMiddle);
            
            // 无名指
            const leftRing = new THREE.Mesh(fingerGeometry, fingerMaterial);
            leftRing.position.set(-0.05, -0.25, 0.08);
            leftRing.rotation.z = Math.PI / 8; // 调整角度
            leftHand.add(leftRing);
            
            // 小指
            const leftPinky = new THREE.Mesh(fingerGeometry, fingerMaterial);
            leftPinky.position.set(-0.1, -0.22, 0.06);
            leftPinky.rotation.z = Math.PI / 4; // 调整角度
            leftHand.add(leftPinky);

            // 右上臂 - 调整比例
            rightArm = new THREE.Mesh(upperArmGeometry, skinMaterial);
            rightArm.position.set(0, -0.35, 0);
            rightArm.castShadow = true;
            rightShoulderJoint.add(rightArm);
            
            // 右肘关节
            const rightElbowJoint = new THREE.Mesh(elbowJointGeometry, metalMaterial);
            rightElbowJoint.position.set(0, -0.45, 0);
            rightArm.add(rightElbowJoint);
            
            // 右前臂
            const rightForearm = new THREE.Mesh(forearmGeometry, skinMaterial);
            rightForearm.position.set(0, -0.45, 0);
            rightForearm.castShadow = true;
            rightElbowJoint.add(rightForearm);
            
            // 右手腕关节
            const rightWristJoint = new THREE.Mesh(wristJointGeometry, metalMaterial);
            rightWristJoint.position.set(0, -0.4, 0);
            rightForearm.add(rightWristJoint);
            
            // 右手
            const rightHand = new THREE.Mesh(handGeometry, skinMaterial);
            rightHand.position.set(0, -0.2, 0);
            rightHand.scale.set(1, 1.2, 0.8);
            //rightWristJoint.add(rightHand);

            // 添加右手手指 - 修正位置和角度
            // 拇指
            const rightThumb = new THREE.Mesh(fingerGeometry, fingerMaterial);
            rightThumb.position.set(0.12, -0.2, 0.02); // 调整位置
            rightThumb.rotation.z = -Math.PI / 3; // 调整角度
            rightHand.add(rightThumb);
            
            // 食指
            const rightIndex = new THREE.Mesh(fingerGeometry, fingerMaterial);
            rightIndex.position.set(-0.05, -0.25, 0.08);
            rightIndex.rotation.z = Math.PI / 8; // 调整角度
            rightHand.add(rightIndex);
            
            // 中指
            const rightMiddle = new THREE.Mesh(fingerGeometry, fingerMaterial);
            rightMiddle.position.set(0, -0.27, 0.1);
            rightHand.add(rightMiddle);
            
            // 无名指
            const rightRing = new THREE.Mesh(fingerGeometry, fingerMaterial);
            rightRing.position.set(0.05, -0.25, 0.08);
            rightRing.rotation.z = -Math.PI / 8; // 调整角度
            rightHand.add(rightRing);
            
            // 小指
            const rightPinky = new THREE.Mesh(fingerGeometry, fingerMaterial);
            rightPinky.position.set(0.1, -0.22, 0.06);
            rightPinky.rotation.z = -Math.PI / 4; // 调整角度
            rightHand.add(rightPinky);
        }
        
        function setupEventListeners() {
            // 头部控制滑块
            const headYaw = document.getElementById('headYaw');
            const headPitch = document.getElementById('headPitch');
            const headRoll = document.getElementById('headRoll');
            
            headYaw.addEventListener('input', function() {
                const angle = parseFloat(this.value) * Math.PI / 180;
                head.rotation.y = angle;
                document.getElementById('yawValue').textContent = this.value + '°';
            });
            
            headPitch.addEventListener('input', function() {
                const angle = parseFloat(this.value) * Math.PI / 180;
                head.rotation.x = angle;
                document.getElementById('pitchValue').textContent = this.value + '°';
            });
            
            headRoll.addEventListener('input', function() {
                const angle = parseFloat(this.value) * Math.PI / 180;
                head.rotation.z = angle;
                document.getElementById('rollValue').textContent = this.value + '°';
            });
            
            // 节拍同步开关
             document.getElementById('enableBeatSync').addEventListener('change', function() {
                 beatSyncEnabled = this.checked;
                 if (!beatSyncEnabled) {
                     // 禁用节拍同步时重置手臂位置
                     if (leftArm) {
                         leftArm.rotation.set(Math.PI / 12, 0, 0);
                     }
                     if (rightArm) {
                         rightArm.rotation.set(-Math.PI / 12, 0, 0);
                     }
                     armAnimation.isAnimating = false;
                 }
             });
            
            // 鼠标控制相机
            renderer.domElement.addEventListener('mousedown', onMouseDown);
            renderer.domElement.addEventListener('mousemove', onMouseMove);
            renderer.domElement.addEventListener('mouseup', onMouseUp);
            renderer.domElement.addEventListener('wheel', onMouseWheel);
            
            // 触摸控制
            renderer.domElement.addEventListener('touchstart', onTouchStart);
            renderer.domElement.addEventListener('touchmove', onTouchMove);
            renderer.domElement.addEventListener('touchend', onTouchEnd);
            
            // 窗口大小调整
            window.addEventListener('resize', onWindowResize);
            
            // 舞蹈模式开关
            const danceModeCheckbox = document.getElementById('enableDanceMode');
            if (danceModeCheckbox) {
                danceModeCheckbox.addEventListener('change', function() {
                    danceModeEnabled = this.checked;
                    if (!danceModeEnabled) {
                        stopDanceMode();
                    }
                });
            }
            
            // FBX模型显示开关
            const fbxModelCheckbox = document.getElementById('showFBXModel');
            if (fbxModelCheckbox) {
                fbxModelCheckbox.addEventListener('change', function() {
                    if (fbxModel) {
                        fbxModel.visible = this.checked;
                    }
                    // 切换自定义角色的可见性
                    if (bodyGroup) {
                        bodyGroup.visible = !this.checked;
                    }
                });
            }
        }
        
        function onMouseDown(event) {
            isMouseDown = true;
            mouseX = event.clientX;
            mouseY = event.clientY;
        }
        
        function onMouseMove(event) {
            if (isMouseDown) {
                const deltaX = event.clientX - mouseX;
                const deltaY = event.clientY - mouseY;
                
                cameraAngleY += deltaX * 0.01;
                cameraAngleX += deltaY * 0.01;
                
                cameraAngleX = Math.max(-Math.PI/2, Math.min(Math.PI/2, cameraAngleX));
                
                updateCameraPosition();
                
                mouseX = event.clientX;
                mouseY = event.clientY;
            }
        }
        
        function onMouseUp(event) {
            isMouseDown = false;
        }
        
        function onMouseWheel(event) {
            const distance = camera.position.distanceTo(new THREE.Vector3(0, 3, 0));
            const newDistance = Math.max(5, Math.min(20, distance + event.deltaY * 0.01));
            
            const direction = new THREE.Vector3();
            direction.subVectors(camera.position, new THREE.Vector3(0, 3, 0)).normalize();
            camera.position.copy(new THREE.Vector3(0, 3, 0).add(direction.multiplyScalar(newDistance)));
        }
        
        function onTouchStart(event) {
            if (event.touches.length === 1) {
                isMouseDown = true;
                mouseX = event.touches[0].clientX;
                mouseY = event.touches[0].clientY;
            }
        }
        
        function onTouchMove(event) {
            if (event.touches.length === 1 && isMouseDown) {
                const deltaX = event.touches[0].clientX - mouseX;
                const deltaY = event.touches[0].clientY - mouseY;
                
                cameraAngleY += deltaX * 0.01;
                cameraAngleX += deltaY * 0.01;
                
                cameraAngleX = Math.max(-Math.PI/2, Math.min(Math.PI/2, cameraAngleX));
                
                updateCameraPosition();
                
                mouseX = event.touches[0].clientX;
                mouseY = event.touches[0].clientY;
            }
        }
        
        function onTouchEnd(event) {
            isMouseDown = false;
        }
        
        function updateCameraPosition() {
            const distance = camera.position.distanceTo(new THREE.Vector3(0, 3, 0));
            
            camera.position.x = distance * Math.sin(cameraAngleY) * Math.cos(cameraAngleX);
            camera.position.y = 3 + distance * Math.sin(cameraAngleX);
            camera.position.z = distance * Math.cos(cameraAngleY) * Math.cos(cameraAngleX);
            
            camera.lookAt(0, 3, 0);
        }
        
        function resetHead() {
             head.rotation.set(0, 0, 0);
             document.getElementById('headYaw').value = 0;
             document.getElementById('headPitch').value = 0;
             document.getElementById('headRoll').value = 0;
             document.getElementById('yawValue').textContent = '0°';
             document.getElementById('pitchValue').textContent = '0°';
             document.getElementById('rollValue').textContent = '0°';
             
             // 重置手臂位置
             if (leftArm) {
                 leftArm.rotation.set(Math.PI / 12, 0, 0);
             }
             if (rightArm) {
                 rightArm.rotation.set(-Math.PI / 12, 0, 0);
             }
             
             // 停止所有动画
             beatAnimation.isAnimating = false;
             armAnimation.isAnimating = false;
         }
        
        function randomMove() {
            const randomYaw = (Math.random() - 0.5) * 120;
            const randomPitch = (Math.random() - 0.5) * 90;
            const randomRoll = (Math.random() - 0.5) * 60;
            
            document.getElementById('headYaw').value = randomYaw;
            document.getElementById('headPitch').value = randomPitch;
            document.getElementById('headRoll').value = randomRoll;
            
            head.rotation.y = randomYaw * Math.PI / 180;
            head.rotation.x = randomPitch * Math.PI / 180;
            head.rotation.z = randomRoll * Math.PI / 180;
            
            document.getElementById('yawValue').textContent = Math.round(randomYaw) + '°';
            document.getElementById('pitchValue').textContent = Math.round(randomPitch) + '°';
            document.getElementById('rollValue').textContent = Math.round(randomRoll) + '°';
        }
        
        // 重置FBX模型位置
        function resetFBXModel() {
            if (fbxModel) {
                fbxModel.position.set(0, 1, 0);
                fbxModel.rotation.set(0, Math.PI, 0);
                fbxModel.scale.set(0.02, 0.02, 0.02);
            }
        }
        
        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }
        
        function animate() {
             requestAnimationFrame(animate);
             
             // 更新节拍动画
             updateBeatAnimation();
             updateArmAnimation();
             
             // 更新舞蹈动画
             updateDanceAnimation();
             
             // 时间变量
             const time = Date.now() * 0.001;
             
             // 动态舞台灯光效果
             if (typeof spotLight1 !== 'undefined') {
                 // 主聚光灯轻微摆动
                 spotLight1.position.x = 5 + Math.sin(time * 0.3) * 2;
                 spotLight1.position.z = 8 + Math.cos(time * 0.4) * 1.5;
                 
                 // 侧光颜色变化
                 const hue = (time * 0.1) % 1;
                 spotLight2.color.setHSL(hue * 0.3 + 0.8, 0.5, 0.6);
             }
             
             // 整体动画协调 - 新增功能
             updateBodyAnimation(time);
             
             // 更自然的身体摆动 - 模拟呼吸
             if (typeof body !== 'undefined') {
                 body.rotation.z = Math.sin(time * 0.8) * 0.02;
             }
             
             // 胸部轻微的呼吸动作
             if (typeof upperTorso !== 'undefined') {
                 upperTorso.rotation.x = Math.sin(time * 1.5) * 0.01;
             }
             
             // 头部轻微的生动摆动（当没有手动控制时）
             if (!beatAnimation.isAnimating && document.getElementById('headYaw').value == 0) {
                 head.rotation.y += Math.sin(time * 0.6) * 0.001;
                 head.rotation.x += Math.cos(time * 0.7) * 0.0005;
             }
             
             // 只有在没有节拍同步、手臂动画未激活且不在舞蹈模式时才应用默认手臂动画
             if ((!beatSyncEnabled || !armAnimation.isAnimating) && !isDanceMode) {
                 // 更自然的手臂摆动
                 leftArm.rotation.x = Math.sin(time * 0.7) * 0.08;
                 rightArm.rotation.x = Math.sin(time * 0.7 + Math.PI) * 0.08;
                 leftArm.rotation.y = Math.cos(time * 0.5) * 0.03;
                 rightArm.rotation.y = Math.cos(time * 0.5 + Math.PI) * 0.03;
             }
             
             // 头发的轻微摆动
             if (head.children && head.children.length > 2) {
                 const leftSideHair = head.children[1];
                 const rightSideHair = head.children[2];
                 if (leftSideHair) {
                     leftSideHair.rotation.z = Math.sin(time * 1.2) * 0.03;
                 }
                 if (rightSideHair) {
                     rightSideHair.rotation.z = Math.sin(time * 1.2 + Math.PI) * 0.03;
                 }
             }
             
             // 衣服的微妙摆动
             if (typeof waist !== 'undefined') {
                 waist.rotation.z = Math.sin(time * 0.9) * 0.015;
             }
             
             // 舞蹈模式下的特殊效果
             if (isDanceMode && danceData) {
                 // 增强舞台灯光效果
                 if (typeof spotLight1 !== 'undefined') {
                     spotLight1.intensity = 1.5 + Math.sin(time * 2) * 0.3;
                     spotLight2.intensity = 0.8 + Math.cos(time * 1.8) * 0.2;
                 }
                 
                 // 身体摆动配合舞蹈
                 if (typeof upperTorso !== 'undefined') {
                     upperTorso.rotation.z = Math.sin(time * 1.5) * 0.05;
                     upperTorso.rotation.x = Math.sin(time * 2.0) * 0.03;
                 }
                 
                 // 腰部摆动
                 if (typeof waist !== 'undefined') {
                     waist.rotation.z = Math.sin(time * 1.8) * 0.04;
                 }
                 
                 // 身体组整体摆动
                 if (bodyGroup) {
                     bodyGroup.rotation.y = Math.sin(time * 0.8) * 0.02;
                 }
             }
             
             // FBX模型动画
             if (fbxModel && fbxModel.visible) {
                 // 轻微的旋转动画
                 fbxModel.rotation.y = Math.sin(time * 0.5) * 0.1;
                 
                 // 轻微的上下摆动
                 fbxModel.position.y = Math.sin(time * 0.8) * 0.05;
             }
             
             // 安全渲染，防止WebGL错误
             try {
                 renderer.render(scene, camera);
             } catch (error) {
                 console.warn('渲染错误，跳过此帧:', error);
             }
         }

         // 整体动画协调函数
         function updateBodyAnimation(time) {
             // 身体整体轻微摆动
             if (bodyGroup) {
                 bodyGroup.rotation.y = Math.sin(time * 0.5) * 0.01;
             }
             
             // 协调的手臂摆动（当没有其他动画时）
             if (leftArm && rightArm && !armAnimation.isAnimating && !isDanceMode) {
                 // 更自然的手臂摆动
                 leftArm.rotation.x = Math.sin(time * 0.7) * 0.05;
                 rightArm.rotation.x = Math.sin(time * 0.7 + Math.PI) * 0.05;
                 
                 // 添加轻微的前后摆动
                 leftArm.rotation.y = Math.cos(time * 0.5) * 0.02;
                 rightArm.rotation.y = Math.cos(time * 0.5 + Math.PI) * 0.02;
             }
             
             // 腿部轻微摆动
             if (leftThigh && rightThigh) {
                 leftThigh.rotation.x = Math.sin(time * 0.6) * 0.01;
                 rightThigh.rotation.x = Math.sin(time * 0.6 + Math.PI) * 0.01;
             }
             
             // 头部轻微摆动（当没有手动控制时）
             if (head && !beatAnimation.isAnimating && document.getElementById('headYaw').value == 0) {
                 head.rotation.y += Math.sin(time * 0.4) * 0.0008;
                 head.rotation.x += Math.cos(time * 0.5) * 0.0003;
             }
             
             // 呼吸效果
             if (upperTorso) {
                 const breathScale = 1 + Math.sin(time * 1.2) * 0.005;
                 upperTorso.scale.y = breathScale;
             }
         }

         return {
            init,
            initAudio,
            togglePlayPause,
            stopAudio,
            updateTimeDisplay,
            resetFBXModel,
         }
}