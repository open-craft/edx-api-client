"""Models Tests for the Grades API"""

import json
import os.path
from copy import deepcopy
from unittest import TestCase

from .models import (
    CurrentGrade,
    CurrentGrades,
)


class CurrentGradesTests(TestCase):
    """Tests for current grades object"""
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(os.path.dirname(__file__),
                               'fixtures/current_grades.json')) as file_obj:
            cls.grades_json = json.loads(file_obj.read())

        cls.current_grades = CurrentGrades([CurrentGrade(json_obj) for json_obj in cls.grades_json])

    def test_str(self):
        """Test the __str__"""
        assert str(self.current_grades) == "<Current Grades for username bob>"

    def test_expected_iterable(self):
        """CurrentGrades expects an iterable as input"""
        with self.assertRaises(TypeError):
            CurrentGrades(123)

    def test_only_same_user_grades(self):
        """CurrentGrades can contain only grades for the same user"""
        grades_json = deepcopy(self.grades_json)
        grades_json[0]['username'] = 'other_random_string'
        with self.assertRaises(ValueError):
            CurrentGrades([CurrentGrade(json_obj) for json_obj in grades_json])

    def test_only_same_course_grades(self):
        """
        CurrentGrades can be restricted to only contain grades from a single course_id.
        """
        with self.assertRaises(ValueError):
            CurrentGrades(
                [CurrentGrade(json_obj) for json_obj in self.grades_json],
                restrict_to='course_id',
            )

    def test_different_usernames(self):
        """
        When restrict_to is "course_id", grades can have different users.
        """
        grades_json = deepcopy(self.grades_json)
        for grade in grades_json:
            grade['course_id'] = grades_json[0]['course_id']
        grades_json[0]['username'] = 'different_username'
        # No exception raised
        CurrentGrades(
            [CurrentGrade(json_obj) for json_obj in grades_json],
            restrict_to="course_id",
        )

    def test_currentgrade_objects(self):
        """CurrentGrades can contain only CurrentGrade objects"""
        with self.assertRaises(ValueError):
            CurrentGrades([{'foo': 'bar'}])

    def test_all_course_ids(self):
        """Test for all_course_ids property"""
        assert set(self.current_grades.all_course_ids) == {
            "course-v1:edX+DemoX+Demo_Course", "course-v1:MITx+8.MechCX+2014_T1"
        }
        assert set(self.current_grades.all_usernames) == {"bob"}

    def test_all_usernames(self):
        """Test all_course_ids and all_usernames for CurrentGrades restricted to a course_id"""
        grades_json = deepcopy(self.grades_json)
        for grade in grades_json:
            grade['course_id'] = grades_json[0]['course_id']
        grades_json[0]['username'] = 'different_username'
        current_grades = CurrentGrades(
            [CurrentGrade(json_obj) for json_obj in grades_json],
            restrict_to="course_id",
        )
        assert set(current_grades.all_course_ids) == {"course-v1:edX+DemoX+Demo_Course"}
        assert set(current_grades.all_usernames) == {"bob", "different_username"}

    def test_all_current_grades(self):
        """Test for all_current_grades property"""
        all_grades = self.current_grades.all_current_grades
        assert len(all_grades) == 2
        for grade in all_grades:
            assert isinstance(grade, CurrentGrade)

    def test_get_current_grade(self):
        """Test for get_current_grade method"""
        course_grade = self.current_grades.get_current_grade("course-v1:edX+DemoX+Demo_Course")
        assert isinstance(course_grade, CurrentGrade)
        assert course_grade.course_id == "course-v1:edX+DemoX+Demo_Course"

    def test_restrict_to_values(self):
        """restrict_to must be one of username or course_id"""
        with self.assertRaises(ValueError):
            CurrentGrades(self.grades_json, restrict_to="email")

    def test_restrict_to_username(self):
        """
        when restrict_to is set to username, the username attr is set
        and the course_id attr is None
        """

        assert self.current_grades.username == "bob"
        assert self.current_grades.course_id is None

    def test_restrict_to_course_id(self):
        """
        when restrict_to is set to course_id, the course_id attr is set
        and the username attr is None
        """
        grades_json = deepcopy(self.grades_json)
        for each in grades_json:
            # All entries must have the same course_id
            each["course_id"] = grades_json[0]["course_id"]
        grades = CurrentGrades(
            [CurrentGrade(json_obj) for json_obj in grades_json],
            restrict_to="course_id",
        )
        assert grades.course_id == "course-v1:edX+DemoX+Demo_Course"
        assert grades.username is None


class CurrentGradeTests(TestCase):
    """Tests for current grade object"""
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(os.path.dirname(__file__),
                               'fixtures/current_grades.json')) as file_obj:
            cls.grades_json = json.loads(file_obj.read())

        cls.current_grade = CurrentGrade(cls.grades_json[0])

    def test_str(self):
        """Test the __str__"""
        assert str(self.current_grade) == ("<Current Grade for user bob in "
                                           "course course-v1:edX+DemoX+Demo_Course>")

    def test_course_id(self):
        """Test for course_id property"""
        assert self.current_grade.course_id == "course-v1:edX+DemoX+Demo_Course"

    def test_email(self):
        """Test for email property"""
        assert self.current_grade.email == "bob@example.com"

    def test_username(self):
        """Test for user property"""
        assert self.current_grade.username == "bob"

    def test_passed(self):
        """Test for passed property"""
        assert self.current_grade.passed is True

    def test_percent(self):
        """Test for percent property"""
        assert self.current_grade.percent == 0.97

    def test_letter_grade(self):
        """Test for letter_grade property"""
        assert self.current_grade.letter_grade == "Pass"
