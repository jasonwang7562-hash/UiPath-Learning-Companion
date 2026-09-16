"""Course workspace visual design, using local CSS and original vector art."""
from html import escape
import streamlit as st

NAVY = '#181C62'
RED = '#D71440'
MEMBERS = ('Fang Xinyi', 'Li Zihao', 'Miao Jiaxuan', 'Wang Chenyu',
           'Wang Senmiao', 'Wu Yushan')


def apply_theme():
    st.markdown('''<style>
    .stApp {--course-border:color-mix(in srgb,currentColor 14%,transparent);
      background-image:radial-gradient(ellipse at 95% 0%,rgba(136,125,232,.12),transparent 42%),
      radial-gradient(ellipse at 0% 75%,rgba(245,166,138,.08),transparent 45%);}
    [data-testid="stMainBlockContainer"] {max-width:1180px;padding-top:4.2rem;padding-bottom:2rem;
      container-type:inline-size;container-name:workspace;}
    [data-testid="stSidebar"] {border-right:1px solid var(--course-border);
      background-image:linear-gradient(165deg,rgba(124,115,216,.07),transparent 65%);}
    [data-testid="stSidebar"] h2 {font-size:1rem!important;}
    h1,h2,h3 {letter-spacing:-.025em;}
    h2 {font-size:1.55rem!important;} h3 {font-size:1.15rem!important;}
    p {line-height:1.7;}
    .workspace-topline {display:flex;align-items:center;justify-content:space-between;gap:12px;
      margin-bottom:14px;font-size:11px;letter-spacing:.08em;font-weight:700;}
    .workspace-wordmark {display:flex;align-items:center;gap:9px;}
    .workspace-logo {display:inline-grid;place-items:center;width:30px;height:30px;border-radius:9px;
      background:#181C62;color:#fff;font-size:17px;font-weight:800;box-shadow:0 4px 12px #181c621a;}
    .workspace-project {font-size:10px;font-weight:600;letter-spacing:.05em;opacity:.65;}
    .workspace-hero {position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(0,1fr) 255px;
      align-items:center;gap:16px;padding:30px 34px;border-radius:24px;color:#fff;
      background:radial-gradient(ellipse at 85% 10%,#6756a2 0%,transparent 58%),linear-gradient(120deg,#171b51,#303475);
      box-shadow:0 12px 32px #24275624;margin-bottom:8px;}
    .workspace-hero::after {content:'';position:absolute;right:-60px;bottom:-140px;width:340px;height:340px;
      border:1px solid #ffffff16;border-radius:50%;pointer-events:none;}
    .hero-copy {position:relative;z-index:1;}
    .hero-eyebrow {font-size:10px;letter-spacing:.13em;color:#c6c4f1;font-weight:700;}
    .workspace-hero h1 {font-size:clamp(28px,3vw,40px)!important;line-height:1.13!important;
      color:#fff!important;padding:12px 0 0!important;margin:0!important;font-weight:750;letter-spacing:-.04em;}
    .workspace-hero h1 span {display:block;color:#d8cdfc;}
    .workspace-hero p {font-size:14px;color:#e0e2f3;line-height:1.65;margin:14px 0;max-width:440px;}
    .hero-badges {display:flex;flex-wrap:wrap;gap:7px;}
    .hero-badges span {font-size:10px;font-weight:600;padding:5px 9px;background:#ffffff10;
      border:1px solid #ffffff29;border-radius:20px;letter-spacing:.01em;}
    .hero-badges .preview-badge {background:#d9efdf;color:#244b39;border:0;}
    .hero-art {width:100%;height:auto;max-height:210px;position:relative;z-index:1;}
    .course-intro {margin:12px 0 4px;padding:2px 0 2px 15px;border-left:3px solid #9384d3;}
    .course-eyebrow {font-size:10px;font-weight:750;letter-spacing:.14em;color:#70619c;margin-bottom:5px;}
    .course-intro h2 {margin:0;padding:0 0 6px;}
    .course-intro p {opacity:.75;margin:0;font-size:14px;}
    .st-key-ui_active_module [role="radiogroup"] {gap:8px;padding:7px;width:100%;border:1px solid var(--course-border);
      background:color-mix(in srgb,currentColor 3%,transparent);border-radius:16px;}
    .st-key-ui_active_module label {flex:1;justify-content:center;margin:0!important;padding:12px 10px;
      border-radius:11px;transition:background .15s,box-shadow .15s;}
    .st-key-ui_active_module label:has(input:checked) {background:linear-gradient(115deg,#242764,#4e4388);
      color:white;box-shadow:0 3px 9px #25255b24;}
    .st-key-ui_active_module label:has(input:checked) p {color:white;font-weight:650;}
    .st-key-ui_active_module label:hover {box-shadow:inset 0 0 0 1px #9688cb;}
    [data-testid="stForm"] {background:color-mix(in srgb,var(--background-color,#fff) 97%,#aaa1d4);
      border:1px solid var(--course-border);border-radius:20px;padding:26px;
      box-shadow:0 5px 22px #24275608;}
    [data-testid="stTextArea"] textarea {line-height:1.75;padding:14px;}
    [data-testid="stForm"] h4 {font-size:1.08rem;color:inherit;}
    [data-testid="stFormSubmitButton"] button {background:linear-gradient(120deg,#D71440,#c42961);color:#fff;
      border:0;border-radius:11px;min-height:44px;font-weight:650;box-shadow:0 4px 11px #d7144022;padding:0 22px;}
    [data-testid="stFormSubmitButton"] button:hover {background:#b91036;color:#fff;box-shadow:0 5px 15px #d7144035;}
    [data-testid="stFormSubmitButton"] button:disabled {opacity:.55;}
    [data-testid="stButton"] button {border-color:var(--course-border);border-radius:11px;transition:transform .15s,box-shadow .15s;}
    [data-testid="stButton"] button:hover {border-color:#8c7bb9;box-shadow:0 5px 13px #24275612;transform:translateY(-1px);}
    button:focus-visible,a:focus-visible {outline:3px solid #6799d0;outline-offset:3px;}
    .st-key-learning_examples button {min-height:68px;text-align:left;font-weight:600;}
    .st-key-learning_examples [data-testid="stColumn"]:nth-child(1) button {background:#efebfa;color:#403267;border-color:#e0d8f1;}
    .st-key-learning_examples [data-testid="stColumn"]:nth-child(2) button {background:#eaf3ef;color:#2d554c;border-color:#d4e6de;}
    .st-key-learning_examples [data-testid="stColumn"]:nth-child(3) button {background:#fbefe8;color:#76523f;border-color:#efded1;}
    .st-key-learning_answer {border:1px solid var(--course-border);border-top:3px solid #9a8bd4;
      border-radius:20px;padding:26px;box-shadow:0 7px 25px #24275608;}
    .st-key-learning_next {margin-top:12px;padding:22px 24px;border-radius:20px;
      background:linear-gradient(120deg,rgba(154,139,212,.12),rgba(103,153,208,.06));border:1px solid #9a8bd42b;}
    .st-key-learning_next button {min-height:46px;}
    .st-key-learning_answer [data-testid="stExpander"] {margin-top:4px;}
    .learning-empty {padding:24px 0 8px;text-align:center;opacity:.65;font-size:14px;line-height:1.8;}
    .library-grid {display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:8px 0 15px;}
    .library-stat {padding:12px;border:1px solid var(--course-border);border-radius:12px;
      background:color-mix(in srgb,currentColor 2%,transparent);}
    .library-stat strong {display:block;font-size:23px;line-height:1.2;color:#625598;font-weight:700;}
    .library-stat span {display:block;margin-top:5px;font-size:11px;opacity:.75;}
    .sidebar-brand {display:flex;align-items:center;gap:10px;margin:8px 0 26px;font-size:14px;line-height:1.4;font-weight:650;}
    .sidebar-brand small {display:block;font-weight:400;font-size:11px;opacity:.6;margin-top:3px;}
    .course-footer {margin-top:22px;padding:20px 2px 6px;border-top:1px solid var(--course-border);
      font-size:12px;line-height:1.9;opacity:.65;}
    .course-members {display:flex;flex-wrap:wrap;gap:3px 16px;margin:5px 0;}
    .course-footer small {font-size:11px;}
    .st-key-practice_question_card {background:rgba(103,153,208,.1);border:1px solid #6799d0;
      border-radius:18px;padding:22px 26px;margin:12px 0 20px;}
    .st-key-practice_question_card [data-testid="stForm"] {background:transparent;padding:0;border:0;box-shadow:none;}
    .question-eyebrow {font-size:12px;font-weight:600;letter-spacing:1px;margin-bottom:10px;}
    .question-stem {font-size:18px;line-height:1.8;white-space:pre-wrap;overflow-wrap:anywhere;margin-bottom:12px;}
    @media(max-width:900px) {.workspace-hero {grid-template-columns:minmax(0,1fr) 165px;padding:26px;gap:8px;}}
    @media(max-width:640px) {
      [data-testid="stMainBlockContainer"] {padding:4.2rem 1rem 1.4rem;}
      [data-testid="stForm"],.st-key-learning_answer,.st-key-learning_next {padding:18px;}
      .st-key-ui_active_module label {padding:9px 5px;}
      .workspace-project {display:none;}
      .workspace-hero {padding:23px;border-radius:19px;grid-template-columns:minmax(0,1fr) 125px;}
      .workspace-hero h1 {font-size:29px!important;}
      .workspace-hero p {font-size:12px;}
      .hero-badges {gap:5px;}.hero-badges span {font-size:9px;padding:4px 7px;}
    }
    @media(max-width:480px) {.workspace-hero {grid-template-columns:1fr;} .hero-art {display:none;}}
    @container workspace (max-width:760px) {
      .workspace-hero {grid-template-columns:minmax(0,1fr) 150px;padding:25px;gap:12px;}
      .workspace-hero h1 {font-size:29px!important;}
      .workspace-hero p {font-size:12px;margin:12px 0;}
    }
    @container workspace (max-width:480px) {
      .workspace-hero {grid-template-columns:minmax(0,1fr) 105px;padding:20px;gap:8px;}
      .workspace-hero h1 {font-size:25px!important;}
      .hero-eyebrow {font-size:8px;}
    }
    @container workspace (max-width:360px) {.workspace-hero {grid-template-columns:1fr;} .hero-art {display:none;}}
    @media(prefers-reduced-motion:reduce) {button,label {transition:none!important;transform:none!important;}}
    </style>''', unsafe_allow_html=True)


def render_header(language, preview):
    zh = language == 'zh'
    description = '让课程知识、操作实践与练习，在这里连起来。' if zh else 'Connect course concepts, hands-on practice and assessment.'
    badge = ('资料预览 · 不调用模型' if zh else 'Preview · No model calls') if preview else ('AI 讲解模式' if zh else 'AI-assisted mode')
    # Original decorative vector art: a workbook connected to a flow and practice card.
    art = '''<svg class="hero-art" viewBox="0 0 260 220" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
    <circle cx="139" cy="113" r="92" fill="none" stroke="#d4c9ff" stroke-opacity=".18"/>
    <circle cx="139" cy="113" r="67" fill="none" stroke="#d4c9ff" stroke-opacity=".12"/>
    <path d="M48 57Q123 17 211 64M44 160Q124 221 218 151" fill="none" stroke="#c0b2f0" stroke-dasharray="3 6" stroke-opacity=".6"/>
    <g transform="rotate(-8 115 113)"><rect x="68" y="39" width="123" height="155" rx="14" fill="#101333" opacity=".25"/>
    <rect x="61" y="31" width="123" height="155" rx="14" fill="#eeeafa"/><rect x="61" y="31" width="15" height="155" rx="7" fill="#c2b1ed"/>
    <rect x="91" y="53" width="67" height="7" rx="3.5" fill="#5d518c"/><rect x="91" y="69" width="47" height="4" rx="2" fill="#b8aecf"/>
    <rect x="91" y="93" width="70" height="37" rx="7" fill="#ddd5f0"/>
    <path d="M104 111l8 7 15-18" fill="none" stroke="#7662a4" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M91 147h65m-65 12h49" stroke="#b8aecf" stroke-width="4" stroke-linecap="round"/></g>
    <g transform="rotate(9 211 145)"><rect x="174" y="116" width="66" height="62" rx="13" fill="#f4c4ad"/>
    <path d="M190 136h30m-30 9h23m-23 9h15" stroke="#815245" stroke-width="3" stroke-linecap="round"/></g>
    <rect x="16" y="105" width="66" height="49" rx="12" fill="#bfe0d5"/>
    <path d="M31 129h10m14 0h11m-17-12v8" stroke="#447664" stroke-width="2"/>
    <rect x="26" y="125" width="10" height="9" rx="2" fill="#447664"/><rect x="44" y="125" width="10" height="9" rx="2" fill="#447664"/>
    <rect x="62" y="125" width="10" height="9" rx="2" fill="#447664"/><rect x="44" y="112" width="10" height="9" rx="2" fill="#447664"/>
    <path d="M212 27v18m-9-9h18" stroke="#ead9a8" stroke-width="2" stroke-linecap="round"/>
    <circle cx="36" cy="63" r="4" fill="#cbbdf2"/><circle cx="149" cy="203" r="3" fill="#cbbdf2"/>
    </svg>'''
    st.markdown('<div class="workspace-topline"><div class="workspace-wordmark"><span class="workspace-logo">u</span>'
                'LEARNING COMPANION</div><span class="workspace-project">PE6203 · GROUP 5</span></div>'
                '<section class="workspace-hero"><div class="hero-copy"><div class="hero-eyebrow">YOUR COURSE LEARNING STUDIO</div>'
                '<h1>UiPath<span>Learning Companion</span></h1><p>' + description + '</p>'
                '<div class="hero-badges"><span>PE6202 · Weeks 1–5</span><span>'
                + ('练习 Weeks 1–4' if zh else 'Practice Weeks 1–4') + '</span><span class="preview-badge">'
                + badge + '</span></div></div>' + art + '</section>', unsafe_allow_html=True)


def render_sidebar_brand(language):
    st.markdown('<div class="sidebar-brand"><span class="workspace-logo">u</span><div>UiPath Companion<small>'
                + ('你的课程学习空间' if language == 'zh' else 'Your course workspace') + '</small></div></div>', unsafe_allow_html=True)


def render_library_counts(counts, language):
    labels = [('concept', '概念卡片', 'Concepts'), ('task', '操作任务', 'Tasks'),
              ('question', '参考例题', 'Examples'), ('official', '官方资料', 'Official sources')]
    cards = ''.join('<div class="library-stat"><strong>' + str(counts[key]) + '</strong><span>'
                    + (zh if language == 'zh' else en) + '</span></div>' for key, zh, en in labels)
    st.markdown('<div class="library-grid">' + cards + '</div>', unsafe_allow_html=True)


def render_footer():
    names = ''.join('<span>' + escape(name) + '</span>' for name in MEMBERS)
    st.markdown('<footer class="course-footer" aria-label="Project credits">'
                '<strong>PE6203 A1 · Group 5</strong><div class="course-members">' + names + '</div>'
                '<small>© 2026 Group 5 · Student coursework project · 非 NTU 官方服务</small></footer>',
                unsafe_allow_html=True)
