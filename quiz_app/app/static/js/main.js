document.addEventListener('DOMContentLoaded', function() {
    const quizForm = document.getElementById('quiz-form');
    const resultDiv = document.getElementById('result');
    const resultText = document.querySelector('.result-text');
    const nextBtn = document.getElementById('next-btn');
    const answerInput = document.getElementById('answer');
    const submitBtn = document.querySelector('#quiz-form button[type="submit"]');

    // 로컬 스토리지 키 상수
    const STORAGE_KEY = 'quiz_state';

    // 상태 저장 함수
    async function saveState() {
        try {
            const response = await fetch('/quiz/save_state', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            const state = await response.json();
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                timestamp: new Date().getTime(),
                state: state
            }));
        } catch (error) {
            console.error('상태 저장 실패:', error);
        }
    }

    // 상태 불러오기 함수
    async function loadState() {
        const savedData = localStorage.getItem(STORAGE_KEY);
        if (savedData) {
            try {
                const { timestamp, state } = JSON.parse(savedData);
                // 24시간이 지난 데이터는 무시
                if (new Date().getTime() - timestamp < 24 * 60 * 60 * 1000) {
                    await fetch('/quiz/load_state', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(state)
                    });
                    // 상태 로드 후 화면 업데이트
                    updateStats(state.stats);
                    updateProgress(state.progress);
                } else {
                    localStorage.removeItem(STORAGE_KEY);
                }
            } catch (error) {
                console.error('상태 불러오기 실패:', error);
                localStorage.removeItem(STORAGE_KEY);
            }
        }
    }

    // 페이지 로드시 저장된 상태 불러오기
    loadState();

    function updateStats(stats) {
        document.querySelector('.accuracy').textContent = `${stats.accuracy}%`;
        document.querySelector('.combo-count').textContent = stats.current_combo;
        document.querySelector('.max-combo').textContent = stats.max_combo;
    }

    function updateProgress(progress) {
        const progressBar = document.querySelector('.progress');
        const progressText = document.querySelector('.progress-text');
        
        if (progressBar && progressText) {
            progressBar.style.width = `${progress.percentage}%`;
            progressText.textContent = 
                `진행률: ${progress.answered}/${progress.total} (${progress.percentage.toFixed(1)}%)`;
        }
    }

    if (quizForm) {
        quizForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(quizForm);
            const response = await fetch('/quiz/check', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            resultDiv.style.display = 'block';
            if (result.correct) {
                resultText.textContent = '정답입니다!';
                resultText.className = 'result-text correct';
                answerInput.disabled = true;
                submitBtn.disabled = true;
                nextBtn.style.display = 'block';
            } else {
                resultText.textContent = `틀렸습니다. 정답은 "${result.correct_answer}" 입니다.`;
                resultText.className = 'result-text incorrect';
                answerInput.value = '';
                answerInput.focus();
            }
            
            const exampleKo = document.querySelector('.example-ko');
            if (exampleKo) {
                exampleKo.textContent = result.example_ko || '';
            }
            
            updateStats(result.stats);
            updateProgress(result.progress);
            
            // 정답 체크 후 상태 저장
            await saveState();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', async function() {
            const response = await fetch('/quiz/next');
            const data = await response.json();
            
            if (data.question) {
                document.querySelector('.word').textContent = data.question.word || '';
                document.querySelector('.example').textContent = data.question.example_en || '';
                if (data.question.lesson) {
                    document.querySelector('.lesson-info').textContent = `Lesson ${data.question.lesson}`;
                }
            }
            
            answerInput.disabled = false;
            submitBtn.disabled = false;
            answerInput.value = '';
            answerInput.focus();
            
            updateStats(data.stats);
            updateProgress(data.progress);
            
            resultDiv.style.display = 'none';
            nextBtn.style.display = 'none';
            
            const exampleKo = document.querySelector('.example-ko');
            if (exampleKo) {
                exampleKo.textContent = '';
            }
            
            // 다음 문제로 넘어갈 때도 상태 저장
            await saveState();
        });
    }

    // 리셋 버튼 추가
    const resetBtn = document.createElement('button');
    resetBtn.textContent = '진행 상황 초기화';
    resetBtn.className = 'reset-btn';
    resetBtn.addEventListener('click', async function() {
        if (confirm('진행 상황을 초기화하시겠습니까?')) {
            localStorage.removeItem(STORAGE_KEY);
            location.reload();
        }
    });
    document.querySelector('.quiz-container').appendChild(resetBtn);

    // 차트 관련 코드
    let accuracyChart = null;
    let progressChart = null;

    function initializeCharts() {
        const accuracyCtx = document.getElementById('accuracyChart').getContext('2d');
        const progressCtx = document.getElementById('progressChart').getContext('2d');

        // 정답률 차트
        accuracyChart = new Chart(accuracyCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '정답률 변화',
                    data: [],
                    borderColor: '#28a745',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        // 진행률 차트
        progressChart = new Chart(progressCtx, {
            type: 'doughnut',
            data: {
                labels: ['완료', '남은 문제'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#28a745', '#dee2e6']
                }]
            },
            options: {
                responsive: true
            }
        });
    }

    // 통계 데이터 업데이트
    function updateCharts(stats, progress) {
        // 현재 시간 추가
        const now = new Date().toLocaleTimeString();
        
        // 정답률 차트 업데이트
        accuracyChart.data.labels.push(now);
        accuracyChart.data.datasets[0].data.push(stats.accuracy);
        
        // 최근 10개 데이터만 표시
        if (accuracyChart.data.labels.length > 10) {
            accuracyChart.data.labels.shift();
            accuracyChart.data.datasets[0].data.shift();
        }
        
        // 진행률 차트 업데이트
        progressChart.data.datasets[0].data = [
            progress.answered,
            progress.total - progress.answered
        ];
        
        accuracyChart.update();
        progressChart.update();
        
        // 통계 요약 업데이트
        document.getElementById('today-solved').textContent = stats.total_attempts;
        document.getElementById('today-accuracy').textContent = stats.accuracy;
        document.getElementById('today-max-combo').textContent = stats.max_combo;
        document.getElementById('total-solved').textContent = progress.answered;
        document.getElementById('total-accuracy').textContent = stats.accuracy;
        document.getElementById('total-max-combo').textContent = stats.max_combo;
    }

    // 모달 관련 코드
    const modal = document.getElementById('stats-modal');
    const btn = document.getElementById('show-stats-btn');
    const span = document.getElementsByClassName('close')[0];
    
    // 차트 초기화
    initializeCharts();

    btn.onclick = function() {
        modal.style.display = 'block';
    }

    span.onclick = function() {
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    // 기존 updateStats 함수 수정
    const originalUpdateStats = updateStats;
    updateStats = function(stats) {
        originalUpdateStats(stats);
        updateCharts(stats, quiz.get_progress());
    }
});
