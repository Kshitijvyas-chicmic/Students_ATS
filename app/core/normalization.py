# app/core/normalization.py

SKILL_ALIASES = {
    # Programming Paradigms
    "oop": "object-oriented-programming",
    "oops": "object-oriented-programming",
    "object-oriented-programming": "object-oriented-programming",
    "functional-programming": "functional-programming",

    # Core CS
    "dsa": "data-structure-and-algorithm",
    "data-structures": "data-structure-and-algorithm",
    "algorithms": "data-structure-and-algorithm",
    "data-structures-and-algorithms": "data-structure-and-algorithm",
    "data-structure-and-algorithm": "data-structure-and-algorithm",
    "dbms": "database-management-system",

    # Languages
    "js": "javascript",
    "py": "python",
    "ts": "typescript",
    "cpp": "c++",
    "golang": "go",
    "react-js": "react",
    "reactjs": "react",
    "node-js": "node.js",
    "nodejs": "node.js",
    "vuejs": "vue.js",
    "angularjs": "angular",
    "react.js": "react",
    "node.js": "node.js",
    "fastapi": "fast-api",
    "fast-api": "fast-api",

    # Databases
    "postgres": "postgresql",
    "mongo": "mongodb",
    "mssql": "sql-server",
    "mysql": "mysql",

    # Tools & Tech
    "git-github": "git/github",
    "git": "git/github",
    "github": "git/github",
    "rest": "rest-api",
    "restful-api": "rest-api",
    "rest-apis": "rest-api",
    "restapi": "rest-api",
    "fastapi": "fast-api",
    "aws-cloud": "aws",
    "azure": "microsoft-azure",
    "gcp": "google-cloud-platform",
    "ml": "machine-learning",
    "ai": "artificial-intelligence",
}

def normalize_skill(skill) -> str:
    """Normalize skill name: lowercase, strip, replace spaces/slashes with dashes, and use alias."""
    if not skill:
        return ""
    
    # Ensure skill is a string (handles cases where LLM might return a dict or other type)
    if not isinstance(skill, str):
        if isinstance(skill, dict):
            # Try to extract name if it's a dictionary
            skill = skill.get("name") or skill.get("skill") or str(skill)
        else:
            skill = str(skill)
    
    # 1. Basic cleaning
    clean = skill.lower().strip()
    clean = clean.replace(" ", "-").replace("/", "-").replace("’", "'")
    
    # 2. Check Aliases
    return SKILL_ALIASES.get(clean, clean)

def normalize_skills_list(skills: list) -> list:
    """Normalize a list of skills, removing duplicates and empty strings."""
    if not skills:
        return []
    normalized = [normalize_skill(s) for s in skills if s]
    return list(set(filter(None, normalized)))
