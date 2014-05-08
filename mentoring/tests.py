from directory.models import Expertise
from directory.tests.test_views import WnycTestCase

class MentoringTests(WnycTestCase):
    def setUp(self):
        WnycTestCase.setUp(self)
        Expertise(category='other',
                  details='I am awesome',
                  user=self.wnyc_member).save()

    def test_index_lists_mentor_counts(self):
        self.login_as_wnyc_member()
        response = self.client.get('/mentoring/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1 mentor')
        self.assertContains(response, '0 mentors')

    def test_category_page_lists_mentors(self):
        self.login_as_wnyc_member()
        response = self.client.get('/mentoring/other/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Brian Lehrer')

    def test_nonmembers_are_denied(self):
        self.assertNonMembersAreDenied('/mentoring/')
        self.assertNonMembersAreDenied('/mentoring/other/')
