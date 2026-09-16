import streamlit as st
from html import escape

import config
from modules.learning_explainer import answer_concept_question
from modules.guided_practice import get_next_step, debug_workflow
from modules.assessment_coach import generate_question, explain_question
from modules.common import evidence_for
from retrieval.retriever import load, by_ids, exercise_catalog
import ui_examples
from ui_locale import (
    DEFAULT_LANGUAGE,
    LANGUAGE_LABELS,
    MODE_LABELS,
    STATUS_LABELS,
    DIAGNOSIS_LABELS,
    TASK_LABELS,
    STAGE_LABELS,
    tr,
)
from ui_theme import apply_theme, render_footer, render_header, render_sidebar_brand, render_library_counts
from ui_runs import run_test, export_json, export_markdown
from ui_learning import render_learning_sources, unique_evidence, followup_prompt
from ui_debug import debug_observations, missing_debug_fields
from ui_help import render_help


def current_language():
    lang = st.session_state.get('ui_language', config.UI_LANGUAGE or DEFAULT_LANGUAGE)
    return lang if lang in LANGUAGE_LABELS else DEFAULT_LANGUAGE


def set_language(language):
    st.session_state.ui_language = language


ACTIVE_MODULE_KEY = 'ui_active_module'

MODULE_STATE_KEYS = {
    'learning': ['learn_question', 'learn_week', 'learn_depth', 'learning'],
    'practice': ['build_week', 'help_mode', 'build_result', 'next_last', 'next_state',
                 'debug_activity', 'debug_error', 'debug_change', 'debug_expected', 'debug_actual'],
    'generate': ['gen_topic', 'gen_difficulty', 'gen_type', 'question', 'assessment_result',
                 'example_question'],
}

GLOBAL_STATE_KEYS = {'ui_language', 'ui_language_picker', ACTIVE_MODULE_KEY}


def set_active_module(module):
    st.session_state[ACTIVE_MODULE_KEY] = module


def infer_active_module():
    scores = {}
    for module, keys in MODULE_STATE_KEYS.items():
        score = sum(1 for key in keys if st.session_state.get(key) not in (None, '', [], {}))
        scores[module] = score
    best = max(scores.values(), default=0)
    if best > 0:
        tied = [module for module, score in scores.items() if score == best]
        stored = st.session_state.get(ACTIVE_MODULE_KEY)
        if stored in tied:
            return stored
        for module in ('learning', 'practice', 'generate'):
            if module in tied:
                return module
    return st.session_state.get(ACTIVE_MODULE_KEY, 'learning')


def clear_module_state(module):
    keep = set(GLOBAL_STATE_KEYS)
    for key in list(st.session_state.keys()):
        if key in keep:
            continue
        if key.startswith('choice_'):
            st.session_state.pop(key, None)
            continue
        if key.startswith('exercise_'):
            st.session_state.pop(key, None)
            continue
        if any(key in keys for keys in MODULE_STATE_KEYS.values()):
            st.session_state.pop(key, None)
            continue
        if key in {'test_runs', 'export_selection'}:
            st.session_state.pop(key, None)


def handle_language_change():
    active_module = infer_active_module()
    st.session_state.ui_language = st.session_state.ui_language_picker
    st.session_state[ACTIVE_MODULE_KEY] = active_module
    clear_module_state(active_module)


def mode_options(language):
    return [MODE_LABELS[language]['next_step'], MODE_LABELS[language]['debug']]


def mode_key(language, value):
    return value == MODE_LABELS[language]['debug']


st.set_page_config(page_title='PE6202 UiPath Learning Companion', layout='wide')
apply_theme()

if 'ui_language' not in st.session_state:
    set_language(config.UI_LANGUAGE if config.UI_LANGUAGE in LANGUAGE_LABELS else DEFAULT_LANGUAGE)

lang = current_language()

render_header(lang, config.MOCK_LLM)
with st.sidebar:
    render_sidebar_brand(lang)
    chosen_language = st.radio(
        '界面语言' if lang == 'zh' else 'Interface language',
        options=list(LANGUAGE_LABELS),
        format_func=lambda code: LANGUAGE_LABELS[code],
        index=list(LANGUAGE_LABELS).index(lang),
        key='ui_language_picker',
        on_change=handle_language_change,
    )

lang = current_language()

if not config.MOCK_LLM:
    st.info(tr(lang, 'real_model_info', model=config.LLM_MODEL))


def attempt(task, function, **inputs):
    with st.status(tr(lang, 'checking_input'), expanded=False) as indicator:
        def progress(event):
            label = STAGE_LABELS[lang].get(event['kind'])
            if label:
                if event['kind'] == 'model_request' and event.get('mock'):
                    label = tr(lang, 'demo_mode_ready')
                indicator.update(label=label + '…')

        result, row = run_test(task, function, inputs, progress, language=lang)
        label = tr(lang, 'request_failed') if row['error'] else tr(lang, 'processing_complete')
        indicator.update(
            label=f"{label} · {tr(lang, 'elapsed', seconds=row['elapsed_seconds'])}",
            state='error' if row['error'] else 'complete',
            expanded=False,
        )
    history = st.session_state.setdefault('test_runs', [])
    history.append(row)
    st.session_state.test_runs = history[-50:]
    if row['error']:
        st.error(row['error']['message'])
    return result


def fill_example(name):
    if name == 'learning':
        set_active_module('learning')
    elif name in {'next_step', 'debug'}:
        set_active_module('practice')
    else:
        set_active_module('generate')
    examples = ui_examples.examples(lang)
    if name == 'explain':
        q = ui_examples.explanation_example(lang)
        st.session_state.question = q
        st.session_state['choice_' + q.question_id] = 'B'
        st.session_state.example_question = True
        st.session_state.pop('assessment_result', None)
        return
    values = dict(examples[name])
    if name == 'debug':
        values['debug_expected'] = ('Overall 表中保留每张发票的数据。' if lang == 'zh'
                                    else 'Keep the data from every invoice in the Overall sheet.')
        values['debug_actual'] = ('处理多个 PDF 后，Overall 表中只保留最后一张发票的数据；流程没有报错。' if lang == 'zh'
                                  else 'After processing multiple PDFs, Overall contains only the last invoice. The workflow reports no error.')
        values['debug_error'] = ''
    if name in {'next_step', 'debug'}:
        values['help_mode'] = MODE_LABELS[lang][name]
    st.session_state.update(values)
    if name == 'learning':
        st.session_state.pop('learning', None)
    elif name in {'next_step', 'debug'}:
        st.session_state.pop('build_result', None)
    else:
        st.session_state.pop('question', None)
        st.session_state.pop('assessment_result', None)
        st.session_state.example_question = False


def fill_learning_prompt(prompt, week):
    set_active_module('learning')
    st.session_state.learn_question = prompt
    st.session_state.learn_week = week if week is not None else tr(current_language(), 'week_any')
    st.session_state.pop('learning', None)


def continue_learning(question, concept, week, kind):
    fill_learning_prompt(followup_prompt(question, concept, kind, current_language()), week)


def practice_this_concept(concept):
    st.session_state.gen_topic = concept[:1000]
    st.session_state['_practice_from_learning'] = concept[:1000]
    st.session_state.pop('question', None)
    st.session_state.pop('assessment_result', None)
    st.session_state.example_question = False
    set_active_module('generate')


def sources(evidence):
    with st.expander(tr(lang, 'sources'), expanded=False):
        if not evidence:
            st.caption(tr(lang, 'no_evidence'))
        for e in evidence:
            st.write(f'{e.source_label} [{e.source_id}]')
            if e.source_pages:
                st.caption(tr(lang, 'pages') + ', '.join(map(str, e.source_pages)))
            if e.url:
                st.link_button(tr(lang, 'official_sources'), e.url)
            if e.product:
                checked_label = 'Checked on' if lang == 'en' else '核对日期'
                st.caption(
                    f"{e.product} · {e.version or tr(lang, 'source_missing_version')} · "
                    f"{checked_label}: {e.checked_on or tr(lang, 'source_missing_date')}"
                )
            st.write(e.text)


def status(result):
    labels = STATUS_LABELS[lang]
    render = st.success if result.status in {'ANSWERED', 'GENERATED'} else st.warning
    render(labels.get(result.status, result.status))
    for item in getattr(result, 'need_more_information', []):
        st.write(f"{tr(lang, 'need_more_information')}: {item}")
    if getattr(result, 'reason', ''):
        st.write(result.reason)


try:
    catalog = exercise_catalog()
    counts = {t: len(load([t])) for t in ('concept', 'task', 'question', 'official')}
except (ValueError, OSError):
    st.error(tr(lang, 'request_failed') + '：' + ('Please run the data validation script first.' if lang == 'en' else '请先运行数据检查脚本。'))
    st.stop()


with st.sidebar:
    st.header(tr(lang, 'knowledge_bank_status'))
    render_library_counts(counts, lang)
    st.caption(tr(lang, 'review_note'))


active_module = st.radio(
    'Module',
    ['learning', 'practice', 'generate'],
    key=ACTIVE_MODULE_KEY,
    format_func=lambda value: {
        'learning': '知识问答' if lang == 'zh' else 'Learn & explain',
        'practice': '操作与排错' if lang == 'zh' else 'Build & debug',
        'generate': '练习与测验' if lang == 'zh' else 'Practice & assess',
    }[value],
    horizontal=True,
    label_visibility='collapsed',
    width='stretch',
)

help_hint, help_button = st.columns([4, 1.5], vertical_alignment='center')
with help_hint:
    st.caption('不知道问什么，或遇到问题？点右侧问号。' if lang == 'zh'
               else 'Not sure what to ask, or stuck? Open Help & FAQs.')
with help_button:
    render_help(lang, active_module, config.MOCK_LLM, fill_example)

if active_module == 'learning':
    st.markdown(
        '<div class="course-intro"><div class="course-eyebrow">LEARN &amp; EXPLAIN</div>'
        '<h2>' + ('把知识点，真正弄明白。' if lang == 'zh' else 'Build understanding, one question at a time.') + '</h2>'
        '<p>' + ('提出你的疑问，从课程资料中寻找解释与练习联系。' if lang == 'zh'
                  else 'Ask a question. Connect the explanation to your course materials and exercises.') + '</p></div>',
        unsafe_allow_html=True,
    )
    st.caption('从一个问题开始 · 点击示例填入' if lang == 'zh' else 'Start with a question · Select an example')
    prompts = [
        ('DataTable 与写回' if lang == 'zh' else 'DataTable & write-back',
         '为什么修改 DataTable 后，Google Sheets 里的内容没有变化？' if lang == 'zh'
         else 'Why does editing a DataTable not update Google Sheets?', 2),
        ('理解 RPA' if lang == 'zh' else 'Understanding RPA',
         '什么是 RPA？哪些任务适合使用 RPA？' if lang == 'zh'
         else 'What is RPA, and which tasks are suitable for it?', None),
        ('循环与数据行' if lang == 'zh' else 'Loops & data rows',
         'For Each Row 如何逐行处理 DataTable？' if lang == 'zh'
         else 'How does For Each Row process a DataTable?', 2),
    ]
    with st.container(key='learning_examples'):
        for col, (label, prompt, example_week) in zip(st.columns(3), prompts):
            col.button(label, on_click=fill_learning_prompt, args=(prompt, example_week), use_container_width=True)
    with st.form('learning_form'):
        question = st.text_area(tr(lang, 'question_label'), placeholder=tr(lang, 'question_placeholder'), height=140, max_chars=12000, key='learn_question')
        week_options = [tr(lang, 'week_any'), 1, 2, 3, 4, 5]
        week_col, depth_col = st.columns(2)
        week = week_col.selectbox(tr(lang, 'week_label'), week_options, key='learn_week')
        depth = depth_col.selectbox(tr(lang, 'depth_label'), ['Brief', 'Detailed'], key='learn_depth',
                                   format_func=lambda value: {'Brief': '简洁讲解', 'Detailed': '详细讲解'}[value] if lang == 'zh' else value)
        ask = st.form_submit_button(
            ('查看相关资料' if lang == 'zh' else 'Find course materials') if config.MOCK_LLM
            else ('获取讲解' if lang == 'zh' else 'Explain this'), type='primary')
    if ask:
        submitted_question = st.session_state.get('learn_question', question)
        if not submitted_question.strip():
            st.warning('请先输入一个问题，或选择上方示例。' if lang == 'zh' else 'Enter a question or choose an example above.')
        else:
            st.session_state.learning = attempt(
                'learning', answer_concept_question, question=submitted_question,
                week=None if week == tr(lang, 'week_any') else week, depth=depth,
            )
            st.session_state['_learning_context'] = {
                'question': submitted_question,
                'week': None if week == tr(lang, 'week_any') else week,
                'depth': depth,
            }
    r = st.session_state.get('learning')
    if r:
        with st.container(key='learning_answer'):
            context = st.session_state.get('_learning_context', {})
            if context.get('question'):
                st.caption('本次提交的问题' if lang == 'zh' else 'Question for this result')
                st.write(context['question'])
                st.divider()
            st.subheader(('相关课程资料' if lang == 'zh' else 'Related course materials') if config.MOCK_LLM
                         else ('为你梳理的讲解' if lang == 'zh' else 'Your explanation'))
            evidence_count = len(unique_evidence(r.evidence))
            st.caption(f'{evidence_count} 条资料摘录可供核对' if lang == 'zh'
                       else f'{evidence_count} source excerpts available to inspect')
            if config.MOCK_LLM and r.status == 'ANSWERED':
                st.caption('资料原文预览 · 不是 AI 生成的回答' if lang == 'zh'
                           else 'Source material preview · Not an AI-generated answer')
            else:
                status(r)
            st.write(r.answer)
            if r.key_concept:
                st.caption(f"{tr(lang, 'key_concept')} {r.key_concept}")
            if r.exercise_connection:
                st.markdown('#### ' + tr(lang, 'exercise_connection').rstrip('：: '))
                st.write(r.exercise_connection)
            if r.common_misunderstanding:
                st.markdown('#### ' + tr(lang, 'common_misunderstanding').rstrip('：: '))
                st.write(r.common_misunderstanding)
            render_learning_sources(r.evidence, lang)
        if r.status == 'ANSWERED':
            with st.container(key='learning_next'):
                st.markdown('### 接下来，你可以…' if lang == 'zh' else 'Keep learning')
                st.caption('追问按钮会填入新问题；练习按钮会带入知识点。确认提交后才处理。' if lang == 'zh'
                           else 'Follow-ups fill a new question; practice carries over the topic. Review and submit when ready.')
                next_example, next_compare, next_practice = st.columns(3)
                original_question = context.get('question', '')
                next_example.button('举个例子' if lang == 'zh' else 'Show an example',
                                    key='learn_followup_example', width='stretch',
                                    disabled=not bool(original_question), on_click=continue_learning,
                                    args=(original_question, r.key_concept, context.get('week'), 'example'))
                next_compare.button('辨析易混点' if lang == 'zh' else 'Clarify differences',
                                    key='learn_followup_compare', width='stretch',
                                    disabled=not bool(original_question), on_click=continue_learning,
                                    args=(original_question, r.key_concept, context.get('week'), 'compare'))
                next_practice.button('用这个知识点练一题' if lang == 'zh' else 'Practice this concept',
                                     key='learn_to_practice', width='stretch', disabled=not bool(r.key_concept.strip()),
                                     on_click=practice_this_concept, args=(r.key_concept,))
                with st.expander('先自己想一想 · 30 秒回顾' if lang == 'zh' else 'Think it through · A 30-second recap'):
                    st.write('先不看上面的解释，用自己的话说出核心概念；再展开一条课程资料，检查是否支持你的理解。' if lang == 'zh'
                             else 'Without looking at the explanation, describe the key idea in your own words. Then open a course source and check whether it supports your understanding.')
    else:
        st.markdown('<div class="learning-empty">' +
                    ('讲解与资料来源会显示在这里。<br>可以先试试上方的示例问题。' if lang == 'zh'
                     else 'Your explanation and sources will appear here.<br>Try one of the example questions above.') +
                    '</div>', unsafe_allow_html=True)

if active_module == 'practice':
    st.markdown(
        '<div class="course-intro"><div class="course-eyebrow">BUILD &amp; DEBUG</div><h2>'
        + ('把卡住的步骤，理清楚。' if lang == 'zh' else 'Work through the step that has you stuck.')
        + '</h2><p>' + ('选择课堂练习，再描述你目前做到哪里。' if lang == 'zh'
                        else 'Choose your course exercise, then describe your current workflow state.') + '</p></div>',
        unsafe_allow_html=True,
    )
    st.caption('先试一个示例 · 只填入内容，不自动提交' if lang == 'zh'
               else 'Try an example · Fills the form without submitting')
    sample_next, sample_debug = st.columns(2)
    sample_next.button(tr(lang, 'fill_next'), on_click=fill_example, args=('next_step',), width='stretch')
    sample_debug.button(tr(lang, 'fill_debug'), on_click=fill_example, args=('debug',), width='stretch')
    week_col, exercise_col = st.columns([1, 2])
    w = week_col.selectbox(tr(lang, 'week_select'), list(catalog), key='build_week')
    ex = exercise_col.selectbox(tr(lang, 'exercise_select'), catalog[w], key=f'exercise_{w}')
    modes = mode_options(lang)
    selected_mode = st.radio(tr(lang, 'mode_label'), modes, horizontal=True, key='help_mode')
    with st.form('practice_form'):
        if selected_mode == MODE_LABELS[lang]['next_step']:
            st.markdown('#### 01 · 最后完成了哪一步？' if lang == 'zh' else '#### 01 · What did you finish?')
            last = st.text_input(tr(lang, 'last_step'), max_chars=12000, key='next_last',
                                 placeholder='例如：已配置 Use Application/Browser。' if lang == 'zh' else 'For example: configured Use Application/Browser.')
            st.markdown('#### 02 · 现在停在哪里？' if lang == 'zh' else '#### 02 · Where are you now?')
            state = st.text_area(tr(lang, 'current_state'), max_chars=12000, key='next_state', height=110,
                                 placeholder='说明当前可见的界面、结果，以及还没完成的操作。' if lang == 'zh'
                                 else 'Describe the visible screen, current result and what has not been completed.')
        else:
            st.markdown('#### 01 · 想实现什么？' if lang == 'zh' else '#### 01 · What should happen?')
            activity = st.text_input('出问题的 Activity 或步骤' if lang == 'zh' else 'Activity or step with the issue',
                                     max_chars=1000, key='debug_activity', placeholder='例如：Write Range、For Each Row' if lang == 'zh' else 'For example: Write Range, For Each Row')
            expected = st.text_area('预期结果（可选）' if lang == 'zh' else 'Expected result (optional)',
                                    max_chars=1000, key='debug_expected', height=85,
                                    placeholder='例如：每张发票的数据都追加到 Overall 表。' if lang == 'zh'
                                    else 'For example: append each invoice to the Overall sheet.')
            st.markdown('#### 02 · 实际发生了什么？' if lang == 'zh' else '#### 02 · What actually happened?')
            actual = st.text_area('实际结果或异常现象' if lang == 'zh' else 'Observed result or unexpected behaviour',
                                  max_chars=4500, key='debug_actual', height=110,
                                  placeholder='例如：没有报错，但最后只剩一张发票的数据。' if lang == 'zh'
                                  else 'For example: no error appears, but only the last invoice remains.')
            st.markdown('#### 03 · 有哪些排查线索？' if lang == 'zh' else '#### 03 · What clues do you have?')
            error = st.text_area('报错原文（没有报错可留空）' if lang == 'zh' else 'Exact error (leave blank if none)',
                                 max_chars=6000, key='debug_error', height=85,
                                 placeholder='粘贴完整报错，并去掉个人信息。' if lang == 'zh' else 'Paste the complete error with personal information removed.')
            change = st.text_input(tr(lang, 'recent_change'), max_chars=4000, key='debug_change',
                                   placeholder='例如：从处理一个文件改成循环处理多个文件。' if lang == 'zh'
                                   else 'For example: changed from one file to a loop over multiple files.')
            st.caption('实际结果和报错至少填写一项。只提供你观察到的事实即可。' if lang == 'zh'
                       else 'Provide an observed result or an error message. Describe what you actually observed.')
        build = st.form_submit_button(
            ('查看相关资料' if lang == 'zh' else 'Find course materials') if config.MOCK_LLM
            else (('获取下一步' if lang == 'zh' else 'Find my next step') if selected_mode == MODE_LABELS[lang]['next_step']
                  else ('开始排查' if lang == 'zh' else 'Start troubleshooting')), type='primary')
    context = (w, ex, selected_mode)
    if build:
        next_mode = selected_mode == MODE_LABELS[lang]['next_step']
        if next_mode:
            missing = [] if last.strip() and state.strip() else [
                '请填写最后完成的操作和当前状态。' if lang == 'zh' else 'Enter the last completed step and the current state.']
        else:
            missing = missing_debug_fields(activity, actual, error, lang)
        if missing:
            st.session_state.pop('build_result', None)
            for message in missing:
                st.warning(message)
        else:
            inputs = dict(week=w, exercise=ex, last_completed_step=last, current_state=state) if next_mode else dict(
                week=w, exercise=ex, activity=activity,
                error_message=debug_observations(expected, actual, error, lang), recent_change=change)
            r = attempt('next_step' if next_mode else 'debug', get_next_step if next_mode else debug_workflow, **inputs)
            st.session_state.build_result = (context, r)
            st.session_state['_practice_request'] = inputs
    stored = st.session_state.get('build_result')
    if stored and stored[0] == context and stored[1]:
        r = stored[1]
        st.divider()
        st.subheader(('相关课程资料' if lang == 'zh' else 'Related course materials') if config.MOCK_LLM
                     else ('下一步指导' if lang == 'zh' else 'Your next step') if selected_mode == MODE_LABELS[lang]['next_step']
                     else ('排查建议' if lang == 'zh' else 'Troubleshooting guidance'))
        st.caption(f'Week {w} · {ex}')
        with st.expander('查看本次提交的情况' if lang == 'zh' else 'Review the submitted situation'):
            submitted = st.session_state.get('_practice_request', {})
            for field, label in [('activity', tr(lang, 'activity_name')), ('last_completed_step', tr(lang, 'last_step')),
                                 ('current_state', tr(lang, 'current_state')), ('error_message', '情况描述' if lang == 'zh' else 'Situation'),
                                 ('recent_change', tr(lang, 'recent_change'))]:
                if submitted.get(field):
                    st.markdown('**' + label + '**')
                    st.text(submitted[field])
        preview_messages = {tr(code, key) for code in ('zh', 'en')
                            for key in ('demo_previews_only', 'configure_real_model_next')}
        preview_only = config.MOCK_LLM and r.status == 'NEED_MORE_INFORMATION' and any(
            note in preview_messages for note in r.need_more_information)
        if preview_only:
            st.info('已找到相关资料。当前为预览模式，不生成排查结论或下一步判断。' if lang == 'zh'
                    else 'Related materials are ready. Preview mode does not generate a diagnosis or decide the next step.')
        else:
            status(r)
        if selected_mode == MODE_LABELS[lang]['next_step']:
            st.write(r.where_you_are)
            for i, action in enumerate(r.next_actions, 1):
                st.write(f'{i}. {action}')
            if r.activity_or_expression:
                st.code('\n'.join(r.activity_or_expression), language=None)
            if r.expected_result:
                st.write(f"{tr(lang, 'expected_result')} {r.expected_result}")
            if r.common_mistake:
                st.write(f"{tr(lang, 'mistake')} {r.common_mistake}")
        else:
            categories = DIAGNOSIS_LABELS[lang]
            if not preview_only:
                st.caption(tr(lang, 'question_type') + categories.get(r.diagnosis_type, r.diagnosis_type))
            if r.possible_causes:
                st.caption(
                    'The following are hypotheses to verify, not confirmed root causes. Check the first one before expanding others.'
                    if lang == 'en'
                    else '以下是待验证的排查方向，并非已确认的根因。先检查第一项，未解决再展开其他原因。'
                )
                first = r.possible_causes[0]
                with st.container(border=True):
                    st.markdown(f"### 01 · {tr(lang, 'priority_check')}")
                    st.write(first.cause)
                    st.markdown(f"**{tr(lang, 'check')}**")
                    st.write(first.check)
                    st.markdown('**检查确认后再修复**' if lang == 'zh' else '**Apply the fix only if the check confirms it**')
                    st.write(first.fix)
                    if first.rationale:
                        with st.expander(tr(lang, 'why_first')):
                            st.write(first.rationale)
                if len(r.possible_causes) > 1:
                    st.markdown(f"#### {tr(lang, 'other_causes')}")
                    for i, c in enumerate(r.possible_causes[1:], 2):
                        with st.expander(f"{i}. {tr(lang, 'priority_check')}"):
                            st.write(c.cause)
                            st.markdown(f"**{tr(lang, 'check')}**")
                            st.write(c.check)
                            st.markdown('**检查确认后再修复**' if lang == 'zh' else '**Apply the fix only if the check confirms it**')
                            st.write(c.fix)
                            if c.rationale:
                                st.markdown(f"**{tr(lang, 'why_first')}**")
                                st.write(c.rationale)
        if r.verification:
            with st.container(border=True):
                st.markdown(
                    f"#### {tr(lang, 'verification_after_fix')}" if selected_mode == MODE_LABELS[lang]['debug']
                    else f"#### {tr(lang, 'verification_complete')}"
                )
                st.write(r.verification)
        render_learning_sources(r.evidence, lang)

if active_module == 'generate':
    st.markdown('<div class="course-intro"><div class="course-eyebrow">PRACTICE &amp; ASSESS</div><h2>'
                + ('把理解，变成会用。' if lang == 'zh' else 'Put your understanding into practice.')
                + '</h2><p>' + ('从一个知识点开始，用练习检查自己的理解。' if lang == 'zh'
                                else 'Start with a concept and check your understanding through practice.')
                + '</p></div>', unsafe_allow_html=True)
    if st.session_state.get('_practice_from_learning') == st.session_state.get('gen_topic') and st.session_state.get('gen_topic'):
        st.info(('已从知识问答带入：' if lang == 'zh' else 'Topic carried over from your explanation: ') + st.session_state.gen_topic)
        st.caption('检查下方知识点、难度和题型，再点击生成。' if lang == 'zh'
                   else 'Review the topic, difficulty and question type, then select Generate.')
    st.caption(
        'The generated item is for learning practice, not exam prediction. Questions and explanations still need to be checked against the source material.'
        if lang == 'en'
        else '生成的是学习练习，不是考试预测。题目与解析仍需结合原资料核对。'
    )
    sample_gen, sample_explain = st.columns(2)
    sample_gen.button(tr(lang, 'fill_generate'), on_click=fill_example, args=('generate',))
    sample_explain.button(tr(lang, 'fill_explain'), on_click=fill_example, args=('explain',))
    st.caption(tr(lang, 'sample_caption'))
    with st.form('generate_form'):
        topic = st.text_input(tr(lang, 'topic_label'), placeholder=tr(lang, 'topic_placeholder'), max_chars=1000, key='gen_topic')
        diff = st.selectbox(tr(lang, 'difficulty_label'), ['Easy', 'Medium', 'Hard'], index=1, key='gen_difficulty')
        qt = st.selectbox(tr(lang, 'question_type_label'), ['Concept Distinction', 'Workflow Logic', 'Activity Selection', 'Error Diagnosis', 'Activity Placement', 'Output Prediction'], key='gen_type')
        generate = st.form_submit_button(tr(lang, 'generate_button'))
    if generate:
        st.session_state.question = attempt('generate', generate_question, topic=topic, difficulty=diff, question_type=qt)
        st.session_state.example_question = False
        st.session_state.pop('assessment_result', None)
    q = st.session_state.get('question')
    if q:
        status(q)
        if q.status == 'GENERATED':
            if not st.session_state.get('example_question') and q.review_status == 'NEEDS_HUMAN_REVIEW':
                st.warning(tr(lang, 'review_pending'))
            if st.session_state.get('example_question'):
                st.caption(tr(lang, 'review_example'))
            with st.container(key='practice_question_card'):
                with st.form('answer_' + q.question_id, border=False):
                    st.markdown(
                        '<div class="question-eyebrow">' + tr(lang, 'question_stem') + '</div>'
                        '<div class="question-stem">'
                        + escape(q.question) + '</div>',
                        unsafe_allow_html=True,
                    )
                    answer = st.radio(tr(lang, 'select_answer'), list(q.options), index=None, format_func=lambda k: f'{k}. {q.options[k]}', key='choice_' + q.question_id)
                    submit = st.form_submit_button(tr(lang, 'submit_answer'))
            if submit:
                if answer is None:
                    st.warning(tr(lang, 'need_choose'))
                else:
                    explanation = attempt('explain', explain_question, question=q, user_answer=answer)
                    st.session_state.assessment_result = (q.question_id, answer, explanation)
            saved = st.session_state.get('assessment_result')
            if saved and saved[0] == q.question_id and saved[2]:
                _, submitted_answer, exp = saved
                st.markdown('### ' + tr(lang, 'answer_analysis'))
                st.caption(tr(lang, 'last_answer') + submitted_answer)
                status(exp)
                if exp.status == 'ANSWERED':
                    if submitted_answer == exp.correct_answer:
                        st.success(tr(lang, 'correct'))
                    else:
                        st.info(tr(lang, 'correct_answer') + exp.correct_answer)
                    st.write(exp.why_correct)
                    for k, value in exp.why_others_wrong.items():
                        st.write(f'{k}: {value}')
                    st.write(f"{tr(lang, 'learning_point')} {exp.learning_takeaway}")
                    if exp.student_misunderstanding:
                        st.write(f"{tr(lang, 'reusable_point')} {exp.student_misunderstanding}")
                sources(exp.evidence)
                sources([evidence_for(c) for c in by_ids(q.course_evidence_ids)])

st.divider()
with st.expander(tr(lang, 'log_section'), expanded=False):
    st.caption(tr(lang, 'log_caption'))
    st.caption(tr(lang, 'log_redaction'))
    rows = st.session_state.get('test_runs', [])
    if not rows:
        st.info(tr(lang, 'no_runs'))
    else:
        st.dataframe([
            {
                tr(lang, 'record'): r['run_id'],
                tr(lang, 'task'): r['task_label'],
                tr(lang, 'version'): r['prompt_version'],
                tr(lang, 'mode'): tr(lang, 'display_mode_mock') if r['mock'] else tr(lang, 'display_mode_real'),
                tr(lang, 'status'): 'ERROR' if r['error'] else r['output'].get('status', ''),
                tr(lang, 'elapsed_s'): r['elapsed_seconds'],
            }
            for r in rows
        ], hide_index=True)
        selected_id = st.selectbox(tr(lang, 'view_record'), [r['run_id'] for r in reversed(rows)], key='export_selection')
        selected = next(r for r in rows if r['run_id'] == selected_id)
        st.caption(
            f"{selected['task_label']} · {selected['prompt_version']} · {tr(lang, 'elapsed', seconds=selected['elapsed_seconds'])}"
        )
        st.text(tr(lang, 'stage_label') + ' → '.join(s['label'] for s in selected['stages']))
        st.json(selected, expanded=False)
        download_one, download_all = st.columns(2)
        download_one.download_button(
            tr(lang, 'download_one'),
            export_json([selected], language=lang),
            file_name=f"C_test_{selected_id}.json",
            mime='application/json',
            on_click='ignore',
        )
        download_all.download_button(
            tr(lang, 'download_all'),
            export_json(rows, language=lang),
            file_name='C_function_tests.json',
            mime='application/json',
            on_click='ignore',
        )
        st.download_button(
            tr(lang, 'download_md'),
            export_markdown(rows, language=lang),
            file_name='C_function_tests.md',
            mime='text/markdown',
            on_click='ignore',
        )

render_footer()
