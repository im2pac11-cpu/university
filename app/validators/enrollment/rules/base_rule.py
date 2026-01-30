class ValidationRule:
    """Base interface for all enrollment validation rules."""

    def validate(self, student_profile, course_group, semester, repo):
        raise NotImplementedError("Subclasses must implement validate method.")
