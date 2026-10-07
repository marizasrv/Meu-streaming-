import unittest
from game_builder_core import validate_game, game_html

class GameTests(unittest.TestCase):
    def test_memory_normalization(self):
        g=validate_game(' Luna ','memory',{'items':[' Lua ','Sol','']})
        self.assertEqual(g['content']['items'],['Lua','Sol'])
    def test_memory_duplicates_and_limits(self):
        for items in [['Lua','lua'],['Lua'],['a'*41,'b'],list(map(str,range(13)))]:
            with self.assertRaises(ValueError): validate_game('X','memory',{'items':items})
    def test_quiz_answer_validation(self):
        with self.assertRaises(ValueError): validate_game('X','quiz',{'questions':[{'prompt':'Q','options':['A','B'],'answer':2}]})
        with self.assertRaises(ValueError): validate_game('X','quiz',{'questions':[{'prompt':'Q','options':['A','A'],'answer':0}]})
    def test_preview_does_not_embed_executable_user_html(self):
        markup=game_html({'title':'</script><script>alert(1)</script>','kind':'memory','content':{'items':['<img src=x onerror=alert(1)>','B']}})
        self.assertEqual(markup.count('</script>'),1)
        self.assertNotIn('<img src=x',markup)
    def test_unknown_kind(self):
        with self.assertRaises(ValueError): validate_game('X','javascript',{})

if __name__=='__main__': unittest.main()
