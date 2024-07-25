from dataclasses import dataclass, field
from typing import List

@dataclass
class JobExperience:
    title: str
    company_name: str
    description: str
    start_date: str
    end_date: str

@dataclass
class Education:
    school: str
    major: str
    degree: str
    start_date: str
    end_date: str

@dataclass
class Resume:
    skills: List[str] = field(default_factory=list)
    work_experience: List[JobExperience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)