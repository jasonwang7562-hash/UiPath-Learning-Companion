import os
import sys
from pathlib import Path
from unittest.mock import patch

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
os.environ['MOCK_LLM'] = 'true'
from streamlit.testing.v1 import AppTest
import config

def check(app):
    assert not app.exception, str(app.exception)
    assert not app.session_state.filtered_state.get('test_runs')


import unittest

class RegressionTests(unittest.TestCase):
    def test_workflow(self):
        with patch('llm_client._request', side_effect=AssertionError('Help must not call model')) as request:
            for language in ['zh', 'en']:
                app = AppTest.from_file(str(root / 'app.py'), default_timeout=30).run()
                app.radio(key='ui_language_picker').set_value(language).run()
                for module, examples in [('learning', ['learning']), ('practice', ['next_step', 'debug']), ('generate', ['generate', 'explain'])]:
                    app.radio(key='ui_active_module').set_value(module).run()
                    check(app)
                    for example in examples:
                        app.button(key='help_example_' + example).click().run()
                        check(app)
                        state = app.session_state.filtered_state
                        if example == 'learning':
                            assert app.text_area(key='learn_question').value
                        elif example == 'debug':
                            assert app.text_area(key='debug_actual').value
                            assert not app.text_area(key='debug_error').value
                        elif example == 'generate':
                            assert app.text_input(key='gen_topic').value
                        elif example == 'explain':
                            assert state.get('question')
                assert any('只能看资料' in x.label or 'only preview' in x.label for x in app.expander)
            with patch.object(config, 'MOCK_LLM', False):
                app.run()
                check(app)
                assert any(x.label == 'What if a request fails?' for x in app.expander)
            request.assert_not_called()
        print('PASS: contextual help and all five examples in Chinese/English; no automatic submission or model calls; preview/model FAQ wording.')
