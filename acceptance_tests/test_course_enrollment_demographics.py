import datetime
from unittest import skipUnless
from bok_choy.web_app_test import WebAppTest

from analyticsclient.constants import demographic
from acceptance_tests import ENABLE_DEMOGRAPHICS_TESTS
from acceptance_tests.mixins import CourseDemographicsPageTestsMixin

from acceptance_tests.pages import CourseEnrollmentDemographicsAgePage, CourseEnrollmentDemographicsEducationPage, \
    CourseEnrollmentDemographicsGenderPage


_multiprocess_can_split_ = True


@skipUnless(ENABLE_DEMOGRAPHICS_TESTS, 'Demographics tests are not enabled.')
class CourseEnrollmentDemographicsAgeTests(CourseDemographicsPageTestsMixin, WebAppTest):
    help_path = 'enrollment/Demographics_Age.html'

    demographic_type = demographic.BIRTH_YEAR
    table_columns = ['Age', 'Number of Students', 'Percent of Total']

    def setUp(self):
        super(CourseEnrollmentDemographicsAgeTests, self).setUp()
        self.page = CourseEnrollmentDemographicsAgePage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)
        self.demographic_data = sorted(self.course.enrollment(self.demographic_type),
                                       key=lambda item: item['count'], reverse=True)

    def test_page(self):
        super(CourseEnrollmentDemographicsAgeTests, self).test_page()
        self._test_metrics()

    def _calculate_median_age(self, current_year):
        total_enrollment = sum([datum['count'] for datum in self.demographic_data])
        half_enrollments = total_enrollment * 0.5
        count_enrollments = 0

        sorted_by_year = sorted(self.course.enrollment(self.demographic_type),
                                key=lambda item: item['birth_year'], reverse=False)

        for index, datum in enumerate(sorted_by_year):
            age = current_year - datum['birth_year']
            count_enrollments += datum['count']

            if count_enrollments > half_enrollments:
                return age
            elif count_enrollments == half_enrollments:
                if total_enrollment % 2 == 0:
                    next_age = current_year - sorted_by_year[index + 1]['birth_year']
                    return (next_age + age) * 0.5
                else:
                    return age

        return None

    def _count_ages(self, current_year, min_age, max_age):
        """
        Returns the number of enrollments between min_age (exclusive) and
        max_age (inclusive).
        """
        filtered_ages = self.demographic_data

        if min_age:
            filtered_ages = ([datum for datum in filtered_ages
                              if (current_year - datum['birth_year']) > min_age])
        if max_age:
            filtered_ages = ([datum for datum in filtered_ages
                              if (current_year - datum['birth_year']) <= max_age])

        return sum([datum['count'] for datum in filtered_ages])

    def _test_metrics(self):
        current_year = datetime.date.today().year
        total = float(sum([datum['count'] for datum in self.demographic_data]))
        age_metrics = [
            {
                'stat_type': 'median_age',
                'value': self._calculate_median_age(current_year)
            },
            {
                'stat_type': 'enrollment_age_under_25',
                'value': self.build_display_percentage(self._count_ages(current_year, None, 25), total)
            },
            {
                'stat_type': 'enrollment_age_between_26_40',
                'value': self.build_display_percentage(self._count_ages(current_year, 26, 40), total)
            },
            {
                'stat_type': 'enrollment_age_over_40',
                'value': self.build_display_percentage(self._count_ages(current_year, 40, None), total)
            }
        ]

        for metric in age_metrics:
            selector = 'data-stat-type={}'.format(metric['stat_type'])
            self.assertSummaryPointValueEquals(selector, unicode(str(metric['value'])))

    def _test_table_row(self, datum, column, sum_count):
        expected_percent_display = self.build_display_percentage(datum['count'], sum_count)
        # it's difficult to test the actual age in the case of a tie, so leave out (unit tests should catch this)
        expected = [unicode(datum['count']), unicode(expected_percent_display)]
        actual = [column[1].text, column[2].text]
        self.assertListEqual(actual, expected)
        self.assertIn('text-right', column[1].get_attribute('class'))
        self.assertIn('text-right', column[2].get_attribute('class'))


@skipUnless(ENABLE_DEMOGRAPHICS_TESTS, 'Demographics tests are not enabled.')
class CourseEnrollmentDemographicsGenderTests(CourseDemographicsPageTestsMixin, WebAppTest):
    help_path = 'enrollment/Demographics_Gender.html'

    demographic_type = demographic.GENDER
    table_columns = ['Date', 'Total Enrollment', 'Female', 'Male', 'Other', 'Not Reported']

    def setUp(self):
        super(CourseEnrollmentDemographicsGenderTests, self).setUp()
        self.page = CourseEnrollmentDemographicsGenderPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)

        end_date = datetime.datetime.utcnow()
        end_date_string = end_date.strftime(self.api_client.DATE_FORMAT)
        response = self.course.enrollment(self.demographic_type, end_date=end_date_string)
        self.demographic_data = sorted(response, key=lambda x: datetime.datetime.strptime(x['date'], '%Y-%m-%d'),
                                       reverse=True)

    def _test_table_row(self, datum, column, sum_count):
        expected_date = datetime.datetime.strptime(datum['date'], self.api_date_format).strftime(
            "%B %d, %Y").replace(' 0', ' ')
        gender_total = sum([value for key, value in datum.iteritems() if
                            value and key in ['female', 'male', 'other', 'unknown']])
        expected = [unicode(expected_date), unicode(gender_total), unicode(datum.get('female', 0)),
                    unicode(datum.get('male', 0)), unicode(datum.get('other', 0)), unicode(datum.get('u', 0))]
        actual = [column[0].text, column[1].text, column[2].text, column[3].text, column[4].text, column[5].text]
        self.assertListEqual(actual, expected)
        for i in range(1, 6):
            self.assertIn('text-right', column[i].get_attribute('class'))


@skipUnless(ENABLE_DEMOGRAPHICS_TESTS, 'Demographics tests are not enabled.')
class CourseEnrollmentDemographicsEducationTests(CourseDemographicsPageTestsMixin, WebAppTest):
    help_path = 'enrollment/Demographics_Education.html'

    demographic_type = demographic.EDUCATION
    table_columns = ['Educational Background', 'Number of Students']

    def setUp(self):
        super(CourseEnrollmentDemographicsEducationTests, self).setUp()
        self.page = CourseEnrollmentDemographicsEducationPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)
        self.demographic_data = sorted(self.course.enrollment(self.demographic_type),
                                       key=lambda item: item['count'], reverse=True)

    def test_page(self):
        super(CourseEnrollmentDemographicsEducationTests, self).test_page()
        self._test_metrics()

    def _test_metrics(self):
        total = self._get_total_demographics()
        education_groups = [
            {
                'levels': ['primary', 'junior_secondary', 'secondary'],
                'stat_type': 'education_high_school_or_less_enrollment'
            },
            {
                'levels': ['associates', 'bachelors'],
                'stat_type': 'education_college_enrollment'
            },
            {
                'levels': ['masters', 'doctorate'],
                'stat_type': 'education_advanced_enrollment'
            }
        ]

        for group in education_groups:
            selector = 'data-stat-type={}'.format(group['stat_type'])
            filtered_group = ([education for education in self.demographic_data
                               if education['education_level']['short_name'] in group['levels']])
            group_total = float(sum([datum['count'] for datum in filtered_group]))
            expected_percent_display = self.build_display_percentage(group_total, total)
            self.assertSummaryPointValueEquals(selector, expected_percent_display)

    def _test_table_row(self, datum, column, sum_count):
        expected = [datum['education_level']['name'],
                    unicode(datum['count'])]
        actual = [column[0].text, column[1].text]
        self.assertListEqual(actual, expected)
        self.assertIn('text-right', column[1].get_attribute('class'))