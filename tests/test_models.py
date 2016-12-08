from rets import models
import unittest
from rets.session import Session


class TesterWithSession(unittest.TestCase):
    # Provides a valid session object to be provided to the models during testing.
    def setUp(self):
        super(TesterWithSession, self).setUp()
        self.session = Session(login_url='http://rets.com/login.php', username='retsuser', version='1.7.2')


class RecordAndResultsTester(TesterWithSession):

    def setUp(self):
        super(RecordAndResultsTester, self).setUp()
        self.results = models.resultsset.ResultsSet()
        self.record = dict()
        self.record['myval'] = 'yourval'
        self.results.values.append(self.record)

        self.resource = 'Property'
        self.resource_class = 'RES'

        self.results.resource = self.resource
        self.results.resource_class = self.resource_class
        self.results.total_results_count = 10

    def test_results(self):
        self.assertEqual('<ResultsSet: 1 Found in Property:RES for None>', repr(self.results))
        self.assertIn(self.record, self.results.values)
        self.assertEqual(self.results.lists('myval'), ['yourval'])

        self.record['ListingPrice'] = 123000

        self.assertEqual(self.record['ListingPrice'], 123000)

        self.record['somefield'] = '****'
        self.assertTrue(self.record['somefield'] == self.results.restricted_indicator)

        self.assertEqual(self.results.unique('somefield'), ['****'])
        for result in self.results:
            self.assertIsNotNone(result)


class ObjectTester(unittest.TestCase):

    def test_methods(self):
        o = models.object.Object()
        o.content = [1, 2, 2, 2, 2]
        self.assertEqual(5, len(o))

        o.preferred = 0
        self.assertFalse(o.is_preferred())
        o.preferred = 1
        self.assertTrue(o.is_preferred())

        o.error = True
        self.assertTrue(o.is_error())
        o.error = False
        self.assertFalse(o.is_error())
