import os
import sys
from pathlib import Path
from unittest.mock import patch
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
os.environ['MOCK_LLM'] = 'true'
from streamlit.testing.v1 import AppTest
from schemas.outputs import DebugAnswer
from ui_debug import debug_observations

def check(app):
    assert not app.exception, str(app.exception)

def click(app, label):
    next(b for b in app.button if b.label == label).click().run()
    check(app)


import unittest

class RegressionTests(unittest.TestCase):
    def test_workflow(self):
        with patch('llm_client._request', side_effect=AssertionError('No real model calls')):
            app = AppTest.from_file(str(root / 'app.py'), default_timeout=30).run()
            app.radio(key='ui_active_module').set_value('practice').run()
            click(app, '查看相关资料')
            assert 'test_runs' not in app.session_state
            assert any('当前状态' in x.value for x in app.warning)
            app.radio(key='help_mode').set_value('Debug').run()
            click(app, '查看相关资料')
            assert len(app.warning) == 2
            assert 'test_runs' not in app.session_state
            click(app, '填入 Debug 示例')
            assert app.selectbox(key='build_week').value == 3
            assert app.text_area(key='debug_error').value == ''
            assert '没有报错' in app.text_area(key='debug_actual').value
            assert app.text_area(key='debug_expected').value
            click(app, '查看相关资料')
            assert len(app.session_state['test_runs']) == 1
            inp = app.session_state['test_runs'][-1]['input']
            assert '预期结果:' in inp['error_message'] and '实际结果:' in inp['error_message']
            assert '报错原文:' not in inp['error_message']
            assert any('当前为预览模式' in x.value for x in app.info)
            assert not any(x.value == '需要补充信息' for x in app.warning)
            assert any(x.label.startswith('01 ·') for x in app.expander)
            app.run()
            assert len(app.session_state['test_runs']) == 1
            answer = DebugAnswer(status='ANSWERED', diagnosis_type='WORKFLOW_LOGIC', possible_causes=[
                {'cause':'Check output placement', 'check':'Inspect loop placement', 'fix':'Move the write if confirmed', 'rationale':'Course task sequence'},
                {'cause':'Check row selection', 'check':'Inspect target row', 'fix':'Correct target if confirmed'}], verification='Run with two invoices and check both records remain.')
            with patch('modules.guided_practice.debug_workflow', return_value=answer) as debug:
                click(app, '查看相关资料')
                assert debug.call_count == 1
            assert any('检查确认后再修复' in x.value for x in app.markdown)
            assert any('修复后验证' in x.value for x in app.markdown)
            app.text_input(key='debug_activity').set_value('')
            click(app, '查看相关资料')
            assert 'build_result' not in app.session_state
            click(app, '填入下一步示例')
            assert app.radio(key='help_mode').value == '下一步'
            assert app.text_input(key='next_last').value
            click(app, '查看相关资料')
            assert app.session_state['test_runs'][-1]['task'] == 'next_step'
            app.radio(key='ui_language_picker').set_value('en').run()
            click(app, 'Fill Debug example')
            assert app.text_area(key='debug_expected').value.startswith('Keep')
            app.text_area(key='debug_actual').set_value('')
            app.text_area(key='debug_expected').set_value('')
            app.text_area(key='debug_error').set_value('Object reference not set to an instance of an object.')
            with patch('modules.guided_practice.debug_workflow', return_value=answer) as debug:
                click(app, 'Find course materials')
                assert debug.call_count == 1
                assert debug.call_args.kwargs['error_message'].startswith('Exact error:')
            assert debug_observations('x'*1000, 'x'*4500, 'x'*6000, 'en').__len__() < 12000
        print('PASS: missing input blocks calls, no-error example, structured payload, sources, no duplicate calls, conditional repair and verification, stale-result clearing, next-step example, English error-only submission, payload length.')
