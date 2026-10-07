import unittest
from streamlit.testing.v1 import AppTest

SCRIPT = '''
import streamlit as st
from types import SimpleNamespace
from game_builder import render_game_builder
class Query:
 def __init__(self): self.filters=[]; self.mode='read'; self.row=None
 def select(self,*a): return self
 def eq(self,k,v): self.filters.append((k,v)); return self
 def order(self,*a,**kw): return self
 def limit(self,*a): return self
 def insert(self,row): self.mode='insert'; self.row=row; return self
 def update(self,row): self.mode='update'; self.row=row; return self
 def execute(self):
  if self.mode=='read':
   assert ('user_id','00000000-0000-0000-0000-000000000001') in self.filters
   return SimpleNamespace(data=st.session_state.get('saved_games',[]))
  if self.mode=='insert':
   assert self.row['user_id']=='00000000-0000-0000-0000-000000000001'
   row=dict(self.row,id='11111111-1111-1111-1111-111111111111')
   st.session_state.saved_games=[row]
  else:
   assert ('user_id','00000000-0000-0000-0000-000000000001') in self.filters
   st.session_state.saved_games[0].update(self.row)
  return SimpleNamespace(data=st.session_state.saved_games)
class Client:
 def table(self,n):
  assert n=='jogos_criados'
  return Query()
render_game_builder('00000000-0000-0000-0000-000000000001',Client())
'''
class BuilderUI(unittest.TestCase):
 def test_create_memory_and_edit(self):
  app=AppTest.from_string(SCRIPT).run()
  self.assertFalse(app.exception)
  app.text_input[0].set_value('Meu jogo')
  app.button[0].click().run()
  self.assertFalse(app.exception)
  self.assertTrue(app.success)
  self.assertEqual(app.session_state['saved_games'][0]['content']['items'],['Luna','Coelho','Castelo'])
  app.run()
  app.selectbox[0].select('11111111-1111-1111-1111-111111111111').run()
  app.text_input[0].set_value('Meu jogo editado')
  app.button[0].click().run()
  self.assertFalse(app.exception)
  self.assertEqual(app.session_state['saved_games'][0]['title'],'Meu jogo editado')
 def test_quiz_create_and_invalid(self):
  app=AppTest.from_string(SCRIPT).run()
  app.selectbox[1].select('quiz').run()
  app.text_input[0].set_value('Quiz')
  app.button[0].click().run()
  self.assertTrue(app.warning)
  app.text_input[1].set_value('Quanto é 2 + 2?')
  app.text_input[2].set_value('3'); app.text_input[3].set_value('4'); app.text_input[4].set_value('5')
  app.radio[0].set_value(1)
  app.button[0].click().run()
  self.assertFalse(app.exception)
  self.assertTrue(app.success)
  self.assertEqual(app.session_state['saved_games'][0]['content']['questions'][0]['answer'],1)

if __name__=='__main__':unittest.main()
