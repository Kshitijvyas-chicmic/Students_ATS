# Skill Database for Deterministic Keyword Matching
SKILL_DB = {
    "languages": [
        "python", "javascript", "java", "c++", "c#", "ruby", "php", "swift", "kotlin", "go", "rust", "typescript", "html", "css", "sql", "r", "scala"
    ],
    "frontend": [
        "react", "angular", "vue", "next.js", "tailwind", "bootstrap", "sass", "redux", "webpack", "svelte"
    ],
    "backend": [
        "node", "express", "django", "flask", "fastapi", "spring boot", "laravel", "asp.net", "rails", "nest.js"
    ],
    "data_science": [
        "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "tensorflow", "pytorch", "keras", "nlp", "opencv", "spark"
    ],
    "database": [
        "postgresql", "mysql", "mongodb", "redis", "oracle", "sqlite", "mariadb", "cassandra", "dynamodb"
    ],
    "cloud_devops": [
        "aws", "azure", "google cloud", "docker", "kubernetes", "jenkins", "terraform", "ansible", "git", "github", "gitlab", "bitbucket", "linux", "nginx"
    ],
    "tools": [
        "jira", "trello", "confluence", "postman", "swagger", "figma", "unity", "unreal engine"
    ]
}

# Role Requirements Mapping (Determines what skills are "Required" for scoring)
ROLE_REQUIREMENTS = {
    "java developer": {
        "must_have": ["java", "spring boot", "sql", "git"],
        "good_to_have": ["aws", "docker", "microservices", "hibernate"],
        "min_exp": 1
    },
    "python developer": {
        "must_have": ["python", "django", "flask", "fastapi", "sql"],
        "good_to_have": ["aws", "docker", "celery", "redis"],
        "min_exp": 1
    },
    "frontend developer": {
        "must_have": ["javascript", "react", "html", "css", "git"],
        "good_to_have": ["typescript", "next.js", "tailwind", "redux"],
        "min_exp": 1
    },
    "fullstack developer": {
        "must_have": ["javascript", "node", "react", "sql", "git"],
        "good_to_have": ["aws", "docker", "typescript", "mongodb"],
        "min_exp": 2
    },
    "data scientist": {
        "must_have": ["python", "pandas", "numpy", "sql", "scikit-learn"],
        "good_to_have": ["tensorflow", "pytorch", "nlp", "tableau"],
        "min_exp": 1
    },
    "default": {
        "must_have": ["git", "communication", "problem solving"],
        "good_to_have": [],
        "min_exp": 0
    }
}
