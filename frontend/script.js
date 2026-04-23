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

    // Fetch and populate available roles
    async function loadRoles() {
        try {
            const response = await fetch('/api/resume/roles');
            if (response.ok) {
                const roles = await response.json();
                roles.forEach(role => {
                    const option = document.createElement('option');
                    option.value = role;
                    option.textContent = role.charAt(0).toUpperCase() + role.slice(1);
                    targetRoleInput.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to load roles:', error);
        }
    }
    loadRoles();

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
        const expLevel = document.getElementById('expLevel').value;

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
            "AI Analysis is running! This will take a couple of minutes...",
            "While you wait, check the live job openings below!",
            "Searching LinkedIn, Indeed, and Naukri for active roles...",
            "Processing your resume with deep LLM logic...",
            "Almost there! Hang tight for your personalized report.",
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
        formData.append('exp_level', expLevel);

        try {
            const response = await fetch('/api/resume/analyze', {
                method: 'POST',
                credentials: 'include',
                body: formData
            });

            if (!response.ok) {
                // Handle BOTH 401 Unauthorized and 403 Forbidden
                if (response.status === 401 || response.status === 403) {
                    showLoginModal();
                    return;
                }
                throw new Error('Server error');
            }

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

    // Modal Logic
    const loginModal = document.getElementById('loginModal');
    const closeLoginBtn = document.getElementById('closeLoginBtn');

    function showLoginModal() {
        if (loginModal) {
            loginModal.style.display = 'flex';
            interimJobs.hidden = true; // Hide interim jobs if login required
        }
    }

    if (closeLoginBtn && loginModal) {
        closeLoginBtn.addEventListener('click', () => {
            loginModal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === loginModal) {
                loginModal.style.display = 'none';
            }
        });
    }

    // -- AUTH UI WIRING --
    const navLoginBtn = document.getElementById('navLoginBtn');
    const navRegisterBtn = document.getElementById('navRegisterBtn');
    const navLogoutBtn = document.getElementById('navLogoutBtn');
    const registerModal = document.getElementById('registerModal');
    const closeRegisterBtn = document.getElementById('closeRegisterBtn');

    async function checkAuthState() {
        try {
            const response = await fetch('/auth/me', {
                method: 'GET',
                credentials: 'include'
            });
            if (response.ok) {
                navLoginBtn.style.display = 'none';
                navRegisterBtn.style.display = 'none';
                navLogoutBtn.style.display = 'block';
                return true;
            }
        } catch (error) {
            console.error('Auth check failed:', error);
        }
        navLoginBtn.style.display = 'block';
        navRegisterBtn.style.display = 'block';
        navLogoutBtn.style.display = 'none';
        return false;
    }
    checkAuthState(); // Check on load

    if (navLoginBtn) navLoginBtn.addEventListener('click', showLoginModal);

    if (navLogoutBtn) {
        navLogoutBtn.addEventListener('click', async () => {
            try {
                await fetch('/auth/logout', {
                    method: 'POST',
                    credentials: 'include'
                });
            } catch (e) {
                console.error('Logout API error:', e);
            }
            checkAuthState();
            alert('Successfully logged out.');
        });
    }

    if (navRegisterBtn && registerModal) {
        navRegisterBtn.addEventListener('click', () => {
            registerModal.style.display = 'flex';
        });
    }

    if (closeRegisterBtn && registerModal) {
        closeRegisterBtn.addEventListener('click', () => {
            registerModal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === registerModal) {
                registerModal.style.display = 'none';
            }
        });
    }

    // -- FORM SUBMISSIONS --
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value;

            try {
                const res = await fetch('/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        userEmail_id: email,
                        userPassword: password
                    })
                });

                if (!res.ok) {
                    const errData = await res.json();
                    alert(errData.detail || 'Login failed. Check your credentials.');
                    return;
                }

                loginModal.style.display = 'none';
                loginForm.reset();
                await checkAuthState();
                alert('Login successful!');
            } catch (err) {
                console.error('Login error:', err);
                alert('Login failed. Make sure the backend is running.');
            }
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userName = document.getElementById('regUsername').value.trim();
            const userEmail_id = document.getElementById('regEmail').value.trim();
            const userPassword = document.getElementById('regPassword').value;
            const userPhoneNumber = document.getElementById('regPhone').value.trim();

            try {
                const res = await fetch('/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        userName,
                        userEmail_id,
                        userPassword,
                        userPhoneNumber
                    })
                });

                if (!res.ok) {
                    const errData = await res.json();
                    alert(errData.detail || 'Registration failed.');
                    return;
                }

                registerModal.style.display = 'none';
                registerForm.reset();
                showLoginModal();
                alert('Registration complete! Please log in now.');
            } catch (err) {
                console.error('Register error:', err);
                alert('Registration failed. Make sure the backend is running.');
            }
        });
    }

    // --- INTERVIEW LOGIC ---
    const startInterviewBtn = document.getElementById('startInterviewBtn');

    if (startInterviewBtn) {
        startInterviewBtn.addEventListener('click', async () => {
            // 1. Auth Check FIRST
            const isLoggedIn = await checkAuthState();
            if (!isLoggedIn) {
                showLoginModal();
                return;
            }

            const role = targetRoleInput.value;
            if (!role) {
                alert("Please select a target role first!");
                return;
            }

            // Open in new tab
            window.open(`interview.html?role=${encodeURIComponent(role)}`, '_blank');
        });
    }
});
