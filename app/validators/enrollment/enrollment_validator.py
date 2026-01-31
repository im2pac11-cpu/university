from .repository import EnrollmentRepository
from .rules.semester_rule import SemesterActiveRule
from .rules.duplicate_rule import DuplicateEnrollmentRule
from .rules.capacity_rule import CapacityRule
from .rules.total_units_rule import TotalUnitsRule

class EnrollmentValidator:
    """Runs all enrollment validation rules in order."""

    def __init__(self, repo=None):
        self.repo = repo or EnrollmentRepository()
        self.rules = [
            SemesterActiveRule(),
            DuplicateEnrollmentRule(),
            CapacityRule(),
            TotalUnitsRule(),
        ]

    def validate(self, student_profile, course_group, semester):
        """Run all rules and collect warnings (errors are raised immediately)."""
        all_warnings = []

        for rule in self.rules:
            result = rule.validate(student_profile, course_group, semester, self.repo)
            if isinstance(result, dict) and "warnings" in result:
                all_warnings.extend(result["warnings"])

        return {"warnings": all_warnings}
