from dataclasses import dataclass, field, asdict
from typing import List
import json

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

    def to_json(self) -> str:
        def custom_asdict(obj):
            if isinstance(obj, (JobExperience, Education)):
                return {k: v for k, v in asdict(obj).items() if v is not None}
            return obj

        resume_dict = asdict(self, dict_factory=custom_asdict)
        return json.dumps(resume_dict, indent=2)