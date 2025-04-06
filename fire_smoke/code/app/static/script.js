document.addEventListener('DOMContentLoaded', function() {

    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const fileType = document.getElementById('file-type');
    const detectBtn = document.getElementById('detect-btn');
    const resetBtn = document.getElementById('reset-btn');
    const loading = document.getElementById('loading');
    const resultsCard = document.getElementById('results-card');
    const resultsContainer = document.getElementById('results-container');
    const resultVisualize = document.getElementById('result-visualize');
    const resultImage = document.getElementById('result-image');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const errorMessage = document.getElementById('error-message');

    let selectedFile = null;
    let detectionWS = null;
    let lastAlertTime = 0;
    const ALERT_INTERVAL = 3000; // 语音提示最小间隔（毫秒）
    // 拖放功能
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#4285F4';
        uploadArea.style.backgroundColor = '#f0f7ff';
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#d0d7de';
        uploadArea.style.backgroundColor = '#fafbfc';
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#d0d7de';
        uploadArea.style.backgroundColor = '#fafbfc';

        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // 点击上传
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });

    // 处理文件
    function handleFile(file) {
        // 验证文件类型
        const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        const validVideoTypes = ['video/mp4', 'video/avi', 'video/mov'];
        if (!validTypes.includes(file.type) && !validVideoTypes.includes(file.type)) {
            showError('请上传有效的文件');
            resetFile();
            return;
        }

        // // 验证文件大小
        // if (file.size > 10 * 1024 * 1024) {  // 10MB
        //     showError('文件大小不能超过10MB');
        //     resetFile();
        //     return;
        // }

        // 验证文件是否为空
        if (file.size === 0) {
            showError('文件不能为空');
            resetFile();
            return;
        }

        selectedFile = file;

        // 隐藏错误消息
        errorMessage.style.display = 'none';


        if (validTypes.includes(file.type)) {
            // 显示文件预览
            const reader = new FileReader();

            reader.onload = function (e) {
                // 创建Image对象验证图片是否可以正常加载
                const img = new Image();
                img.onload = function () {
                    // 图片成功加载
                    previewImage.src = e.target.result;
                    previewContainer.style.display = 'block';

                    // 显示文件信息
                    fileName.textContent = file.name;
                    fileSize.textContent = formatFileSize(file.size);
                    fileType.textContent = file.type;

                    // 启用检测按钮
                    detectBtn.disabled = false;
                };

                img.onerror = function () {
                    // 图片加载失败
                    showError('图片文件已损坏或格式不兼容');
                    resetFile();
                };

                img.src = e.target.result;
            }

            reader.onerror = function () {
                showError('读取文件时发生错误');
                resetFile();
            };

            reader.readAsDataURL(file);
        }

        if (validVideoTypes.includes(file.type)) {
            const videoPreview = document.createElement('video');
            videoPreview.src = URL.createObjectURL(file);
            videoPreview.controls = true;
            videoPreview.style.width = '100%'; // 设置宽度为容器的50%
            videoPreview.style.height = 'auto';
            previewContainer.innerHTML = ''; // 清空预览容器
            previewContainer.appendChild(videoPreview);
            previewContainer.style.display = 'block';

            // 显示文件信息
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            fileType.textContent = file.type;

            // 启用检测按钮
            detectBtn.disabled = false;
        }
    }


    // 重置文件选择状态
    function resetFile() {
        fileInput.value = '';
        selectedFile = null;
        previewContainer.style.display = 'none';
        detectBtn.disabled = true;
    }

    // 启动检测
    detectBtn.addEventListener('click', function() {
        if (!selectedFile) return;

        if (fileInput.getAttribute('accept') === 'image/*') {
            detectImage(selectedFile); // 图片检测
        } else {
            detectVideo(selectedFile); // 视频检测
    }
    });

    // 显示结果
    function showResults(response) {
        if (response.success) {
            // 清空结果容器
            resultsContainer.innerHTML = '';

            let fireSpots = 0;
            let smokeSpots = 0;

            // 添加检测到的对象
            response.data.objects.forEach(obj => {
                if (obj.class === 'fire') {
                    fireSpots++;
                }
                if (obj.class === 'smoke') {
                    smokeSpots++;
                }
            });


            if (response.data.processedImage) {
                const summaryItem = document.createElement('div');
                summaryItem.className = 'result-item';
                summaryItem.innerHTML = `
                <div class="result-content">
                    <div class="result-title">火焰数量: ${fireSpots}</div>
                    <div class="result-title">烟雾数量: ${smokeSpots}</div>
                </div>
                `;
                resultsContainer.appendChild(summaryItem)
                resultImage.src = 'data:image/jpeg;base64,' + response.data.processedImage;
                resultVisualize.style.display = 'block';
            }


            const videoElement = document.querySelector('#result-video');
            if (videoElement) {
                videoElement.style.display = 'none';
            }

            // 显示结果卡片
            resultsCard.style.display = 'block';

            // 滚动到结果区域
            resultsCard.scrollIntoView({behavior: 'smooth'});
        }else {
            showError('检测失败: ' + (response.message || '未知错误'));
        }
    }

    // 重置按钮
    resetBtn.addEventListener('click', function() {
        // 重置文件输入
        fileInput.value = '';
        selectedFile = null;

        // 隐藏预览
        previewContainer.style.display = 'none';

        // 禁用检测按钮
        detectBtn.disabled = true;

        // 隐藏结果
        resultsCard.style.display = 'none';

        // 隐藏错误消息
        errorMessage.style.display = 'none';

        // 隐藏进度条
        progressContainer.style.display = 'none';
        progressBar.style.width = '0%';
    });

    // 辅助函数
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' 字节';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';

        // 使错误消息明显
        errorMessage.classList.add('error-shake');
        setTimeout(() => {
            errorMessage.classList.remove('error-shake');
        }, 500);

        // 滚动到错误消息
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function animateProgressBar() {
        let width = 0;
        const interval = setInterval(function() {
            if (width >= 90) {
                clearInterval(interval);
            } else {
                width += Math.random() * 5;
                progressBar.style.width = width + '%';
            }
        }, 100);
    }

    // 获取切换按钮
    const imageModeBtn = document.getElementById('image-mode-btn');
    const videoModeBtn = document.getElementById('video-mode-btn');

    // 切换模式
    function switchMode(activeBtn, inactiveBtn) {
        activeBtn.classList.add('active');
        inactiveBtn.classList.remove('active');
    }

    // 图片模式按钮点击事件
    imageModeBtn.addEventListener('click', function () {
        switchMode(imageModeBtn, videoModeBtn);
        // 更新上传区域提示
        uploadArea.querySelector('.upload-text').textContent = '点击或拖拽图片到此处上传';
        uploadArea.querySelector('.upload-subtext').textContent = '支持 JPG、PNG、JPEG 格式，最大 10MB，图片必须完好无损';
        fileInput.setAttribute('accept', 'image/*');
    });

    // 视频模式按钮点击事件
    videoModeBtn.addEventListener('click', function () {
        switchMode(videoModeBtn, imageModeBtn);
        // 更新上传区域提示
        uploadArea.querySelector('.upload-text').textContent = '点击或拖拽视频到此处上传';
        uploadArea.querySelector('.upload-subtext').textContent = '支持 MP4、AVI、MOV 格式，最大 100MB，视频必须完好无损';
        fileInput.setAttribute('accept', 'video/*');
    });

    function speak(text) {
        if ('speechSynthesis' in window) {
           const utterance = new SpeechSynthesisUtterance(text);
           utterance.lang = 'zh-CN';
           utterance.rate = 0.9; // 稍慢速更清晰
           window.speechSynthesis.speak(utterance);
        } else {
           console.warn("浏览器不支持语音合成");


        }
    }

function detectVideo(file) {
    if (!file) return;

    // 检查是否支持WebSocket并优先使用实时检测
    const useWebSocket = window.WebSocket && navigator.onLine;

    if (useWebSocket) {
        realtimeVideoDetection(file);
    } else {
        legacyVideoDetection(file);
    }
}

// 实时视频检测（WebSocket）
function realtimeVideoDetection(file) {
    // 初始化UI状态
    loading.style.display = 'block';
    progressContainer.style.display = 'block';
    resultsCard.style.display = 'none';
    resultVisualize.style.display = 'block'; // 确保结果可视化区域可见

    // 创建视频元素
    const video = document.createElement('video');
    video.src = URL.createObjectURL(file);
    video.muted = true;
    video.playsInline = true;
    video.controls = true;
    video.style.width = '100%';
    video.style.height = 'auto';

    // 初始化WebSocket
    detectionWS = new WebSocket(`ws://${location.host}/ws/video-detection`);

    detectionWS.onopen = () => {
        console.log("WebSocket连接已建立，开始检测");
    };

    detectionWS.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // 语音提示
        if (data.type === 'detection') {
            const now = Date.now();
            if (now - lastAlertTime >= ALERT_INTERVAL) {
                if (data.classes.includes('fire')) {
                    speak('警告！检测到火焰');
                    lastAlertTime = now;
                }
                if (data.classes.includes('smoke')) {
                    speak('警告！检测到烟雾');
                    lastAlertTime = now;
                }
            }
        }

        // 显示检测结果（如果有）
        if (data.processedImage) {
            resultImage.src = 'data:image/jpeg;base64,' + data.processedImage;
            resultVisualize.style.display = 'block';
        }
    };

    detectionWS.onclose = () => {
        console.log("WebSocket连接已关闭");
        loading.style.display = 'none';
        progressContainer.style.display = 'none';
    };

    detectionWS.onerror = (error) => {
        console.error("WebSocket错误:", error);
        loading.style.display = 'none';
        progressContainer.style.display = 'none';
        showError('实时视频检测失败，将尝试传统方式');

        // 如果WebSocket失败，回退到传统方式
        legacyVideoDetection(file);
    };

    // 帧处理
    video.onloadedmetadata = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        video.play();

        const processFrame = () => {
            if (video.paused || video.ended || detectionWS.readyState !== WebSocket.OPEN) {
                if (detectionWS.readyState !== WebSocket.OPEN) {
                    console.log("WebSocket连接已关闭，停止帧处理");
                }
                loading.style.display = 'none';
                return;
            }

            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            canvas.toBlob(blob => {
                if (detectionWS?.readyState === WebSocket.OPEN) {
                    blob.arrayBuffer().then(buf => detectionWS.send(buf));
                }
            }, 'image/jpeg', 0.8);

            setTimeout(processFrame, 100); // 10fps
        };

        processFrame();
    };

    // 显示视频和结果
    resultsContainer.innerHTML = '';
    resultsContainer.appendChild(video);
    resultsCard.style.display = 'block';
    resultsCard.scrollIntoView({behavior: 'smooth'});
}

// 传统视频检测（文件上传方式）
function legacyVideoDetection(file) {
    progressContainer.style.display = 'block';
    animateProgressBar();
    loading.style.display = 'block';
    resultsCard.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    fetch('/detect_video', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        loading.style.display = 'none';
        progressContainer.style.display = 'none';

        const videoElement = document.createElement('video');
        videoElement.src = URL.createObjectURL(blob);
        videoElement.controls = true;
        videoElement.style.width = '100%';
        videoElement.style.height = 'auto';

        resultsContainer.innerHTML = '';
        resultsContainer.appendChild(videoElement);
        resultsCard.style.display = 'block';
        resultImage.style.display = 'none';
        resultsCard.scrollIntoView({behavior: 'smooth'});
    })
    .catch(error => {
        loading.style.display = 'none';
        progressContainer.style.display = 'none';
        showError('视频检测失败: ' + error.message);
    });
}

// 语音提示功能
function speak(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zh-CN';
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    }
}

    function detectImage(file) {
        if (!file) return;
        // 显示进度条
        progressContainer.style.display = 'block';
        animateProgressBar();

        // 显示加载状态
        loading.style.display = 'block';

        // 隐藏结果卡片
        resultsCard.style.display = 'none';

        // 创建FormData实例
        const formData = new FormData();
        formData.append('file', selectedFile);

        // 发送到后端的请求
        fetch('/detect', {
            method: 'POST',
            body: formData
        })
        .then(response => {

            return response.json();
        })
        .then(data => {
            // 隐藏加载状态和进度条
            loading.style.display = 'none';
            progressContainer.style.display = 'none';


            // 显示结果
            showResults(data);
        })
        .catch(error => {
            // 隐藏加载状态和进度条
            loading.style.display = 'none';
            progressContainer.style.display = 'none';

            showError('检测失败: ' + error.message);
        });
    }
});
