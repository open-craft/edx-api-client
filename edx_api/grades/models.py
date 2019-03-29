"""
Business objects for the Grades API
"""

from __future__ import unicode_literals
from six import PY2, python_2_unicode_compatible

# pylint: disable=no-name-in-module, import-error
if PY2:
    from collections import Iterable
else:
    from collections.abc import Iterable
# pylint: enable=no-name-in-module, import-error


UNDEFINED = object()


# pylint: disable=too-few-public-methods

@python_2_unicode_compatible
class CurrentGrades(object):
    """
    Current Grades object representation

    restrict_to should be one of "username" or "course_id", and indicates that
    all contained CurrentGrade objects must have the same value for that
    field.
    """
    def __init__(self, current_grade_list, restrict_to="username"):
        if not isinstance(current_grade_list, Iterable):
            raise TypeError('CurrentGrades needs an Iterable object')
        self.current_grades = {}
        if restrict_to not in {"username", "course_id"}:
            raise ValueError("""restrict_to must be one of "username" or "course_id".""")
        self.restrict_to = restrict_to
        self.restricted_value = UNDEFINED
        for current_grade in current_grade_list:
            current_restricted_value = getattr(current_grade, restrict_to, None)
            if not isinstance(current_grade, CurrentGrade):
                raise ValueError("Only CurrentGrade objects are allowed")
            if self.restricted_value is UNDEFINED:
                self.restricted_value = current_restricted_value
            elif current_restricted_value != getattr(self, self.restrict_to):
                raise ValueError(
                    "Only CurrentGrade objects for the same {restrict_to} are allowed".format(
                        restrict_to=self.restrict_to
                    )
                )
            if self.restrict_to == 'username':
                key = current_grade.course_id
            else:
                key = current_grade.username
            self.current_grades[key] = current_grade

    def __str__(self):
        return "<Current Grades for {restrict_to} {restricted_value}>".format(
            restrict_to=self.restrict_to,
            restricted_value=self.restricted_value
        )

    @property
    def username(self):
        """
        If the current grades are restricted to a single username,
        return it, otherwise, return None.
        """
        if self.restrict_to == "username":
            return self.restricted_value
        else:
            return None

    @property
    def course_id(self):
        """
        If the current grades are restricted to a single course_id,
        return it, otherwise, return None.
        """

        if self.restrict_to == "course_id":
            return self.restricted_value
        else:
            return None

    @property
    def all_course_ids(self):
        """Helper property to return all the course ids of the current grades"""
        if self.restrict_to == "username":
            return self.current_grades.keys()
        else:
            return {self.course_id}

    @property
    def all_usernames(self):
        """Helper property to return all the usernames of the current grades"""
        if self.restrict_to == "course_id":
            return self.current_grades.keys()
        else:
            return {self.username}

    @property
    def all_current_grades(self):
        """Helper property to return all the CurrentGrade objects"""
        return self.current_grades.values()

    def get_current_grade(self, course_id):
        """Returns the current grade for the given course id"""
        return self.current_grades.get(course_id)


@python_2_unicode_compatible
class CurrentGrade(object):
    """
    Single current grade object representation
    """
    def __init__(self, json):
        self.json = json

    def __str__(self):
        return "<Current Grade for user {user} in course {course}>".format(
            user=self.username,
            course=self.course_id
        )

    @property
    def course_id(self):
        """Shortcut for a nested property"""
        return self.json.get('course_id')

    @property
    def email(self):
        """Returns email of the user"""
        return self.json.get('email')

    @property
    def username(self):
        """Returns the username of the user."""
        return self.json.get('username')

    @property
    def passed(self):
        """Whether the user has passed the course"""
        return self.json.get('passed')

    @property
    def percent(self):
        """
        Returns a decimal representation between
        0 and 1 of the student grade for the course
        """
        return self.json.get('percent')

    @property
    def letter_grade(self):
        """
        Returns a letter grade as defined in the
        edX grading_policy (e.g. 'A' 'B' 'C' for 6.002x) or None
        """
        return self.json.get('letter_grade')
