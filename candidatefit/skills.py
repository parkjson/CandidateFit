"""
skills.py
====================================
The skill vocabulary CandidateFit looks for in postings and resumes.

Each entry maps a display name to regex patterns. Patterns are matched
case-insensitively unless the name is listed in ``CASE_SENSITIVE``: short or
ambiguous names like "Go", "C" and "R" only count when written that way, so
"go to market" or "plan c" don't register as skills.
"""

SKILLS = {
    # Languages
    "Python": [r"python"],
    "Java": [r"java(?!\s*script)"],
    "JavaScript": [r"javascript", r"ecmascript", r"(?<!\.)js"],
    "TypeScript": [r"typescript"],
    "C": [r"(?<![\w+#.])C(?![\w+#])"],
    "C++": [r"c\+\+", r"cpp"],
    "C#": [r"c#", r"c\s*sharp"],
    "Go": [r"golang", r"(?<![\w.])Go(?=\s*[,/)]|\s+(?:and|or)\b|$)"],
    "Rust": [r"rust"],
    "Ruby": [r"ruby(?!\s+on\s+rails)"],
    "PHP": [r"php"],
    "Swift": [r"swift"],
    "Kotlin": [r"kotlin"],
    "Scala": [r"scala"],
    "R": [r"(?<![\w&])R(?![\w&])"],
    "MATLAB": [r"matlab"],
    "Bash": [r"bash", r"shell scripting"],
    "SQL": [r"sql(?!ite)"],
    "HTML": [r"html5?"],
    "CSS": [r"css3?"],
    # Web / frameworks
    "React": [r"react(?:\.js|js)?(?!\s+native)"],
    "React Native": [r"react\s+native"],
    "Angular": [r"angular(?:js)?"],
    "Vue": [r"vue(?:\.js|js)?"],
    "Node.js": [r"node\.?js"],
    "Express": [r"express(?:\.js|js)"],
    "Next.js": [r"next\.js", r"nextjs"],
    "Django": [r"django"],
    "Flask": [r"flask"],
    "FastAPI": [r"fastapi"],
    "Spring": [r"spring\s+(?:boot|framework|mvc|cloud)"],
    "Ruby on Rails": [r"ruby\s+on\s+rails"],
    ".NET": [r"\.net", r"asp\.net", r"dotnet"],
    "GraphQL": [r"graphql"],
    "REST APIs": [r"rest(?:ful)?(?:\s+apis?|\s+services?)", r"restful"],
    # Data / ML
    "Pandas": [r"pandas"],
    "NumPy": [r"numpy"],
    "scikit-learn": [r"scikit[\s-]?learn", r"sklearn"],
    "TensorFlow": [r"tensorflow"],
    "PyTorch": [r"pytorch"],
    "Machine Learning": [r"machine\s+learning", r"\bml\b"],
    "Deep Learning": [r"deep\s+learning"],
    "NLP": [r"nlp", r"natural\s+language\s+processing"],
    "LLMs": [r"llms?", r"large\s+language\s+models?"],
    "Data Analysis": [r"data\s+analysis", r"data\s+analytics"],
    "Spark": [r"(?:apache\s+)?spark", r"pyspark"],
    "Hadoop": [r"hadoop"],
    "Airflow": [r"airflow"],
    "Tableau": [r"tableau"],
    "Power BI": [r"power\s*bi"],
    "Excel": [r"(?:microsoft\s+|ms\s+)?excel(?!\s+(?:at|in)\b)"],
    # Databases
    "PostgreSQL": [r"postgres(?:ql)?"],
    "MySQL": [r"mysql"],
    "SQLite": [r"sqlite"],
    "MongoDB": [r"mongo(?:db)?"],
    "Redis": [r"redis"],
    "Elasticsearch": [r"elasticsearch", r"elastic\s+search"],
    "Snowflake": [r"snowflake"],
    "Databases": [r"databases?", r"database\s+platforms?"],
    # Cloud / DevOps
    "AWS": [r"aws", r"amazon\s+web\s+services"],
    "Azure": [r"azure"],
    "GCP": [r"gcp", r"google\s+cloud"],
    "Docker": [r"docker"],
    "Kubernetes": [r"kubernetes", r"k8s"],
    "Terraform": [r"terraform"],
    "CI/CD": [r"ci\s*/\s*cd", r"continuous\s+(?:integration|delivery|deployment)"],
    "GitHub Actions": [r"github\s+actions"],
    "Jenkins": [r"jenkins"],
    "Git": [r"git(?!hub|lab)"],
    "Linux": [r"linux", r"unix"],
    "Microservices": [r"micro[\s-]?services?"],
    "Distributed Systems": [r"distributed\s+systems?"],
    # Testing / QA
    "Test Automation": [
        r"test\s+automation",
        r"automated\s+test(?:s|ing)?",
        r"automate\s+tests",
    ],
    "Selenium": [r"selenium"],
    "pytest": [r"pytest"],
    "JUnit": [r"junit"],
    "Cypress": [r"cypress"],
    "Unit Testing": [r"unit\s+test(?:s|ing)?"],
    "QA": [r"\bqa\b", r"quality\s+assurance"],
    # Practices / other
    "Agile": [r"agile", r"scrum"],
    "Object-Oriented Programming": [r"object[\s-]oriented", r"\boop\b"],
    "Data Structures & Algorithms": [r"data\s+structures", r"algorithms"],
    "System Design": [r"system\s+design"],
    "Web Scraping": [r"web\s*scrap(?:e|ing)", r"beautifulsoup", r"bs4"],
    "Open Source": [r"open[\s-]source"],
    "Figma": [r"figma"],
    "iOS": [r"\bios\b"],
    "Android": [r"android"],
}

CASE_SENSITIVE = {"C", "Go", "R"}
