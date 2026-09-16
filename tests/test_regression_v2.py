import os
import sys
from pathlib import Path
from unittest.mock import patch
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
os.environ['MOCK_LLM'] = 'true'
from streamlit.testing.v1 import AppTest
from schemas.outputs import LearningAnswer

def check(app):
    assert not app.exception, str(app.exception)

def click(app, label):
    next(b for b in app.button if b.label == label).click().run()
    check(app)


import unittest

class RegressionTests(unittest.TestCase):
    def test_workflow(self):
        with patch('llm_client._request', side_effect=AssertionError('No automatic model calls')):
            app = AppTest.from_file(str(root / 'app.py'), default_timeout=30).run()
            check(app)
            click(app, 'DataTable 与写回')
            question = app.text_area(key='learn_question').value
            click(app, '查看相关资料')
            assert app.session_state['_learning_context']['question'] == question
            assert any('可供核对' in c.value for c in app.caption)
            assert any(e.label.startswith('01 ·') for e in app.expander)
            assert len(app.session_state['test_runs']) == 1
            app.button(key='learn_followup_example').click().run()
            check(app)
            assert question in app.text_area(key='learn_question').value
            assert '具体例子' in app.text_area(key='learn_question').value
            assert app.selectbox(key='learn_week').value == 2
            assert len(app.session_state['test_runs']) == 1
            click(app, 'DataTable 与写回')
            click(app, '查看相关资料')
            concept = app.session_state['learning'].key_concept
            run_count = len(app.session_state['test_runs'])
            app.button(key='learn_to_practice').click().run()
            check(app)
            assert app.radio(key='ui_active_module').value == 'generate'
            assert app.text_input(key='gen_topic').value == concept
            assert len(app.session_state['test_runs']) == run_count
            assert any(concept in i.value for i in app.info)
            app.radio(key='ui_active_module').set_value('learning').run()
            app.radio(key='ui_language_picker').set_value('en').run()
            check(app)
            click(app, 'DataTable & write-back')
            click(app, 'Find course materials')
            app.button(key='learn_followup_compare').click().run()
            check(app)
            assert 'Original question:' in app.text_area(key='learn_question').value
            assert 'distinguish' in app.text_area(key='learn_question').value
            unavailable = LearningAnswer(status='INSUFFICIENT_EVIDENCE', answer='No matching evidence.')
            with patch('modules.learning_explainer.answer_concept_question', return_value=unavailable):
                click(app, 'Find course materials')
            assert not any(b.key == 'learn_to_practice' for b in app.button)
            assert any('No source references' in c.value for c in app.caption)
        print('PASS: source cards, original-question context, follow-up draft and week, topic handoff, no auto requests, English actions, insufficient-evidence state.')
