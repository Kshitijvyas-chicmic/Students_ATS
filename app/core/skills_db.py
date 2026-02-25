# app/core/skills_db.py

ROLE_REQUIREMENTS = {
    "java backend developer": {
        "skills": {
            "java": 15,
            "spring-boot": 15,
            "rest-api": 10,
            "postgresql": 10,
            "git/github": 10,
            "aws": 5,
            "docker": 5,
            "microservices": 5,
            "kafka": 5,
            "junit": 5,
            "ci/cd": 5
        },
        "min_exp": 2
    },

    "frontend developer": {
        "skills": {
            "javascript": 15,
            "react": 15,
            "html": 10,
            "css": 10,
            "typescript": 5,
            "redux": 5,
            "tailwindcss": 5,
            "webpack": 5,
            "git/github": 5,
            "postman": 5
        },
        "min_exp": 1
    },

    "fullstack developer": {
        "skills": {
            "javascript": 10,
            "react": 10,
            "java": 10,
            "spring-boot": 10,
            "git/github": 10,
            "postgresql": 5,
            "docker": 5,
            "aws": 5,
            "ci/cd": 5
        },
        "min_exp": 2
    },

    "data scientist": {
        "skills": {
            "python": 15,
            "pandas": 10,
            "numpy": 10,
            "scikit-learn": 10,
            "matplotlib": 5,
            "tensorflow": 5,
            "pytorch": 5,
            "sql": 5,
            "aws": 5
        },
        "min_exp": 1
    },

    "python backend developer": {
        "skills": {
            "python": 15,
            "django": 15,
            "fastapi": 10,
            "rest-api": 10,
            "postgresql": 10,
            "docker": 5,
            "aws": 5,
            "git/github": 5,
            "celery": 5,
            "redis": 5
        },
        "min_exp": 2
    },

    "devops engineer": {
        "skills": {
            "aws": 15,
            "docker": 15,
            "kubernetes": 15,
            "ci/cd": 10,
            "terraform": 10,
            "linux": 10,
            "jenkins": 5,
            "ansible": 5,
            "monitoring": 5,
            "bash": 5
        },
        "min_exp": 2
    },

    "machine learning engineer": {
        "skills": {
            "python": 15,
            "scikit-learn": 10,
            "tensorflow": 10,
            "pytorch": 10,
            "mlops": 10,
            "aws": 5,
            "docker": 5,
            "sql": 5,
            "data-preprocessing": 5,
            "model-deployment": 5
        },
        "min_exp": 2
    },

    "android developer": {
        "skills": {
            "java": 15,
            "kotlin": 15,
            "android-sdk": 10,
            "firebase": 10,
            "rest-api": 10,
            "git/github": 5,
            "mvvm": 5,
            "room-db": 5,
            "ui/ux": 5
        },
        "min_exp": 1
    },

    "ios developer": {
        "skills": {
            "swift": 15,
            "objective-c": 10,
            "ios-sdk": 10,
            "firebase": 10,
            "rest-api": 10,
            "git/github": 5,
            "coredata": 5,
            "mvvm": 5,
            "ui/ux": 5
        },
        "min_exp": 1
    },

    "qa engineer": {
        "skills": {
            "selenium": 15,
            "manual-testing": 15,
            "automation-testing": 10,
            "postman": 10,
            "junit": 5,
            "testng": 5,
            "ci/cd": 5,
            "bug-tracking": 5,
            "api-testing": 5
        },
        "min_exp": 1
    },

    "ui/ux designer": {
        "skills": {
            "figma": 20,
            "adobe-xd": 15,
            "wireframing": 15,
            "prototyping": 10,
            "user-research": 10,
            "interaction-design": 10,
            "design-systems": 10,
            "usability-testing": 10
        },
        "min_exp": 1
    },
    "backend developer": {
        "skills": {
            "java": 10,
            "python": 10,
            "nodejs": 10,
            "spring-boot": 10,
            "expressjs": 10,
            "rest-api": 10,
            "postgresql": 10,
            "mongodb": 5,
            "redis": 5,
            "docker": 5,
            "aws": 5,
            "git/github": 5,
            "ci/cd": 5
        },
        "min_exp": 1
    },
    "default": {
        "skills": {},
        "min_exp": 1
    }
}