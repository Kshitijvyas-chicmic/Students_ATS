document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const role = urlParams.get('role');
    const roleDisplay = document.getElementById('roleDisplay');
    const questionContainer = document.getElementById('questionContainer');
    const quizSection = document.getElementById('quizSection');
    const loaderSection = document.getElementById('loaderSection');
    const progressInner = document.getElementById('progressInner');
    const submitBtn = document.getElementById('submitBtn');
    const resultSection = document.getElementById('resultSection');
    const finalScore = document.getElementById('finalScore');

    if (!role) {
        window.location.href = 'index.html';
        return;
    }

    roleDisplay.textContent = `Target Role: ${role}`;

    let currentInterviewId = null;
    let questions = [];
    let userAnswers = [];

    // 1. Start Interview & Fetch Questions
    try {
        const res = await fetch('/api/interview/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: role }),
            credentials: 'include'
        });

        if (!res.ok) throw new Error("Could not start interview");

        const data = await res.json();
        currentInterviewId = data.interview_id;
        questions = data.questions;
        userAnswers = new Array(questions.length).fill(null);

        loaderSection.hidden = true;
        quizSection.hidden = false;
        renderQuestions();
    } catch (err) {
        console.error(err);
        alert("Failed to start session. Return to dashboard.");
        window.location.href = 'index.html';
    }

    function renderQuestions() {
        questionContainer.innerHTML = '';
        questions.forEach((q, qIndex) => {
            const qDiv = document.createElement('div');
            qDiv.className = 'card question-card';
            qDiv.innerHTML = `
                <h4>Question ${qIndex + 1}: ${q.question_name}</h4>
                <div class="options-grid">
                    ${q.options.map(opt => `
                        <button class="option-btn" onclick="selectOption(${qIndex}, '${opt.replace(/'/g, "\\'")}', this)">
                            ${opt}
                        </button>
                    `).join('')}
                </div>
            `;
            questionContainer.appendChild(qDiv);
        });
    }

    window.selectOption = (qIndex, option, btn) => {
        userAnswers[qIndex] = option;
        updateProgress();

        // Highlight active button
        const buttons = btn.parentElement.querySelectorAll('.option-btn');
        buttons.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
    };

    function updateProgress() {
        const answered = userAnswers.filter(a => a !== null).length;
        const total = userAnswers.length;
        progressInner.style.width = `${(answered / total) * 100}%`;
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', async () => {
            if (userAnswers.includes(null)) {
                if (!confirm("You haven't answered all questions. Submit?")) return;
            }

            submitBtn.disabled = true;
            submitBtn.textContent = "Submitting answers...";

            try {
                const res = await fetch('/api/interview/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        interview_id: currentInterviewId,
                        user_answers: userAnswers
                    }),
                    credentials: 'include'
                });

                if (!res.ok) throw new Error("Submission failed");

                const data = await res.json();

                // Show result screen
                quizSection.hidden = true;
                resultSection.hidden = false;
                finalScore.textContent = `${data.score}%`;
            } catch (err) {
                console.error(err);
                const errorDetail = err.message || "Unknown error";
                alert(`Submission error: ${errorDetail}. If you started the quiz before a server reload, please start a new session.`);
                submitBtn.disabled = false;
                submitBtn.textContent = "Submit Final Answers";
            }
        });
    }
});
