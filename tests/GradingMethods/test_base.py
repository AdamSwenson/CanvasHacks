# """
# Created by adam on 3/15/20
# """
# __author__ = 'adam'
#
# from unittest import TestCase
#
# from CanvasHacks.GradingMethods.base import IGradingMethod
# from TestingBase import TestingBase
#
# if __name__ == '__main__':
#     pass
#
#
# class TestIGradingMethod( TestingBase ):
#     def setUp(self) -> None:
#         self.config_for_test()
#
#     def test_to_remove_no_stopwords( self ):
#         obj = IGradingMethod()
#         obj.count_stopwords = True
#         self.assertIn('.', obj.to_remove)
#         self.assertNotIn('the', obj.to_remove)
#
#     def test_to_remove_inc_stopwords( self ):
#         obj = IGradingMethod()
#         obj.count_stopwords = False
#         self.assertIn( '.', obj.to_remove )
#         self.assertIn( 'the', obj.to_remove )
#
#     def test_to_remove_count_stopwords_not_set( self ):
#         obj = IGradingMethod()
#         self.assertEqual([], obj.to_remove, "returns an empty list if attribute missing")
#
#
#     def test__determine_word_count( self ):
#         obj = IGradingMethod()
#         obj.count_stopwords = True
#         expected = self.fake.random.randint(1, 1000)
#         content = " ".join([ self.fake.word() for _ in range(0, expected)])
#
#         result = obj._determine_word_count(content)
#
#         self.assertEqual(expected, result, 'expected count returned')
#
