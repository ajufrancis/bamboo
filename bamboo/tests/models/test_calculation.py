from nose.tools import assert_raises
from pymongo.cursor import Cursor

from bamboo.core.parser import ParseError
from bamboo.models.calculation import Calculation
from bamboo.models.dataset import Dataset
from bamboo.models.observation import Observation
from bamboo.tests.test_base import TestBase


class TestCalculation(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self.dataset = Dataset()
        self.dataset.save(self.test_dataset_ids['good_eats.csv'])
        self.formula = 'rating'
        self.name = 'test'

    def _save_observations(self):
        Observation().save(self.test_data['good_eats.csv'], self.dataset)

    def _save_observations_and_calculation(self, formula=None):
        if not formula:
            formula = self.formula
        self._save_observations()
        return Calculation.create(self.dataset, formula, self.name)

    def test_save(self):
        record = self._save_observations_and_calculation()
        self.assertTrue(isinstance(record, dict))
        self.assertTrue(Calculation.FORMULA in record.keys())

    def test_save_improper_formula(self):
        assert_raises(ParseError, self._save_observations_and_calculation, 'NON_EXISTENT_COLUMN')
        try:
            self._save_observations_and_calculation('NON_EXISTENT_COLUMN')
        except ParseError as e:
            self.assertTrue('Missing column' in e.__str__())

    def test_save_unparsable_formula(self):
        assert_raises(ParseError, self._save_observations_and_calculation, '=NON_EXISTENT_COLUMN')
        try:
            self._save_observations_and_calculation(
            '=NON_EXISTENT_COLUMN')
        except ParseError as e:
            self.assertTrue('Parse Failure' in e.__str__())

    def test_save_improper_formula_no_data(self):
        assert_raises(ParseError, Calculation().save, self.dataset,
                      'NON_EXISTENT_COLUMN', self.name)
        try:
            Calculation().save(self.dataset, 'NON_EXISTENT_COLUMN',
                               self.name)
        except ParseError as e:
            self.assertTrue('Missing column' in e.__str__())

    def test_save_unparsable_formula_no_data(self):
        assert_raises(ParseError, Calculation().save, self.dataset,
                      '=NON_EXISTENT_COLUMN', self.name)
        try:
            Calculation().save(self.dataset, '=NON_EXISTENT_COLUMN',
                               self.name)
        except ParseError as e:
            self.assertTrue('Parse Failure' in e.__str__())

    def test_save_non_existent_group(self):
        self._save_observations()
        assert_raises(ParseError, Calculation().save, self.dataset,
                      self.formula, self.name, group='NON_EXISTENT_GROUP')
        try:
            Calculation().save(self.dataset, self.formula, self.name,
                               group='NON_EXISTENT_GROUP')
        except ParseError as e:
            self.assertTrue('Group' in e.__str__())

    def test_find(self):
        record = self._save_observations_and_calculation()
        rows = Calculation.find(self.dataset)
        self.assertEqual(record, rows[0].record)
