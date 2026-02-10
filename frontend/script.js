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

        // Status Messaging Logic
        const statusContainer = document.getElementById('statusContainer');
        const statusText = document.getElementById('statusText');
        statusContainer.hidden = false;

        const messages = [
            "Parsing your resume...",
            "Analyzing your experience...",
            "Extracting your skills...",
            "Comparing against target role...",
            "Identifying skill gaps...",
            "Generating recommendations...",
            "Finalizing your ATS score...",
            "Polishing the results..."
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
            displayResults(data);
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

    function displayResults(data) {
        resultSection.hidden = false;

        // Update Score
        const score = data.score || 0;
        scoreText.textContent = `${score}%`;
        const dashArray = `${score}, 100`;
        scoreCircle.setAttribute('stroke-dasharray', dashArray);

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

        // Update Recommendation
        try {
            const recommendationText = document.getElementById('recommendationText');
            if (recommendationText) {
                recommendationText.textContent = data.recommendation || 'No recommendation available.';
                recommendationText.classList.remove('file-hint');
            }
        } catch (e) { console.error("Error updating recommendation:", e); }

        // Update Job Links
        try {
            console.log("Job links data:", data.job_links);
            const jobLinksList = document.getElementById('jobLinksList');
            if (jobLinksList) {
                jobLinksList.innerHTML = '';
                if (data.job_links) {
                    const links = [
                        { id: 'linkedin', name: 'LinkedIn', icon: '🔗', url: data.job_links.linkedin_24h, class: 'linkedin' },
                        { id: 'indeed', name: 'Indeed', icon: '🔍', url: data.job_links.indeed_24h, class: 'indeed' },
                        { id: 'naukri', name: 'Naukri', icon: '💼', url: data.job_links.naukri, class: 'naukri' }
                    ];

                    links.forEach(link => {
                        const a = document.createElement('a');
                        a.href = link.url;
                        a.target = '_blank';
                        a.className = `job-link-btn ${link.class}`;
                        a.innerHTML = `
                            <span class="btn-icon">${link.icon}</span>
                            <span class="btn-name">${link.name} Jobs</span>
                        `;
                        jobLinksList.appendChild(a);
                    });
                } else {
                    jobLinksList.innerHTML = '<p class="file-hint">No job links generated. Check backend.</p>';
                }
            } else {
                console.error("Could not find jobLinksList element!");
            }
        } catch (e) {
            console.error("Error generating job links UI:", e);
        }

        // Scroll to results
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
