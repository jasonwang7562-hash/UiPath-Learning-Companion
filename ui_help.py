"""Bilingual, module-aware guidance. Opening help never requests a model."""
import streamlit as st


GUIDES = {
    'zh': {
        'learning': ('知识问答', [
            ('不知道该问什么？', '可以从“是什么、为什么、有什么区别”开始。写出具体的 Activity 或知识点；知道课程周次时再选择 Week。\n\n**示例：** 为什么修改 DataTable 后，Google Sheets 里的数据没有变化？'),
            ('怎样让问题更清楚？', '用“知识点＋不理解的地方＋希望怎么解释”的方式提问。\n\n**提问模板：** 我正在学习【知识点】，不理解【具体疑问】。请结合课程资料，用一个例子解释。'),
            ('看完回答后还不明白怎么办？', '在回答下方选择“举个例子”或“辨析易混点”，检查自动填入的问题后再提交。也可以选择“用这个知识点练一题”，到练习页检查主题后生成。'),
        ]),
        'practice': ('操作与排错', [
            ('我应该选“下一步”还是“Debug”？', '**下一步：** 流程暂时没有出问题，但不知道接着做什么。填写最后完成的操作和当前状态。\n\n**Debug：** 出现报错，或运行结果和预期不一样。填写出问题的 Activity，以及实际现象或报错。'),
            ('不知道怎么描述问题？', '**提问模板：** 我在 Week【周次】的【练习】中使用【Activity】。我希望【预期结果】，但实际【异常现象】。报错是【原文，没有可留空】，最近修改了【操作】。\n\n不需要先猜原因，描述你看到的情况即可。'),
            ('没有报错，但结果不对，也能问吗？', '可以。在“实际结果或异常现象”中说明问题，例如“处理多个 PDF 后，表格只保留最后一个文件的数据”。报错框可以留空；实际现象和报错至少填写一项。'),
            ('拿到排查建议后怎么做？', '先做“优先检查”，确认情况吻合后再使用对应修复办法。最后按“修复后验证”检查结果。其他可能原因可以逐项展开，避免一次修改多处。'),
        ]),
        'generate': ('练习与测验', [
            ('不知道该填什么知识点？', '先选一个具体课程概念，例如 DataTable、Google Sheets 或 For Each Row，再选择难度和题型。也可以先用知识问答理解概念，再通过回答下方的入口带入练习主题。'),
            ('生成题目之后怎么做？', '阅读题目、选择 A–D 中的一项，再点击“提交答案”查看讲解。题目和解析仍需结合课程资料核对。'),
            ('题目被标记“需要复核”怎么办？', '先展开资料来源核对题干、选项与解释。如果仍有多个合理答案或资料不足，请交给组员或老师复核，暂时不要把它作为确定的评分依据。'),
            ('能直接看到一道示例题吗？', '可以点击下方“载入讲题示例”。这是固定开发测试题，不是新生成的题目，也不是教师原题。示例预选了 B，你可以修改后提交；预览模式不会判分。'),
        ]),
    },
    'en': {
        'learning': ('Learn & explain', [
            ('What can I ask?', 'Start with “what is”, “why”, or “what is the difference”. Name the activity or concept and select a course week if you know it.\n\n**Example:** Why does editing a DataTable not update Google Sheets?'),
            ('How can I make my question clearer?', 'Include the concept, the specific difficulty and the kind of explanation you need.\n\n**Template:** I am learning about [concept] and do not understand [specific question]. Please use course materials and an example to explain it.'),
            ('What if I still do not understand?', 'Choose “Show an example” or “Clarify differences” below the answer. Review the new question before submitting. “Practice this concept” carries the topic into the practice page for you to review.'),
        ]),
        'practice': ('Build & debug', [
            ('Should I choose Next step or Debug?', '**Next step:** You are unsure what to do after the last completed action. Describe that action and the current state.\n\n**Debug:** An error occurs or the result differs from what you expected. Name the activity and describe the observed behaviour or error.'),
            ('How do I describe the problem?', '**Template:** In Week [number], exercise [name], I use [activity]. I expect [result], but observe [actual result]. The exact error is [message, if any]. My most recent change was [change].\n\nDescribe what you observed; you do not need to guess the cause.'),
            ('Can I ask about a wrong result without an error?', 'Yes. Describe the unexpected behaviour, such as “only the last invoice remains after processing several PDFs”. Leave the error field blank. Either an observed result or an error message is required.'),
            ('How should I use the troubleshooting advice?', 'Start with the priority check. Apply its fix only if the check confirms that situation, then verify the result. Expand other possible causes one at a time.'),
        ]),
        'generate': ('Practice & assess', [
            ('What topic should I enter?', 'Choose a specific course concept such as DataTable, Google Sheets or For Each Row, then select difficulty and question type. You can also carry a topic over from a concept explanation.'),
            ('What happens after a question is generated?', 'Read the question, choose A–D and select “Submit answer” to request an explanation. Check the question and explanation against course sources.'),
            ('What does “needs review” mean?', 'Check the question, options and explanation against the source materials. If multiple answers remain plausible or evidence is missing, ask a teammate or teacher to review it before using it for scoring.'),
            ('Can I try a ready-made question?', 'Select “Load explanation example” below. This is a fixed development example, not a newly generated question or an original teacher question. B is preselected and can be changed. Preview mode does not grade answers.'),
        ]),
    },
}


def render_help(language, module, preview, fill_example):
    lang = 'en' if language == 'en' else 'zh'
    zh = lang == 'zh'
    title, guides = GUIDES[lang][module]
    with st.popover('使用帮助' if zh else 'Help & FAQs', icon=':material/help_outline:',
                    key='course_help', width='stretch'):
        st.markdown('### 使用帮助' if zh else '### Help & FAQs')
        st.caption(('当前模块：' if zh else 'Current module: ') + title)
        for index, (question, answer) in enumerate(guides):
            with st.expander(question, expanded=index == 0):
                st.markdown(answer)
        st.markdown('#### 先试一个示例' if zh else '#### Try an example')
        buttons = {
            'learning': [('learning', '填入知识问答示例', 'Fill a concept example')],
            'practice': [('next_step', '填入下一步示例', 'Fill a next-step example'), ('debug', '填入 Debug 示例', 'Fill a troubleshooting example')],
            'generate': [('generate', '填入出题示例', 'Fill a question-generation example'), ('explain', '载入讲题示例', 'Load explanation example')],
        }
        for example, cn, en in buttons[module]:
            st.button(cn if zh else en, key='help_example_' + example, on_click=fill_example,
                      args=(example,), width='stretch')
        st.caption('示例会替换对应输入和旧结果，不自动提交。点击弹窗外即可返回表单。' if zh
                   else 'Examples replace the corresponding inputs and previous result without submitting. Click outside this panel to return to the form.')
        st.markdown('#### 常见问题' if zh else '#### Common questions')
        common = [
            ('为什么只能看资料，不能生成答案或试题？' if preview else '请求失败怎么办？',
             ('当前是资料预览模式，只展示课程资料，不生成真实讲解、诊断或试题，也不判分。可以先体验示例和资料查看；需要真实 AI 功能时，请联系项目维护者启用模型服务。' if preview
              else '当前已启用真实模型。如果请求失败，可检查网络后重试；若持续失败，请把页面上的错误信息交给项目维护者检查服务配置。'),
             'Why can I only preview materials?' if preview else 'What if a request fails?',
             ('This session is in material-preview mode. It does not generate real explanations, diagnoses or questions, or grade answers. Try examples and inspect sources; ask the project maintainer to enable the model service for AI features.' if preview
              else 'The model is enabled. If a request fails, check the connection and retry. For repeated failures, share the on-screen error with the project maintainer.')),
            ('提示“资料不足”或“超出范围”怎么办？',
             '知识问答主要覆盖 Weeks 1–5，课堂操作练习覆盖 Weeks 1–4。确认周次和练习选择，补充具体 Activity、概念或异常现象，再提交。如果仍没有依据，请核对课程材料或向老师求助。',
             'What if evidence is missing or a topic is out of scope?',
             'Concept questions cover Weeks 1–5; hands-on exercises cover Weeks 1–4. Check the week and exercise and add a specific activity, concept or observed problem. If evidence is still missing, consult the course materials or your teacher.'),
            ('中文界面为什么会出现英文资料？',
             '资料预览会保留课程资料原文，切换界面语言不会自动翻译原文。真实模型的回答语言还会受你提交的问题语言影响。',
             'Why are some sources in a different language?',
             'Material preview preserves the original course text. Changing interface language does not translate sources; model responses are also influenced by the language of your question.'),
            ('怎样保存结果？切换语言会怎样？',
             '展开页面底部“测试与导出”，下载需要的记录。记录只保留在当前会话；当前版本切换语言会重置输入、结果及会话记录，需要保留时请先导出。分享前检查导出内容。',
             'How do I save results, and what happens when I change language?',
             'Open “Test & export” at the bottom of the page to download records. Records are session-only. In this version, changing language resets inputs, results and records, so export first if needed. Review exported content before sharing.'),
        ]
        for cn_question, cn_answer, en_question, en_answer in common:
            with st.expander(cn_question if zh else en_question):
                st.write(cn_answer if zh else en_answer)
