"""Prepare structured UI observations for the existing debugging interface."""


def debug_observations(expected, actual, error, language):
    labels = ('预期结果', '实际结果', '报错原文') if language == 'zh' else ('Expected result', 'Observed result', 'Exact error')
    return '\n\n'.join(f'{label}:\n{value.strip()}' for label, value in zip(labels, (expected, actual, error)) if value.strip())


def missing_debug_fields(activity, actual, error, language):
    missing = []
    if not activity.strip():
        missing.append('填写出问题的 Activity 或步骤名称。' if language == 'zh' else 'Enter the activity or step where the issue occurs.')
    if not actual.strip() and not error.strip():
        missing.append('描述实际结果，或粘贴报错原文；没有报错也可以排查。' if language == 'zh' else 'Describe the observed result or paste the exact error. An error message is not required if you describe the issue.')
    return missing
