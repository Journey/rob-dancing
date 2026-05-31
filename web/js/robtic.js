// Rob-Dancing: NOVA — futuristic robot dancer with keyframe-driven pose animation
function robtic() {
    const DEG = Math.PI / 180;

    let scene, camera, renderer;
    let head, body, upperTorso, waist;
    let spotLight1, spotLight2, beatLight;

    let energyCore    = null;
    let eyeMaterials  = [];
    let antennaBall   = null;
    let floorGlow     = null;
    let accentStripes = [];

    let leftShoulderPivot,  rightShoulderPivot;
    let leftElbowPivot,     rightElbowPivot;
    let leftHipPivot,       rightHipPivot;
    let leftKneePivot,      rightKneePivot;
    let leftAnklePivot,     rightAnklePivot;

    let mouseX = 0, mouseY = 0, isMouseDown = false;
    let cameraAngleX = 0, cameraAngleY = 0;

    let audioPlayer;
    let beatSyncEnabled  = true;
    let currentBeatIndex = 0;

    let danceData           = null;
    let lastAppliedPoseTime = -1;

    function init() {
        scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x020408, 0.050);
        buildBackground();
        camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 200);
        camera.position.set(0, 3.5, 9.5);
        camera.lookAt(0, 2.8, 0);
        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.35;
        document.getElementById('container').appendChild(renderer.domElement);
        buildLighting();
        createStage();
        createCharacter();
        initAudio();
        setupEventListeners();
        loadDanceData();
        animate();
    }

    function buildBackground() {
        const c = document.createElement('canvas');
        c.width = 512; c.height = 512;
        const ctx = c.getContext('2d');
        const g = ctx.createRadialGradient(256, 480, 20, 256, 200, 460);
        g.addColorStop(0,   '#08051A');
        g.addColorStop(0.5, '#040310');
        g.addColorStop(1,   '#020206');
        ctx.fillStyle = g; ctx.fillRect(0, 0, 512, 512);
        for (let i = 0; i < 160; i++) {
            const x = Math.random() * 512, y = Math.random() * 420;
            const r = Math.random() * 1.4, a = 0.3 + Math.random() * 0.7;
            ctx.fillStyle = `rgba(${140 + (Math.random()*115)|0},${160 + (Math.random()*95)|0},255,${a})`;
            ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
        }
        const hg = ctx.createLinearGradient(0, 340, 0, 512);
        hg.addColorStop(0, 'rgba(0,60,120,0)');
        hg.addColorStop(1, 'rgba(0,80,160,0.22)');
        ctx.fillStyle = hg; ctx.fillRect(0, 340, 512, 172);
        scene.background = new THREE.CanvasTexture(c);
    }

    function buildLighting() {
        scene.add(new THREE.AmbientLight(0x080C18, 0.7));
        spotLight1 = new THREE.SpotLight(0xDDEEFF, 2.2, 45, Math.PI / 5.5, 0.22, 1.2);
        spotLight1.position.set(6, 15, 8); spotLight1.target.position.set(0, 2.5, 0);
        spotLight1.castShadow = true;
        spotLight1.shadow.mapSize.width = spotLight1.shadow.mapSize.height = 2048;
        spotLight1.shadow.camera.near = 2; spotLight1.shadow.camera.far = 45;
        scene.add(spotLight1); scene.add(spotLight1.target);
        spotLight2 = new THREE.SpotLight(0x0088FF, 1.1, 40, Math.PI / 4, 0.35, 1.2);
        spotLight2.position.set(-10, 9, 3); spotLight2.target.position.set(0, 2.5, 0);
        scene.add(spotLight2); scene.add(spotLight2.target);
        const rim = new THREE.SpotLight(0xFF22AA, 0.7, 35, Math.PI / 3.5, 0.55, 1.5);
        rim.position.set(-3, 8, -11); rim.target.position.set(0, 3, 0);
        scene.add(rim); scene.add(rim.target);
        const backTop = new THREE.DirectionalLight(0xFF8833, 0.35);
        backTop.position.set(4, 10, -12); scene.add(backTop);
        beatLight = new THREE.PointLight(0x00FFFF, 0, 12, 2.0);
        beatLight.position.set(0, 3.5, 1.5); scene.add(beatLight);
        const under = new THREE.PointLight(0x6600CC, 0.35, 9, 2);
        under.position.set(0, -0.4, 0); scene.add(under);
        [{ pos:[-9,6,-9], color:0xFF2299 },{ pos:[9,6,-9], color:0x00CCFF },
         { pos:[-9,6,9],  color:0xFFAA00 },{ pos:[9,6,9],  color:0x44FF99 }
        ].forEach(({ pos, color }) => {
            const pl = new THREE.PointLight(color, 0.28, 22, 2);
            pl.position.set(...pos); scene.add(pl);
        });
    }

    function createStage() {
        const fc = document.createElement('canvas');
        fc.width = 1024; fc.height = 1024;
        const fctx = fc.getContext('2d');
        fctx.fillStyle = '#04040E'; fctx.fillRect(0, 0, 1024, 1024);
        const drawGrid = (color, lw, step) => {
            fctx.strokeStyle = color; fctx.lineWidth = lw;
            for (let i = 0; i <= 1024; i += step) {
                fctx.beginPath(); fctx.moveTo(i, 0); fctx.lineTo(i, 1024); fctx.stroke();
                fctx.beginPath(); fctx.moveTo(0, i); fctx.lineTo(1024, i); fctx.stroke();
            }
        };
        drawGrid('rgba(0,140,220,0.09)', 2.5, 64);
        drawGrid('rgba(0,200,255,0.22)', 1,   64);
        drawGrid('rgba(0,100,180,0.14)', 4,   256);
        fctx.shadowColor = 'rgba(0,220,255,0.8)'; fctx.shadowBlur = 6;
        fctx.strokeStyle = 'rgba(0,200,255,0.55)'; fctx.lineWidth = 2;
        fctx.beginPath(); fctx.moveTo(512, 0); fctx.lineTo(512, 1024); fctx.stroke();
        fctx.beginPath(); fctx.moveTo(0, 512); fctx.lineTo(1024, 512); fctx.stroke();
        fctx.shadowBlur = 0;
        const floorTex = new THREE.CanvasTexture(fc);
        floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping;
        floorTex.repeat.set(3.5, 3.5);
        const floor = new THREE.Mesh(
            new THREE.PlaneGeometry(55, 55),
            new THREE.MeshStandardMaterial({ map: floorTex, metalness: 0.85, roughness: 0.18 })
        );
        floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; floor.position.y = -0.5;
        scene.add(floor);
        const platform = new THREE.Mesh(
            new THREE.CylinderGeometry(3.8, 3.8, 0.10, 48),
            new THREE.MeshStandardMaterial({ color: 0x0A1220, metalness: 0.92, roughness: 0.12 })
        );
        platform.position.y = -0.55; platform.receiveShadow = true; scene.add(platform);
        const edgeRing = new THREE.Mesh(
            new THREE.TorusGeometry(3.8, 0.042, 10, 80),
            new THREE.MeshStandardMaterial({ color: 0x003355, emissive: 0x0066AA, emissiveIntensity: 1.2 })
        );
        edgeRing.position.y = -0.50; edgeRing.rotation.x = Math.PI / 2; scene.add(edgeRing);
        floorGlow = new THREE.Mesh(
            new THREE.RingGeometry(0.6, 1.9, 72),
            new THREE.MeshBasicMaterial({ color: 0x00CCFF, transparent: true, opacity: 0.10, side: THREE.DoubleSide })
        );
        floorGlow.rotation.x = -Math.PI / 2; floorGlow.position.y = -0.49; scene.add(floorGlow);
    }

    function createCharacter() {
        const mkS = (col, met, rou, emi, emiI) => new THREE.MeshStandardMaterial({
            color: col, metalness: met, roughness: rou,
            emissive: emi || 0x000000, emissiveIntensity: emiI || 0,
        });
        const armorMat  = mkS(0x1A2B3C, 0.75, 0.30);
        const plateMat  = mkS(0x243344, 0.70, 0.35);
        const chromeMat = mkS(0xC8D8E8, 0.95, 0.05);
        const accentMat = mkS(0x002233, 0.50, 0.35, 0x0088CC, 0.9);
        const visorMat  = mkS(0x001133, 0.20, 0.08, 0x0099FF, 1.4);
        const bootMat   = mkS(0x080C14, 0.85, 0.20);
        const ringMat   = mkS(0x7799BB, 0.90, 0.10, 0x0055AA, 0.4);
        const eyeMat = new THREE.MeshStandardMaterial({
            color: 0x002233, metalness: 0.1, roughness: 0.0,
            emissive: 0x00CCFF, emissiveIntensity: 2.5, transparent: true, opacity: 0.95,
        });
        eyeMaterials.push(eyeMat);
        const coreMat = new THREE.MeshStandardMaterial({
            color: 0x001122, metalness: 0.1, roughness: 0.0,
            emissive: 0x00FFFF, emissiveIntensity: 3.2, transparent: true, opacity: 0.92,
        });

        body = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.46, 0.62, 8), armorMat);
        body.position.y = 1.65; body.castShadow = true; scene.add(body);

        waist = new THREE.Mesh(new THREE.CylinderGeometry(0.29, 0.41, 0.16, 8), chromeMat);
        waist.position.y = 2.08; scene.add(waist);

        upperTorso = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.38, 1.02, 8), armorMat);
        upperTorso.position.y = 2.82; upperTorso.castShadow = true; scene.add(upperTorso);

        const chestPlate = new THREE.Mesh(new THREE.BoxGeometry(0.64, 0.68, 0.07), plateMat);
        chestPlate.position.set(0, 0.06, 0.45); upperTorso.add(chestPlate);

        energyCore = new THREE.Mesh(new THREE.SphereGeometry(0.105, 22, 22), coreMat);
        energyCore.position.set(0, 0.06, 0.51); upperTorso.add(energyCore);

        const coreRing = new THREE.Mesh(new THREE.TorusGeometry(0.135, 0.022, 8, 28), accentMat);
        coreRing.rotation.x = Math.PI / 2; coreRing.position.set(0, 0.06, 0.49); upperTorso.add(coreRing);

        [-0.16, 0.16].forEach(xOff => {
            const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.48, 0.045), accentMat.clone());
            stripe.position.set(xOff, 0.06, 0.48); upperTorso.add(stripe);
            accentStripes.push(stripe.material);
        });
        const hStripe = new THREE.Mesh(new THREE.BoxGeometry(0.60, 0.032, 0.045), accentMat.clone());
        hStripe.position.set(0, 0.06, 0.48); upperTorso.add(hStripe);
        accentStripes.push(hStripe.material);

        [-0.64, 0.64].forEach(x => {
            const pad = new THREE.Mesh(new THREE.CylinderGeometry(0.23, 0.18, 0.28, 8), armorMat);
            pad.rotation.z = Math.PI / 2; pad.position.set(x, 2.88, 0); pad.castShadow = true; scene.add(pad);
            const ring = new THREE.Mesh(new THREE.TorusGeometry(0.19, 0.034, 8, 22), ringMat);
            ring.position.set(x, 2.88, 0); scene.add(ring);
            const dot = new THREE.Mesh(new THREE.SphereGeometry(0.055, 10, 10), accentMat);
            dot.position.set(x < 0 ? x + 0.24 : x - 0.24, 2.88, 0); scene.add(dot);
        });

        head = new THREE.Group();
        head.position.set(0, 4.06, 0); scene.add(head);

        const helm = new THREE.Mesh(new THREE.SphereGeometry(0.52, 28, 22), armorMat);
        helm.scale.set(1, 1.06, 0.96); helm.castShadow = true; head.add(helm);

        const faceGeo = new THREE.SphereGeometry(0.505, 28, 22, 0, Math.PI * 2, Math.PI * 0.30, Math.PI * 0.42);
        head.add(new THREE.Mesh(faceGeo, plateMat));

        const visor = new THREE.Mesh(new THREE.BoxGeometry(0.92, 0.14, 0.055), visorMat);
        visor.position.set(0, 0.06, 0.44); head.add(visor);

        [-0.22, 0.22].forEach(x => {
            const eyeM = eyeMat.clone(); eyeMaterials.push(eyeM);
            const eye = new THREE.Mesh(new THREE.CircleGeometry(0.115, 22), eyeM);
            eye.position.set(x, 0.06, 0.462); head.add(eye);
            const dot = new THREE.Mesh(new THREE.CircleGeometry(0.052, 16),
                new THREE.MeshBasicMaterial({ color: 0xCCFFFF }));
            dot.position.z = 0.001; eye.add(dot);
        });

        const chin = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.09, 0.38), plateMat);
        chin.position.set(0, -0.37, 0.14); head.add(chin);

        [-0.55, 0.55].forEach((x, i) => {
            const fin = new THREE.Mesh(new THREE.BoxGeometry(0.068, 0.32, 0.24), armorMat);
            fin.position.set(x, 0.04, -0.02); head.add(fin);
            const fa = new THREE.Mesh(new THREE.BoxGeometry(0.022, 0.22, 0.038), accentMat);
            fa.position.set(i === 0 ? 0.016 : -0.016, 0.04, 0.10); fin.add(fa);
        });

        const ridge = new THREE.Mesh(new THREE.BoxGeometry(0.095, 0.055, 0.88), accentMat);
        ridge.position.set(0, 0.50, 0); head.add(ridge);

        const antStalk = new THREE.Mesh(new THREE.CylinderGeometry(0.017, 0.024, 0.48, 8), chromeMat);
        antStalk.position.set(0, 0.75, 0); head.add(antStalk);
        antennaBall = new THREE.Mesh(new THREE.SphereGeometry(0.052, 14, 14),
            new THREE.MeshStandardMaterial({
                color: 0x110000, metalness: 0.1, roughness: 0.05,
                emissive: 0xFF4400, emissiveIntensity: 2.0,
            }));
        antennaBall.position.set(0, 1.01, 0); head.add(antennaBall);

        const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.155, 0.20, 10), chromeMat);
        neck.position.set(0, 3.70, 0); scene.add(neck);

        const makeArm = (side) => {
            const sx = side === 'left' ? -1 : 1;
            const pivot = new THREE.Group();
            pivot.position.set(sx * 0.66, 3.08, 0); scene.add(pivot);
            const uArm = new THREE.Mesh(new THREE.CylinderGeometry(0.098, 0.118, 0.88, 8), armorMat);
            uArm.position.set(0, -0.44, 0); uArm.castShadow = true; pivot.add(uArm);
            const uStripe = new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.52, 0.09), accentMat);
            uStripe.position.set(sx * 0.088, -0.44, 0.04); pivot.add(uStripe);
            const eJ = new THREE.Mesh(new THREE.SphereGeometry(0.112, 14, 10), chromeMat);
            eJ.position.set(0, -0.92, 0); pivot.add(eJ);
            const eRing = new THREE.Mesh(new THREE.TorusGeometry(0.112, 0.028, 8, 18), ringMat);
            eRing.position.set(0, -0.92, 0); eRing.rotation.z = Math.PI / 2; pivot.add(eRing);
            const elbowPivot = new THREE.Group();
            elbowPivot.position.set(0, -0.92, 0); pivot.add(elbowPivot);
            const fa = new THREE.Mesh(new THREE.CylinderGeometry(0.082, 0.098, 0.74, 8), plateMat);
            fa.position.set(0, -0.37, 0); fa.castShadow = true; elbowPivot.add(fa);
            const wRing = new THREE.Mesh(new THREE.TorusGeometry(0.095, 0.022, 8, 16), chromeMat);
            wRing.position.set(0, -0.75, 0); wRing.rotation.z = Math.PI / 2; elbowPivot.add(wRing);
            const hand = new THREE.Mesh(new THREE.BoxGeometry(0.225, 0.195, 0.285), armorMat);
            hand.position.set(0, -0.855, 0.02); hand.castShadow = true; elbowPivot.add(hand);
            const knuckle = new THREE.Mesh(new THREE.BoxGeometry(0.20, 0.058, 0.058), chromeMat);
            knuckle.position.set(0, 0.10, 0.15); hand.add(knuckle);
            if (side === 'left') { leftShoulderPivot = pivot; leftElbowPivot = elbowPivot; }
            else                 { rightShoulderPivot = pivot; rightElbowPivot = elbowPivot; }
        };
        makeArm('left'); makeArm('right');

        const makeLeg = (side) => {
            const pivot = new THREE.Group();
            pivot.position.set(side === 'left' ? -0.26 : 0.26, 1.28, 0); scene.add(pivot);
            const thigh = new THREE.Mesh(new THREE.CylinderGeometry(0.165, 0.195, 0.96, 8), armorMat);
            thigh.position.set(0, -0.48, 0); thigh.castShadow = true; pivot.add(thigh);
            const kJ = new THREE.Mesh(new THREE.SphereGeometry(0.148, 14, 10), chromeMat);
            kJ.position.set(0, -0.98, 0); pivot.add(kJ);
            const kp = new THREE.Mesh(new THREE.BoxGeometry(0.23, 0.11, 0.075), plateMat);
            kp.position.set(0, -0.98, 0.14); pivot.add(kp);
            const kneePivot = new THREE.Group();
            kneePivot.position.set(0, -0.98, 0); pivot.add(kneePivot);
            const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.128, 0.158, 0.84, 8), plateMat);
            shin.position.set(0, -0.42, 0); shin.castShadow = true; kneePivot.add(shin);
            const sg = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.58, 0.055), armorMat);
            sg.position.set(0, -0.42, 0.156); kneePivot.add(sg);
            const sgLine = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.44, 0.040), accentMat);
            sgLine.position.set(0, -0.42, 0.185); kneePivot.add(sgLine);
            const aJ = new THREE.Mesh(new THREE.SphereGeometry(0.118, 12, 10), chromeMat);
            aJ.position.set(0, -0.90, 0); kneePivot.add(aJ);
            const anklePivot = new THREE.Group();
            anklePivot.position.set(0, -0.90, 0); kneePivot.add(anklePivot);
            const boot = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.34, 0.60), bootMat);
            boot.position.set(0, -0.17, 0.07); boot.castShadow = true; anklePivot.add(boot);
            const toe = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.22, 0.20), armorMat);
            toe.position.set(0, -0.27, 0.37); toe.rotation.x = -0.20; anklePivot.add(toe);
            const bootTrim = new THREE.Mesh(new THREE.BoxGeometry(0.40, 0.040, 0.62), chromeMat);
            bootTrim.position.set(0, 0.01, 0.07); anklePivot.add(bootTrim);
            const sole = new THREE.Mesh(new THREE.BoxGeometry(0.41, 0.088, 0.68), chromeMat);
            sole.position.set(0, -0.38, 0.07); anklePivot.add(sole);
            const soleGlow = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.036, 0.70),
                new THREE.MeshBasicMaterial({ color: 0x0088BB }));
            soleGlow.position.set(0, -0.423, 0.07); anklePivot.add(soleGlow);
            if (side === 'left') { leftHipPivot = pivot; leftKneePivot = kneePivot; leftAnklePivot = anklePivot; }
            else                 { rightHipPivot = pivot; rightKneePivot = kneePivot; rightAnklePivot = anklePivot; }
        };
        makeLeg('left'); makeLeg('right');
    }

    function loadDanceData() {
        fetch('data/shuangjiegun_dance.json')
            .then(r => r.json())
            .then(data => {
                danceData = data;
                console.log('[dance] Loaded: ' + data.keyframes.length + ' keyframes, tempo=' + data.tempo.toFixed(1) + ' BPM, duration=' + data.duration.toFixed(1) + 's');
            })
            .catch(() => { console.warn('[dance] shuangjiegun_dance.json not found; run make dance AUDIO=... first.'); });
    }

    function easeInOut(t) {
        t = Math.max(0, Math.min(1, t));
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }

    function lerpPose(a, b, t) {
        const e = easeInOut(t);
        const keys = ['head_yaw','head_pitch','shoulder_left','shoulder_right','elbow_left','elbow_right',
                       'hip_left','hip_right','knee_left','knee_right','ankle_left','ankle_right'];
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
        while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (kfs[mid].time <= time) lo = mid; else hi = mid; }
        return lerpPose(kfs[lo].pose, kfs[hi].pose, (time - kfs[lo].time) / (kfs[hi].transition || 0.3));
    }

    function applyPose(pose) {
        if (!pose) return;
        head.rotation.y =  pose.head_yaw   * DEG;
        head.rotation.x = -pose.head_pitch * DEG;
        leftShoulderPivot.rotation.x  = -pose.shoulder_left  * DEG;
        rightShoulderPivot.rotation.x = -pose.shoulder_right * DEG;
        leftElbowPivot.rotation.x     =  pose.elbow_left     * DEG;
        rightElbowPivot.rotation.x    =  pose.elbow_right    * DEG;
        leftHipPivot.rotation.x   = -pose.hip_left   * DEG;
        rightHipPivot.rotation.x  = -pose.hip_right  * DEG;
        leftKneePivot.rotation.x  =  pose.knee_left  * DEG;
        rightKneePivot.rotation.x =  pose.knee_right * DEG;
        leftAnklePivot.rotation.x  =  pose.ankle_left  * DEG;
        rightAnklePivot.rotation.x =  pose.ankle_right * DEG;
        const hipDiff = pose.hip_left - pose.hip_right;
        body.rotation.z       = -hipDiff * 0.003;
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

    function initAudio() {
        audioPlayer = document.getElementById('audioPlayer');
        audioPlayer.addEventListener('loadedmetadata', updateTimeDisplay);
        audioPlayer.addEventListener('timeupdate', function() {
            updateTimeDisplay(); updateProgress(); checkBeatIndicator();
        });
        audioPlayer.addEventListener('ended', function() {
            document.getElementById('playPauseBtn').textContent = '播放';
            document.getElementById('playPauseBtn').classList.remove('playing');
            currentBeatIndex = 0;
        });
    }

    function togglePlayPause() {
        const btn = document.getElementById('playPauseBtn');
        if (audioPlayer.paused) { audioPlayer.play(); btn.textContent = '暂停'; btn.classList.add('playing'); }
        else { audioPlayer.pause(); btn.textContent = '播放'; btn.classList.remove('playing'); }
    }

    function stopAudio() {
        audioPlayer.pause(); audioPlayer.currentTime = 0;
        document.getElementById('playPauseBtn').textContent = '播放';
        document.getElementById('playPauseBtn').classList.remove('playing');
        currentBeatIndex = 0; lastAppliedPoseTime = -1;
        applyPose({ head_yaw:0, head_pitch:0, shoulder_left:0, shoulder_right:0,
                    elbow_left:0, elbow_right:0, hip_left:0, hip_right:0,
                    knee_left:0, knee_right:0, ankle_left:0, ankle_right:0 });
    }

    function updateTimeDisplay() {
        document.getElementById('timeDisplay').textContent =
            formatTime(audioPlayer.currentTime) + ' / ' + formatTime(audioPlayer.duration);
    }
    function updateProgress() {
        if (audioPlayer.duration)
            document.getElementById('progress').style.width =
                (audioPlayer.currentTime / audioPlayer.duration * 100) + '%';
    }
    function formatTime(s) {
        if (isNaN(s)) return '00:00';
        const m = Math.floor(s / 60);
        return String(m).padStart(2,'0') + ':' + String(Math.floor(s % 60)).padStart(2,'0');
    }
    function checkBeatIndicator() {
        if (!beatSyncEnabled || !danceData || !danceData.keyframes) return;
        const t = audioPlayer.currentTime, kfs = danceData.keyframes;
        while (currentBeatIndex < kfs.length && kfs[currentBeatIndex].time < t - 0.05)
            currentBeatIndex++;
        if (currentBeatIndex < kfs.length && Math.abs(t - kfs[currentBeatIndex].time) <= 0.06) {
            beatLight.intensity = 2.8;
            if (floorGlow) floorGlow.material.opacity = 0.60;
            const ind = document.getElementById('beat-indicator');
            if (ind) { ind.classList.add('active'); setTimeout(() => ind.classList.remove('active'), 200); }
            currentBeatIndex++;
        }
    }

    function setupEventListeners() {
        const headYaw   = document.getElementById('headYaw');
        const headPitch = document.getElementById('headPitch');
        const headRoll  = document.getElementById('headRoll');
        if (headYaw)   headYaw.addEventListener('input',   function() { head.rotation.y = parseFloat(this.value) * DEG; document.getElementById('yawValue').textContent   = this.value + '°'; });
        if (headPitch) headPitch.addEventListener('input', function() { head.rotation.x = parseFloat(this.value) * DEG; document.getElementById('pitchValue').textContent = this.value + '°'; });
        if (headRoll)  headRoll.addEventListener('input',  function() { head.rotation.z = parseFloat(this.value) * DEG; document.getElementById('rollValue').textContent  = this.value + '°'; });
        const bsync = document.getElementById('enableBeatSync');
        if (bsync) bsync.addEventListener('change', function() { beatSyncEnabled = this.checked; });
        const pb = document.getElementById('progress-bar');
        if (pb) {
            pb.style.cursor = 'pointer';
            pb.addEventListener('click', function(e) {
                if (audioPlayer.duration) {
                    audioPlayer.currentTime = (e.offsetX / this.offsetWidth) * audioPlayer.duration;
                    currentBeatIndex = 0; lastAppliedPoseTime = -1;
                }
            });
        }
        renderer.domElement.addEventListener('mousedown',  onMouseDown);
        renderer.domElement.addEventListener('mousemove',  onMouseMove);
        renderer.domElement.addEventListener('mouseup',    onMouseUp);
        renderer.domElement.addEventListener('wheel',      onMouseWheel);
        renderer.domElement.addEventListener('touchstart', onTouchStart, { passive: true });
        renderer.domElement.addEventListener('touchmove',  onTouchMove,  { passive: true });
        renderer.domElement.addEventListener('touchend',   onTouchEnd);
        window.addEventListener('resize', onWindowResize);
    }

    function onMouseDown(e) { isMouseDown = true;  mouseX = e.clientX; mouseY = e.clientY; }
    function onMouseUp()    { isMouseDown = false; }
    function onMouseMove(e) {
        if (!isMouseDown) return;
        cameraAngleY += (e.clientX - mouseX) * 0.010;
        cameraAngleX += (e.clientY - mouseY) * 0.010;
        cameraAngleX = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 4, cameraAngleX));
        updateCameraPosition(); mouseX = e.clientX; mouseY = e.clientY;
    }
    function onMouseWheel(e) {
        const center = new THREE.Vector3(0, 3, 0);
        const dir  = new THREE.Vector3().subVectors(camera.position, center).normalize();
        const dist = Math.max(4, Math.min(22, camera.position.distanceTo(center) + e.deltaY * 0.01));
        camera.position.copy(center.clone().addScaledVector(dir, dist));
        camera.lookAt(0, 2.8, 0);
    }
    function onTouchStart(e) { if (e.touches.length===1) { isMouseDown=true; mouseX=e.touches[0].clientX; mouseY=e.touches[0].clientY; } }
    function onTouchEnd()    { isMouseDown = false; }
    function onTouchMove(e) {
        if (e.touches.length===1 && isMouseDown) {
            cameraAngleY += (e.touches[0].clientX - mouseX) * 0.010;
            cameraAngleX += (e.touches[0].clientY - mouseY) * 0.010;
            cameraAngleX = Math.max(-Math.PI/2.5, Math.min(Math.PI/4, cameraAngleX));
            updateCameraPosition(); mouseX=e.touches[0].clientX; mouseY=e.touches[0].clientY;
        }
    }
    function updateCameraPosition() {
        const dist = camera.position.distanceTo(new THREE.Vector3(0, 3, 0));
        camera.position.set(
            dist * Math.sin(cameraAngleY) * Math.cos(cameraAngleX),
            3   + dist * Math.sin(cameraAngleX),
            dist * Math.cos(cameraAngleY) * Math.cos(cameraAngleX)
        );
        camera.lookAt(0, 2.8, 0);
    }

    function resetHead() {
        head.rotation.set(0, 0, 0);
        ['headYaw','headPitch','headRoll'].forEach(id => { const el = document.getElementById(id); if (el) el.value = 0; });
        ['yawValue','pitchValue','rollValue'].forEach(id => { const el = document.getElementById(id); if (el) el.textContent = '0°'; });
    }
    function randomMove() {
        const ry=(Math.random()-0.5)*80, rx=(Math.random()-0.5)*50, rz=(Math.random()-0.5)*25;
        head.rotation.set(rx*DEG, ry*DEG, rz*DEG);
        [['headYaw','yawValue',ry],['headPitch','pitchValue',rx],['headRoll','rollValue',rz]].forEach(([ii,vi,v]) => {
            const ie=document.getElementById(ii), ve=document.getElementById(vi);
            if (ie) ie.value=v; if (ve) ve.textContent=Math.round(v)+'°';
        });
    }
    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight);
    }

    function animate() {
        requestAnimationFrame(animate);
        const time    = Date.now() * 0.001;
        const dancing = danceData && audioPlayer && !audioPlayer.paused;
        updatePoseAnimation();

        if (energyCore) {
            const pulse = dancing ? 1.0 + Math.sin(time * 9.0) * 0.28 : 1.0 + Math.sin(time * 1.6) * 0.09;
            energyCore.scale.setScalar(pulse);
            energyCore.material.emissiveIntensity = dancing
                ? 2.8 + Math.sin(time * 9.0) * 1.8
                : 2.0 + Math.sin(time * 1.6) * 0.7;
        }

        const eyeTarget = dancing ? 2.2 + Math.sin(time * 7.0) * 1.0 : 1.4 + Math.sin(time * 1.0) * 0.4;
        eyeMaterials.forEach(m => { m.emissiveIntensity = eyeTarget; });

        if (dancing) {
            const c = new THREE.Color().setHSL(((time * 0.12) % 1) * 0.25 + 0.52, 0.9, 0.55);
            accentStripes.forEach(m => { m.emissive.set(c); m.emissiveIntensity = 0.8; });
        } else {
            accentStripes.forEach(m => { m.emissive.setHex(0x0088CC); m.emissiveIntensity = 0.9; });
        }

        if (antennaBall) antennaBall.material.emissiveIntensity = 1.2 + Math.sin(time * 3.0) * 1.2;

        if (beatLight.intensity > 0) beatLight.intensity = Math.max(0, beatLight.intensity - 0.18);

        if (floorGlow) {
            floorGlow.material.opacity = Math.max(0.08, floorGlow.material.opacity - 0.022);
            floorGlow.rotation.z += dancing ? 0.016 : 0.005;
        }

        const orbit = dancing ? 0.45 : 0.16;
        spotLight1.position.x = 6 + Math.sin(time * orbit * 0.70) * 3;
        spotLight1.position.z = 8 + Math.cos(time * orbit * 0.50) * 2;

        spotLight2.color.setHSL(dancing ? (time * 0.10) % 1 : 0.59, 0.85, 0.52);

        if (!dancing) {
            body.rotation.z               = Math.sin(time * 0.68) * 0.016;
            body.position.y               = 1.65 + Math.sin(time * 1.05) * 0.007;
            waist.position.y              = 2.08 + Math.sin(time * 1.05) * 0.006;
            upperTorso.rotation.x         = Math.sin(time * 1.25) * 0.009;
            upperTorso.position.y         = 2.82 + Math.sin(time * 1.05) * 0.006;
            leftShoulderPivot.rotation.x  =  Math.sin(time * 0.60) * 0.055;
            rightShoulderPivot.rotation.x = -Math.sin(time * 0.60) * 0.055;
            head.rotation.y += Math.sin(time * 0.55) * 0.0008;
            head.rotation.x += Math.cos(time * 0.65) * 0.0004;
        } else {
            upperTorso.position.y = 2.82 + Math.sin(time * 1.05) * 0.004;
        }

        renderer.render(scene, camera);
    }

    function switchTrack(audioSrc, danceSrc) {
        stopAudio();
        audioPlayer.src = audioSrc;
        audioPlayer.load();
        danceData = null;
        lastAppliedPoseTime = -1;
        currentBeatIndex = 0;
        fetch(danceSrc)
            .then(r => r.json())
            .then(data => {
                danceData = data;
                console.log('[dance] Switched to ' + danceSrc + ': ' + data.keyframes.length + ' keyframes, ' + data.tempo.toFixed(1) + ' BPM');
            })
            .catch(() => console.warn('[dance] Failed to load: ' + danceSrc));
    }

    return { init, togglePlayPause, stopAudio, updateTimeDisplay, switchTrack };
}
