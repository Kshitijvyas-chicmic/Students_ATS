document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyzeForm');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resumeFile');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const submitBtn = document.getElementById('submitBtn');
    const loader = submitBtn.querySelector('.loader');
    const btnText = submitBtn.querySelector('.btn-text');

    const resultSection = document.getElementById('resultSection');
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreText = document.getElementById('scoreText');
    const skillsList = document.getElementById('skillsList');
    const missingSkillsList = document.getElementById('missingSkillsList');
    const expValue = document.getElementById('expValue');
    const fitValue = document.getElementById('fitValue');
    const projValue = document.getElementById('projValue');
    const targetRoleInput = document.getElementById('targetRole');
    const interimJobs = document.getElementById('interimJobs');
    const interimJobLinksList = document.getElementById('interimJobLinks');

    function populateJobLinks(container, role) {
        const roleQuery = encodeURIComponent(role);
        const links = [
            { id: 'linkedin', name: 'LinkedIn', icon: '🔗', url: `https://www.linkedin.com/jobs/search/?keywords=${roleQuery}&f_TPR=r3600`, class: 'linkedin' },
            { id: 'indeed', name: 'Indeed', icon: '🔍', url: `https://www.indeed.com/jobs?q=${roleQuery}&fromage=1`, class: 'indeed' },
            { id: 'naukri', name: 'Naukri', icon: '💼', url: `https://www.naukri.com/${role.replace(/\s+/g, '-')}-jobs?freshness=1`, class: 'naukri' }
        ];

        container.innerHTML = '';
        links.forEach(link => {
            const a = document.createElement('a');
            a.href = link.url;
            a.target = '_blank';
            a.className = `job-link-btn ${link.class}`;
            a.innerHTML = `
                <span class="btn-icon">${link.icon}</span>
                <span class="btn-name">${link.name} Jobs</span>
            `;
            container.appendChild(a);
        });
    }

    // Drag and drop logic
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    ['dragleave', 'drop'].forEach(event => {
        dropZone.addEventListener(event, () => dropZone.classList.remove('dragover'));
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            updateFileName(files[0].name);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            updateFileName(fileInput.files[0].name);
        }
    });

    function updateFileName(name) {
        fileNameDisplay.innerHTML = `Selected: <span class="browse">${name}</span>`;
    }

    // Form Submission
    form.addEventListener('submit', async (e) => {
        console.log("Submit button clicked!");
        e.preventDefault();

        const file = fileInput.files[0];
        const targetRole = document.getElementById('targetRole').value;

        if (!file) {
            alert('Please select a resume (PDF)');
            return;
        }

        // UI Loading State
        submitBtn.disabled = true;
        loader.hidden = false;
        btnText.style.opacity = '0.5';
        resultSection.hidden = true;

        // Show Instant Jobs immediately after submit
        interimJobs.hidden = false;
        populateJobLinks(interimJobLinksList, targetRole);
        interimJobs.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Status Messaging Logic
        const statusContainer = document.getElementById('statusContainer');
        const statusText = document.getElementById('statusText');
        statusContainer.hidden = false;

        const messages = [
            `Parsing your resume for ${targetRole}...`,
            `Analyzing experience against ${targetRole} standards...`,
            "Extracting specific technical skills...",
            `Evaluating role fit for ${targetRole}...`,
            "Identifying critical skill gaps...",
            "Calculating precise ATS score...",
            "Generating direct job links...",
            "Finalizing your report..."
        ];

        let msgIndex = 0;
        statusText.textContent = messages[0];

        const statusInterval = setInterval(() => {
            msgIndex = (msgIndex + 1) % messages.length;
            statusText.textContent = messages[msgIndex];
        }, 3000); // Change message every 3 seconds for better dynamic feel

        const formData = new FormData();
        formData.append('resume', file);
        formData.append('target_role', targetRole);

        try {
            const response = await fetch('http://127.0.0.1:8000/api/resume/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Server error');

            const data = await response.json();
            displayResults(data, targetRole);
        } catch (error) {
            console.error(error);
            alert('Error analyzing resume. Make sure backend and Ollama are running.');
        } finally {
            clearInterval(statusInterval);
            submitBtn.disabled = false;
            loader.hidden = true;
            statusContainer.hidden = true;
            btnText.style.opacity = '1';
        }
    });

    function displayResults(data, targetRole) {
        // Keep jobs visible as requested
        interimJobs.hidden = false;
        resultSection.hidden = false;

        // Update Score
        const score = data.score || 0;
        scoreText.textContent = `${score}%`;
        const dashArray = `${score}, 100`;
        scoreCircle.setAttribute('stroke-dasharray', dashArray);

        // Add Hybrid Label
        const existingLabel = document.getElementById('hybridLabel');
        if (!existingLabel) {
            const label = document.createElement('div');
            label.id = 'hybridLabel';
            label.style.fontSize = '0.7rem';
            label.style.color = 'var(--primary)';
            label.style.marginTop = '5px';
            label.style.fontWeight = '600';
            label.textContent = 'Hybrid AI-Verified';
            scoreCircle.parentElement.appendChild(label);
        }

        // Update Summary
        expValue.textContent = data.experience || 'N/A';
        fitValue.textContent = data.role_fit || 'N/A';
        projValue.textContent = data.projects || '0';

        // Update Skills
        skillsList.innerHTML = '';
        if (data.skills && data.skills.length) {
            data.skills.forEach((skill, index) => {
                const tag = document.createElement('span');
                tag.className = 'skill-tag';
                tag.textContent = skill;
                tag.style.animationDelay = `${index * 0.1}s`;
                skillsList.appendChild(tag);
            });
        } else {
            skillsList.innerHTML = '<p class="file-hint">No technical skills detected</p>';
        }

        // Update Missing Skills
        missingSkillsList.innerHTML = '';
        if (data.missing_skills && data.missing_skills.length) {
            data.missing_skills.forEach((skill, index) => {
                const tag = document.createElement('span');
                tag.className = 'skill-tag missing';
                tag.textContent = skill;
                tag.style.animationDelay = `${(data.skills ? data.skills.length : 0) * 0.1 + index * 0.1}s`;
                missingSkillsList.appendChild(tag);
            });
        } else {
            missingSkillsList.innerHTML = '<p class="file-hint">No missing skills detected!</p>';
        }

        // --- NEW: Update AI Insights ---
        try {
            if (data.analysis) {
                const detailsGrid = document.querySelector('.details-grid');
                if (!detailsGrid) return;

                // Remove old insights
                document.querySelectorAll('.insight-card').forEach(card => card.remove());

                // 1. Summary Card
                const summaryCard = document.createElement('div');
                summaryCard.className = 'detail-card full-width insight-card';
                summaryCard.innerHTML = `
                    <h3><span class="icon">📝</span> AI Analysis Summary</h3>
                    <p style="line-height: 1.6; color: var(--text-main); font-size: 0.95rem;">${data.analysis.summary || 'Detailed analysis complete.'}</p>
                `;
                detailsGrid.prepend(summaryCard);

                // 2. Strengths & Soft Skills
                const insightsRow = document.createElement('div');
                insightsRow.className = 'detail-card full-width insight-card';
                insightsRow.style.display = 'grid';
                insightsRow.style.gridTemplateColumns = '1fr 1fr';
                insightsRow.style.gap = '20px';

                const strengths = Array.isArray(data.analysis.strengths) ? data.analysis.strengths : ["Technical Proficiency"];
                const softSkills = Array.isArray(data.analysis.soft_skills) ? data.analysis.soft_skills : ["Communication", "Reliability"];

                insightsRow.innerHTML = `
                    <div>
                        <h3><span class="icon">💪</span> Core Strengths</h3>
                        <ul style="color: var(--text-dim); padding-left: 20px;">
                            ${strengths.map(s => `<li style="margin-bottom: 8px;">${s}</li>`).join('')}
                        </ul>
                    </div>
                    <div>
                        <h3><span class="icon">🧠</span> Soft Skills</h3>
                        <div class="skills-wrap">
                            ${softSkills.map(s => `<span class="skill-tag" style="background: rgba(16, 185, 129, 0.1); color: #6ee7b7; border-color: rgba(16, 185, 129, 0.2);">${s}</span>`).join('')}
                        </div>
                    </div>
                `;
                detailsGrid.appendChild(insightsRow);

                // 3. Improvement Tips
                const tips = Array.isArray(data.analysis.improvement_tips) ? data.analysis.improvement_tips : ["Tailor keywords to job description"];
                const tipsCard = document.createElement('div');
                tipsCard.className = 'detail-card full-width insight-card';
                tipsCard.style.border = '1px solid var(--warning)';
                tipsCard.innerHTML = `
                    <h3><span class="icon">💡</span> How to Beat the ATS (Tips)</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                        ${tips.map(t => `
                            <div style="background: rgba(245, 158, 11, 0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.1);">
                                ${t}
                            </div>
                        `).join('')}
                    </div>
                `;
                detailsGrid.appendChild(tipsCard);
            }
        } catch (uiError) {
            console.error("UI Render Error:", uiError);
        }

        // Scroll to results
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
