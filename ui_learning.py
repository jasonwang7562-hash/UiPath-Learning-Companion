"""Source inspection and next learning actions; no model requests here."""
import streamlit as st


def unique_evidence(evidence):
    seen = set()
    result = []
    for item in evidence:
        key = (item.source_id, item.source_label, tuple(item.source_pages), item.text, item.url)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def render_learning_sources(evidence, language):
    zh = language == 'zh'
    items = unique_evidence(evidence)
    st.markdown('#### 核对课程依据' if zh else 'Check the course evidence')
    if not items:
        st.caption('本次没有可核对的资料引用。' if zh else 'No source references are available for this result.')
        return
    st.caption('逐条展开查看资料摘录；引用数量不代表答案已经验证。' if zh
               else 'Open a source to inspect its excerpt. A source count does not establish correctness.')
    for index, item in enumerate(items, 1):
        pages = ', '.join(map(str, item.source_pages))
        page_label = ('第 ' + pages + ' 页' if zh else 'pp. ' + pages) if pages else ('页码未提供' if zh else 'Pages not provided')
        with st.expander(f'{index:02d} · {item.source_label or item.source_id} · {page_label}'):
            st.caption(item.source_id)
            st.write(item.text or ('暂无摘录。' if zh else 'No excerpt available.'))
            if item.url and item.url.lower().startswith(('https://', 'http://')):
                st.link_button('打开原始链接' if zh else 'Open source link', item.url)
            if item.product:
                st.caption(' · '.join(str(value) for value in [item.product, item.version, item.checked_on] if value))


def followup_prompt(question, concept, kind, language):
    if language == 'zh':
        instruction = ('请结合课程资料，给出一个具体例子，帮助我理解这个问题。'
                       if kind == 'example' else '请解释这个问题中最容易混淆的概念，以及如何区分它们。')
        return f'原问题：{question}\n相关知识点：{concept}\n{instruction}'
    instruction = ('Use the course materials to give a concrete example that helps explain this question.'
                   if kind == 'example' else 'Explain the concepts most easily confused in this question and how to distinguish them.')
    return f'Original question: {question}\nRelated concept: {concept}\n{instruction}'
