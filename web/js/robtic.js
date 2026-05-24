// Rob-Dancing: Astro Boy robot with keyframe-driven pose animation
function robtic() {
    const DEG = Math.PI / 180;

    // Scene objects
    let scene, camera, renderer;
    let head, body, upperTorso, waist;
    let spotLight1, spotLight2;

    // Articulated joint pivot groups
    let leftShoulderPivot, rightShoulderPivot;
    let leftElbowPivot,    rightElbowPivot;
    let leftHipPivot,      rightHipPivot;
    let leftKneePivot,     rightKneePivot;
    let leftAnklePivot,    rightAnklePivot;

    // Camera drag state
    let mouseX = 0, mouseY = 0;
    let isMouseDown = false;
    let cameraAngleX = 0, cameraAngleY = 0;

    // Audio
    let audioPlayer;
    let beatSyncEnabled = true;
    let currentBeatIndex = 0;

    // Dance data loaded from JSON
    let danceData = null;
    let lastAppliedPoseTime = -1;

    // -------------------------------------------------------------------------
    // Init
    // -------------------------------------------------------------------------
    function init() {
        scene = new THREE.Scene();

        const bgCanvas = document.createElement('canvas');
        bgCanvas.width = 512; bgCanvas.height = 512;
        const ctx = bgCanvas.getContext('2d');
        const grad = ctx.createLinearGradient(0, 0, 0, 512);
        grad.addColorStop(0,   '#2C1810');
        grad.addColorStop(0.5, '#4A2C47');
        grad.addColorStop(1,   '#1A1A2E');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 512, 512);
        scene.background = new THREE.CanvasTexture(bgCanvas);

        camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 3, 10);
        camera.lookAt(0, 3, 0);

        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        document.getElementById('container').appendChild(renderer.domElement);

        scene.add(new THREE.AmbientLight(0x4A4A6A, 0.3));

        spotLight1 = new THREE.SpotLight(0xFFFFFF, 1.5, 30, Math.PI / 4, 0.3, 1);
        spotLight1.position.set(5, 12, 8);
        spotLight1.target.position.set(0, 3, 0);
        spotLight1.castShadow = true;
        spotLight1.shadow.mapSize.width  = 2048;
        spotLight1.shadow.mapSize.height = 2048;
        scene.add(spotLight1);
        scene.add(spotLight1.target);

        spotLight2 = new THREE.SpotLight(0xFF9999, 0.8, 25, Math.PI / 3, 0.5, 1);
        spotLight2.position.set(-8, 8, 5);
        spotLight2.target.position.set(0, 3, 0);
        spotLight2.castShadow = true;
        scene.add(spotLight2);
        scene.add(spotLight2.target);

        const rimLight = new THREE.DirectionalLight(0x9999FF, 0.6);
        rimLight.position.set(-5, 5, -8);
        scene.add(rimLight);

        const ptLight = new THREE.PointLight(0xFFAA77, 0.4, 15);
        ptLight.position.set(3, 6, -3);
        scene.add(ptLight);

        createCharacter();
        createStage();
        initAudio();
        setupEventListeners();
        loadDanceData();
        animate();
    }

    // -------------------------------------------------------------------------
    // Stage
    // -------------------------------------------------------------------------
    function createStage() {
        const sc2 = document.createElement('canvas');
        sc2.width = 512; sc2.height = 512;
        const sc = sc2.getContext('2d');
        sc.fillStyle = '#8B4513';
        sc.fillRect(0, 0, 512, 512);
        for (let i = 0; i < 20; i++) {
            const y = i * 25.6;
            sc.fillStyle = i % 2 === 0 ? '#A0522D' : '#8B4513';
            sc.fillRect(0, y, 512, 25.6);
            sc.strokeStyle = '#654321'; sc.lineWidth = 1;
            sc.beginPath(); sc.moveTo(0, y + 12.8); sc.lineTo(512, y + 12.8); sc.stroke();
        }
        const stageTex = new THREE.CanvasTexture(sc2);
        stageTex.wrapS = stageTex.wrapT = THREE.RepeatWrapping;
        stageTex.repeat.set(2, 2);

        const stage = new THREE.Mesh(
            new THREE.PlaneGeometry(40, 40),
            new THREE.MeshPhongMaterial({ map: stageTex, shininess: 80, specular: 0x333333 })
        );
        stage.rotation.x = -Math.PI / 2;
        stage.receiveShadow = true;
        stage.position.y = -0.5;
        scene.add(stage);

        const border = new THREE.Mesh(
            new THREE.BoxGeometry(42, 0.3, 42),
            new THREE.MeshPhongMaterial({ color: 0x2C1810, shininess: 60 })
        );
        border.position.y = -0.65;
        border.receiveShadow = true;
        scene.add(border);
    }

    // -------------------------------------------------------------------------
    // Character: Astro Boy with articulated pivot hierarchies
    // -------------------------------------------------------------------------
    function createCharacter() {
        const skinMat  = new THREE.MeshPhongMaterial({ color: 0xFFE4B5, shininess: 40, specular: 0x222222 });
        const metalMat = new THREE.MeshPhongMaterial({ color: 0xC0C0C0, shininess: 100, specular: 0x888888 });
        const hairMat  = new THREE.MeshPhongMaterial({ color: 0x1A1A1A, shininess: 80 });
        const redMat   = new THREE.MeshPhongMaterial({ color: 0xDC143C, shininess: 30 });
        const blueMat  = new THREE.MeshPhongMaterial({ color: 0x0047AB, shininess: 25 });
        const blackMat = new THREE.MeshPhongMaterial({ color: 0x2F2F2F, shininess: 50 });

        // Torso
        upperTorso = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.45, 1.2, 16), redMat);
        upperTorso.position.y = 3.0;
        upperTorso.castShadow = true;
        scene.add(upperTorso);

        const chestCore = new THREE.Mesh(
            new THREE.CylinderGeometry(0.15, 0.15, 0.06, 16),
            new THREE.MeshPhongMaterial({ color: 0x4169E1, shininess: 100, emissive: 0x001122, transparent: true, opacity: 0.8 })
        );
        chestCore.position.set(0, 0.2, 0.42);
        chestCore.rotation.x = Math.PI / 2;
        upperTorso.add(chestCore);
        chestCore.add(new THREE.Mesh(
            new THREE.CylinderGeometry(0.08, 0.08, 0.08, 12),
            new THREE.MeshPhongMaterial({ color: 0x87CEEB, shininess: 150, emissive: 0x002244 })
        ));

        waist = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.4, 0.3, 16), skinMat);
        waist.position.y = 2.2;
        waist.castShadow = true;
        scene.add(waist);

        body = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.42, 0.6, 16), blueMat);
        body.position.y = 1.7;
        body.castShadow = true;
        scene.add(body);

        // Head
        head = new THREE.Mesh(new THREE.SphereGeometry(0.55, 24, 20), skinMat);
        head.position.set(0, 4.2, 0);
        head.scale.set(1, 1.05, 1);
        head.castShadow = true;
        scene.add(head);

        const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.18, 0.25, 12), skinMat);
        neck.position.y = 3.7;
        neck.castShadow = true;
        scene.add(neck);

        // Hair
        const hairTop = new THREE.Mesh(
            new THREE.SphereGeometry(0.52, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.7), hairMat
        );
        hairTop.position.set(0, 0.15, -0.1);
        hairTop.scale.set(1, 1.2, 0.9);
        head.add(hairTop);

        const spikeGeo = new THREE.ConeGeometry(0.08, 0.3, 8);
        const sp1 = new THREE.Mesh(spikeGeo, hairMat);
        sp1.position.set(-0.15, 0.4, 0.35); sp1.rotation.set(-Math.PI/6, 0, -Math.PI/8);
        head.add(sp1);
        const sp2 = new THREE.Mesh(spikeGeo, hairMat);
        sp2.position.set(0.15, 0.4, 0.35); sp2.rotation.set(-Math.PI/6, 0, Math.PI/8);
        head.add(sp2);

        const sideGeo = new THREE.ConeGeometry(0.06, 0.25, 8);
        const lsh = new THREE.Mesh(sideGeo, hairMat);
        lsh.position.set(-0.4, 0.25, 0.1); lsh.rotation.z = -Math.PI/4;
        head.add(lsh);
        const rsh = new THREE.Mesh(sideGeo, hairMat);
        rsh.position.set(0.4, 0.25, 0.1); rsh.rotation.z = Math.PI/4;
        head.add(rsh);

        // Eyes
        const eyeWMat = new THREE.MeshPhongMaterial({ color: 0xFFFFFF, shininess: 100, specular: 0x444444 });
        const pupMat  = new THREE.MeshPhongMaterial({ color: 0x1A1A1A, shininess: 100 });
        const hlMat   = new THREE.MeshPhongMaterial({ color: 0xFFFFFF, shininess: 200, transparent: true, opacity: 0.9 });
        function makeEye(x) {
            const e = new THREE.Mesh(new THREE.SphereGeometry(0.18, 16, 12), eyeWMat);
            e.position.set(x, 0.05, 0.45); e.scale.set(1, 1.2, 0.8); head.add(e);
            const p = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 8), pupMat);
            p.position.set(0, 0, 0.05); e.add(p);
            const h = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6), hlMat);
            h.position.set(-0.02, 0.03, 0.08); p.add(h);
        }
        makeEye(-0.22); makeEye(0.22);

        const nose = new THREE.Mesh(new THREE.SphereGeometry(0.02, 8, 6), skinMat);
        nose.position.set(0, -0.08, 0.52); head.add(nose);
        const mouth = new THREE.Mesh(
            new THREE.SphereGeometry(0.04, 8, 6, 0, Math.PI),
            new THREE.MeshPhongMaterial({ color: 0xFF6B6B })
        );
        mouth.position.set(0, -0.22, 0.5); mouth.rotation.x = Math.PI; head.add(mouth);

        // Shoulder joint decorations (static, visual only)
        const sJGeo = new THREE.SphereGeometry(0.15, 12, 8);
        const lsj = new THREE.Mesh(sJGeo, metalMat); lsj.position.set(-0.55, 3.6, 0); scene.add(lsj);
        const rsj = new THREE.Mesh(sJGeo, metalMat); rsj.position.set( 0.55, 3.6, 0); scene.add(rsj);

        // Left arm pivot hierarchy
        leftShoulderPivot = new THREE.Group();
        leftShoulderPivot.position.set(-0.6, 3.6, 0);
        scene.add(leftShoulderPivot);
        const luArm = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.12, 1.0, 12), skinMat);
        luArm.position.set(0, -0.5, 0); luArm.castShadow = true;
        leftShoulderPivot.add(luArm);
        const leJoint = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 8), metalMat);
        leJoint.position.set(0, -1.0, 0);
        leftShoulderPivot.add(leJoint);
        leftElbowPivot = new THREE.Group();
        leftElbowPivot.position.set(0, -1.0, 0);
        leftShoulderPivot.add(leftElbowPivot);
        const lForearm = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 0.8, 12), skinMat);
        lForearm.position.set(0, -0.4, 0); lForearm.castShadow = true;
        leftElbowPivot.add(lForearm);
        const lHand = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 8), skinMat);
        lHand.position.set(0, -0.85, 0); lHand.scale.set(1, 1.2, 0.8);
        leftElbowPivot.add(lHand);

        // Right arm pivot hierarchy
        rightShoulderPivot = new THREE.Group();
        rightShoulderPivot.position.set(0.6, 3.6, 0);
        scene.add(rightShoulderPivot);
        const ruArm = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.12, 1.0, 12), skinMat);
        ruArm.position.set(0, -0.5, 0); ruArm.castShadow = true;
        rightShoulderPivot.add(ruArm);
        const reJoint = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 8), metalMat);
        reJoint.position.set(0, -1.0, 0);
        rightShoulderPivot.add(reJoint);
        rightElbowPivot = new THREE.Group();
        rightElbowPivot.position.set(0, -1.0, 0);
        rightShoulderPivot.add(rightElbowPivot);
        const rForearm = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 0.8, 12), skinMat);
        rForearm.position.set(0, -0.4, 0); rForearm.castShadow = true;
        rightElbowPivot.add(rForearm);
        const rHand = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 8), skinMat);
        rHand.position.set(0, -0.85, 0); rHand.scale.set(1, 1.2, 0.8);
        rightElbowPivot.add(rHand);

        // Left leg pivot hierarchy
        leftHipPivot = new THREE.Group();
        leftHipPivot.position.set(-0.25, 1.4, 0);
        scene.add(leftHipPivot);
        const lThigh = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.18, 1.2, 12), skinMat);
        lThigh.position.set(0, -0.6, 0); lThigh.castShadow = true;
        leftHipPivot.add(lThigh);
        const lkJoint = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 8), metalMat);
        lkJoint.position.set(0, -1.2, 0);
        leftHipPivot.add(lkJoint);
        leftKneePivot = new THREE.Group();
        leftKneePivot.position.set(0, -1.2, 0);
        leftHipPivot.add(leftKneePivot);
        const lCalf = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.15, 1.0, 12), skinMat);
        lCalf.position.set(0, -0.5, 0); lCalf.castShadow = true;
        leftKneePivot.add(lCalf);
        const laJoint = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 8), metalMat);
        laJoint.position.set(0, -1.0, 0);
        leftKneePivot.add(laJoint);
        leftAnklePivot = new THREE.Group();
        leftAnklePivot.position.set(0, -1.0, 0);
        leftKneePivot.add(leftAnklePivot);
        const lBoot = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.4, 0.7), redMat);
        lBoot.position.set(0, -0.2, 0.1); lBoot.castShadow = true;
        leftAnklePivot.add(lBoot);
        const lSole = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.1, 0.75), blackMat);
        lSole.position.set(0, -0.45, 0.1);
        leftAnklePivot.add(lSole);

        // Right leg pivot hierarchy
        rightHipPivot = new THREE.Group();
        rightHipPivot.position.set(0.25, 1.4, 0);
        scene.add(rightHipPivot);
        const rThigh = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.18, 1.2, 12), skinMat);
        rThigh.position.set(0, -0.6, 0); rThigh.castShadow = true;
        rightHipPivot.add(rThigh);
        const rkJoint = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 8), metalMat);
        rkJoint.position.set(0, -1.2, 0);
        rightHipPivot.add(rkJoint);
        rightKneePivot = new THREE.Group();
        rightKneePivot.position.set(0, -1.2, 0);
        rightHipPivot.add(rightKneePivot);
        const rCalf = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.15, 1.0, 12), skinMat);
        rCalf.position.set(0, -0.5, 0); rCalf.castShadow = true;
        rightKneePivot.add(rCalf);
        const raJoint = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 8), metalMat);
        raJoint.position.set(0, -1.0, 0);
        rightKneePivot.add(raJoint);
        rightAnklePivot = new THREE.Group();
        rightAnklePivot.position.set(0, -1.0, 0);
        rightKneePivot.add(rightAnklePivot);
        const rBoot = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.4, 0.7), redMat);
        rBoot.position.set(0, -0.2, 0.1); rBoot.castShadow = true;
        rightAnklePivot.add(rBoot);
        const rSole = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.1, 0.75), blackMat);
        rSole.position.set(0, -0.45, 0.1);
        rightAnklePivot.add(rSole);
    }

    // -------------------------------------------------------------------------
    // Dance data
    // -------------------------------------------------------------------------
    function loadDanceData() {
        fetch('data/dance.json')
            .then(r => r.json())
            .then(data => {
                danceData = data;
                console.log(
                    '[dance] Loaded: ' + data.keyframes.length + ' keyframes, ' +
                    'tempo=' + data.tempo.toFixed(1) + ' BPM, ' +
                    'duration=' + data.duration.toFixed(1) + 's'
                );
            })
            .catch(() => {
                console.warn('[dance] dance.json not found; run make dance AUDIO=... first.');
            });
    }

    // -------------------------------------------------------------------------
    // Pose helpers
    // -------------------------------------------------------------------------
    function easeInOut(t) {
        t = Math.max(0, Math.min(1, t));
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }

    function lerpPose(a, b, t) {
        const e = easeInOut(t);
        const keys = ['head_yaw','head_pitch','shoulder_left','shoulder_right',
                      'elbow_left','elbow_right','hip_left','hip_right',
                      'knee_left','knee_right','ankle_left','ankle_right'];
        const r = {};
        for (const k of keys) r[k] = a[k] + (b[k] - a[k]) * e;
        return r;
    }

    function getCurrentPose(time) {
        if (!danceData || !danceData.keyframes || danceData.keyframes.length === 0) return null;
        const kfs = danceData.keyframes;
        if (time >= kfs[kfs.length - 1].time) return kfs[kfs.length - 1].pose;
        if (time <= kfs[0].time)              return kfs[0].pose;

        let lo = 0, hi = kfs.length - 1;
        while (hi - lo > 1) {
            const mid = (lo + hi) >> 1;
            if (kfs[mid].time <= time) lo = mid; else hi = mid;
        }
        const kfA = kfs[lo], kfB = kfs[hi];
        const transition = kfB.transition || 0.3;
        const t = (time - kfA.time) / transition;
        return lerpPose(kfA.pose, kfB.pose, t);
    }

    function applyPose(pose) {
        if (!pose) return;
        head.rotation.y = pose.head_yaw   * DEG;
        head.rotation.x = -pose.head_pitch * DEG;

        leftShoulderPivot.rotation.x  = -pose.shoulder_left  * DEG;
        rightShoulderPivot.rotation.x = -pose.shoulder_right * DEG;
        leftElbowPivot.rotation.x     =  pose.elbow_left     * DEG;
        rightElbowPivot.rotation.x    =  pose.elbow_right    * DEG;

        leftHipPivot.rotation.x  = -pose.hip_left  * DEG;
        rightHipPivot.rotation.x = -pose.hip_right * DEG;
        leftKneePivot.rotation.x  =  pose.knee_left  * DEG;
        rightKneePivot.rotation.x =  pose.knee_right * DEG;
        leftAnklePivot.rotation.x  =  pose.ankle_left  * DEG;
        rightAnklePivot.rotation.x =  pose.ankle_right * DEG;

        const hipDiff = pose.hip_left - pose.hip_right;
        body.rotation.z      = -hipDiff * 0.003;
        upperTorso.rotation.z = -hipDiff * 0.002;
    }

    function updatePoseAnimation() {
        if (!audioPlayer || audioPlayer.paused) return;
        const t = audioPlayer.currentTime;
        if (Math.abs(t - lastAppliedPoseTime) < 0.001) return;
        lastAppliedPoseTime = t;
        const pose = getCurrentPose(t);
        if (pose) applyPose(pose);
    }

    // -------------------------------------------------------------------------
    // Audio
    // -------------------------------------------------------------------------
    function initAudio() {
        audioPlayer = document.getElementById('audioPlayer');
        audioPlayer.addEventListener('loadedmetadata', updateTimeDisplay);
        audioPlayer.addEventListener('timeupdate', function() {
            updateTimeDisplay();
            updateProgress();
            checkBeatIndicator();
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
        } else {
            audioPlayer.pause();
            btn.textContent = '播放';
            btn.classList.remove('playing');
        }
    }

    function stopAudio() {
        audioPlayer.pause();
        audioPlayer.currentTime = 0;
        document.getElementById('playPauseBtn').textContent = '播放';
        document.getElementById('playPauseBtn').classList.remove('playing');
        currentBeatIndex = 0;
        lastAppliedPoseTime = -1;
        applyPose({
            head_yaw:0, head_pitch:0,
            shoulder_left:0, shoulder_right:0,
            elbow_left:0, elbow_right:0,
            hip_left:0, hip_right:0,
            knee_left:0, knee_right:0,
            ankle_left:0, ankle_right:0,
        });
    }

    function updateTimeDisplay() {
        const cur = formatTime(audioPlayer.currentTime);
        const dur = formatTime(audioPlayer.duration);
        document.getElementById('timeDisplay').textContent = cur + ' / ' + dur;
    }

    function updateProgress() {
        if (audioPlayer.duration) {
            const pct = (audioPlayer.currentTime / audioPlayer.duration) * 100;
            document.getElementById('progress').style.width = pct + '%';
        }
    }

    function formatTime(s) {
        if (isNaN(s)) return '00:00';
        const m = Math.floor(s / 60);
        return String(m).padStart(2, '0') + ':' + String(Math.floor(s % 60)).padStart(2, '0');
    }

    function checkBeatIndicator() {
        if (!beatSyncEnabled || !danceData || !danceData.keyframes) return;
        const t = audioPlayer.currentTime;
        const kfs = danceData.keyframes;
        while (currentBeatIndex < kfs.length && kfs[currentBeatIndex].time < t - 0.05) {
            currentBeatIndex++;
        }
        if (currentBeatIndex < kfs.length && Math.abs(t - kfs[currentBeatIndex].time) <= 0.06) {
            const ind = document.getElementById('beat-indicator');
            ind.classList.add('active');
            setTimeout(function() { ind.classList.remove('active'); }, 200);
            currentBeatIndex++;
        }
    }

    // -------------------------------------------------------------------------
    // Event listeners
    // -------------------------------------------------------------------------
    function setupEventListeners() {
        document.getElementById('headYaw').addEventListener('input', function() {
            head.rotation.y = parseFloat(this.value) * DEG;
            document.getElementById('yawValue').textContent = this.value + '°';
        });
        document.getElementById('headPitch').addEventListener('input', function() {
            head.rotation.x = parseFloat(this.value) * DEG;
            document.getElementById('pitchValue').textContent = this.value + '°';
        });
        document.getElementById('headRoll').addEventListener('input', function() {
            head.rotation.z = parseFloat(this.value) * DEG;
            document.getElementById('rollValue').textContent = this.value + '°';
        });

        document.getElementById('enableBeatSync').addEventListener('change', function() {
            beatSyncEnabled = this.checked;
        });

        const progressBar = document.getElementById('progress-bar');
        if (progressBar) {
            progressBar.style.cursor = 'pointer';
            progressBar.addEventListener('click', function(e) {
                if (audioPlayer.duration) {
                    audioPlayer.currentTime = (e.offsetX / this.offsetWidth) * audioPlayer.duration;
                    currentBeatIndex = 0;
                    lastAppliedPoseTime = -1;
                }
            });
        }

        renderer.domElement.addEventListener('mousedown', onMouseDown);
        renderer.domElement.addEventListener('mousemove', onMouseMove);
        renderer.domElement.addEventListener('mouseup',   onMouseUp);
        renderer.domElement.addEventListener('wheel',     onMouseWheel);
        renderer.domElement.addEventListener('touchstart', onTouchStart);
        renderer.domElement.addEventListener('touchmove',  onTouchMove);
        renderer.domElement.addEventListener('touchend',   onTouchEnd);
        window.addEventListener('resize', onWindowResize);
    }

    function onMouseDown(e) { isMouseDown = true; mouseX = e.clientX; mouseY = e.clientY; }
    function onMouseUp()    { isMouseDown = false; }
    function onMouseMove(e) {
        if (!isMouseDown) return;
        cameraAngleY += (e.clientX - mouseX) * 0.01;
        cameraAngleX += (e.clientY - mouseY) * 0.01;
        cameraAngleX = Math.max(-Math.PI/2, Math.min(Math.PI/2, cameraAngleX));
        updateCameraPosition();
        mouseX = e.clientX; mouseY = e.clientY;
    }
    function onMouseWheel(e) {
        const center = new THREE.Vector3(0, 3, 0);
        const dir = new THREE.Vector3().subVectors(camera.position, center).normalize();
        const dist = Math.max(5, Math.min(20, camera.position.distanceTo(center) + e.deltaY * 0.01));
        camera.position.copy(center.addScaledVector(dir, dist));
    }
    function onTouchStart(e) {
        if (e.touches.length === 1) { isMouseDown = true; mouseX = e.touches[0].clientX; mouseY = e.touches[0].clientY; }
    }
    function onTouchEnd() { isMouseDown = false; }
    function onTouchMove(e) {
        if (e.touches.length === 1 && isMouseDown) {
            cameraAngleY += (e.touches[0].clientX - mouseX) * 0.01;
            cameraAngleX += (e.touches[0].clientY - mouseY) * 0.01;
            cameraAngleX = Math.max(-Math.PI/2, Math.min(Math.PI/2, cameraAngleX));
            updateCameraPosition();
            mouseX = e.touches[0].clientX; mouseY = e.touches[0].clientY;
        }
    }
    function updateCameraPosition() {
        const dist = camera.position.distanceTo(new THREE.Vector3(0, 3, 0));
        camera.position.set(
            dist * Math.sin(cameraAngleY) * Math.cos(cameraAngleX),
            3   + dist * Math.sin(cameraAngleX),
            dist * Math.cos(cameraAngleY) * Math.cos(cameraAngleX)
        );
        camera.lookAt(0, 3, 0);
    }

    function resetHead() {
        head.rotation.set(0, 0, 0);
        document.getElementById('headYaw').value   = 0;
        document.getElementById('headPitch').value = 0;
        document.getElementById('headRoll').value  = 0;
        document.getElementById('yawValue').textContent   = '0°';
        document.getElementById('pitchValue').textContent = '0°';
        document.getElementById('rollValue').textContent  = '0°';
    }

    function randomMove() {
        const ry = (Math.random() - 0.5) * 120;
        const rx = (Math.random() - 0.5) * 90;
        const rz = (Math.random() - 0.5) * 60;
        document.getElementById('headYaw').value   = ry;
        document.getElementById('headPitch').value = rx;
        document.getElementById('headRoll').value  = rz;
        head.rotation.set(rx * DEG, ry * DEG, rz * DEG);
        document.getElementById('yawValue').textContent   = Math.round(ry) + '°';
        document.getElementById('pitchValue').textContent = Math.round(rx) + '°';
        document.getElementById('rollValue').textContent  = Math.round(rz) + '°';
    }

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    // -------------------------------------------------------------------------
    // Main animation loop
    // -------------------------------------------------------------------------
    function animate() {
        requestAnimationFrame(animate);

        updatePoseAnimation();

        const time = Date.now() * 0.001;

        spotLight1.position.x = 5 + Math.sin(time * 0.3) * 2;
        spotLight1.position.z = 8 + Math.cos(time * 0.4) * 1.5;
        spotLight2.color.setHSL((time * 0.1 % 1) * 0.3 + 0.8, 0.5, 0.6);

        const dancing = danceData && audioPlayer && !audioPlayer.paused;

        if (!dancing) {
            body.rotation.z        = Math.sin(time * 0.8) * 0.02;
            body.position.y        = 1.7 + Math.sin(time * 1.2) * 0.01;
            upperTorso.rotation.x  = Math.sin(time * 1.5) * 0.01;
            upperTorso.position.y  = 3.0 + Math.sin(time * 1.2) * 0.008;
            leftShoulderPivot.rotation.x  = Math.sin(time * 0.7) * 0.08;
            rightShoulderPivot.rotation.x = Math.sin(time * 0.7 + Math.PI) * 0.08;
        } else {
            upperTorso.position.y = 3.0 + Math.sin(time * 1.2) * 0.005;
        }

        if (!dancing && document.getElementById('headYaw').value == 0) {
            head.rotation.y += Math.sin(time * 0.6) * 0.001;
            head.rotation.x += Math.cos(time * 0.7) * 0.0005;
        }

        if (head.children.length > 1) head.children[1].rotation.z = Math.sin(time * 1.2) * 0.03;
        if (head.children.length > 2) head.children[2].rotation.z = Math.sin(time * 1.2 + Math.PI) * 0.03;
        if (waist) waist.rotation.z = Math.sin(time * 0.9) * 0.015;

        renderer.render(scene, camera);
    }

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------
    return { init, initAudio, togglePlayPause, stopAudio, updateTimeDisplay };
}
