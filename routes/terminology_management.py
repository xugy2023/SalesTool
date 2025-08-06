# routes/terminology_management.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
import os
from utils.terminology_corrector import TerminologyCorrector

terminology_bp = Blueprint('terminology', __name__)

# 全局纠错器实例
corrector = TerminologyCorrector("data/terminology_dictionary.json")


@terminology_bp.route('/terminology/manage')
def manage_terminology():
    """术语管理页面"""
    stats = corrector.get_correction_stats()
    return render_template('terminology.html',
                           corrections=corrector.corrections,
                           stats=stats)


@terminology_bp.route('/terminology/add', methods=['POST'])
def add_terminology():
    """添加新的纠错规则"""
    wrong_term = request.form.get('wrong_term', '').strip()
    correct_term = request.form.get('correct_term', '').strip()

    if not wrong_term:
        flash('错误词汇不能为空！', 'error')
        return redirect(url_for('terminology.manage_terminology'))

    # 添加纠错规则
    corrector.add_correction(wrong_term, correct_term)

    # 保存到文件
    corrector.save_dictionary("data/terminology_dictionary.json")

    flash(f'成功添加纠错规则: "{wrong_term}" -> "{correct_term}"', 'success')
    return redirect(url_for('terminology.manage_terminology'))


@terminology_bp.route('/terminology/delete', methods=['POST'])
def delete_terminology():
    """删除纠错规则"""
    wrong_term = request.form.get('wrong_term', '').strip()

    if wrong_term in corrector.corrections:
        del corrector.corrections[wrong_term]
        corrector.save_dictionary("data/terminology_dictionary.json")
        flash(f'成功删除纠错规则: "{wrong_term}"', 'success')
    else:
        flash(f'未找到纠错规则: "{wrong_term}"', 'error')

    return redirect(url_for('terminology.manage_terminology'))


@terminology_bp.route('/terminology/edit', methods=['POST'])
def edit_terminology():
    """编辑纠错规则"""
    old_wrong_term = request.form.get('old_wrong_term', '').strip()
    new_wrong_term = request.form.get('new_wrong_term', '').strip()
    new_correct_term = request.form.get('new_correct_term', '').strip()

    if not new_wrong_term:
        flash('错误词汇不能为空！', 'error')
        return redirect(url_for('terminology.manage_terminology'))

    # 删除旧规则
    if old_wrong_term in corrector.corrections:
        del corrector.corrections[old_wrong_term]

    # 添加新规则
    corrector.add_correction(new_wrong_term, new_correct_term)
    corrector.save_dictionary("data/terminology_dictionary.json")

    flash(f'成功更新纠错规则: "{new_wrong_term}" -> "{new_correct_term}"', 'success')
    return redirect(url_for('terminology.manage_terminology'))


@terminology_bp.route('/terminology/batch_add', methods=['POST'])
def batch_add_terminology():
    """批量添加纠错规则"""
    batch_text = request.form.get('batch_text', '').strip()

    if not batch_text:
        flash('批量添加内容不能为空！', 'error')
        return redirect(url_for('terminology.manage_terminology'))

    lines = batch_text.split('\n')
    added_count = 0

    for line in lines:
        line = line.strip()
        if not line or '->' not in line:
            continue

        try:
            wrong_term, correct_term = line.split('->', 1)
            wrong_term = wrong_term.strip()
            correct_term = correct_term.strip()

            if wrong_term:
                corrector.add_correction(wrong_term, correct_term)
                added_count += 1
        except Exception as e:
            flash(f'解析失败的行: "{line}" - {e}', 'warning')

    if added_count > 0:
        corrector.save_dictionary("data/terminology_dictionary.json")
        flash(f'成功批量添加 {added_count} 条纠错规则', 'success')
    else:
        flash('没有成功添加任何规则', 'error')

    return redirect(url_for('terminology.manage_terminology'))


@terminology_bp.route('/terminology/test', methods=['POST'])
def test_terminology():
    """测试纠错功能"""
    test_text = request.form.get('test_text', '').strip()

    if not test_text:
        return jsonify({'error': '测试文本不能为空'})

    corrected_text = corrector.correct_text(test_text)
    print("纠错前：", test_text)
    print("纠错后：", corrected_text)

    return jsonify({
        'original': test_text,
        'corrected': corrected_text,
        'changed': test_text != corrected_text
    })


@terminology_bp.route('/terminology/export')
def export_terminology():
    """导出纠错字典"""
    from flask import make_response
    import json

    # 创建JSON响应
    response = make_response(json.dumps(corrector.corrections, ensure_ascii=False, indent=2))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=terminology_dictionary.json'

    return response


@terminology_bp.route('/terminology/import', methods=['POST'])
def import_terminology():
    """导入纠错字典"""
    if 'file' not in request.files:
        flash('没有选择文件！', 'error')
        return redirect(url_for('terminology.manage_terminology'))

    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件！', 'error')
        return redirect(url_for('terminology.manage_terminology'))

    if file and file.filename.endswith('.json'):
        try:
            import json
            content = file.read().decode('utf-8')
            imported_dict = json.loads(content)

            # 合并字典
            old_count = len(corrector.corrections)
            corrector.corrections.update(imported_dict)
            new_count = len(corrector.corrections)

            # 保存更新后的字典
            corrector.save_dictionary("data/terminology_dictionary.json")

            flash(f'成功导入 {new_count - old_count} 条新规则，当前共有 {new_count} 条规则', 'success')
        except Exception as e:
            flash(f'导入失败: {e}', 'error')
    else:
        flash('请选择有效的JSON文件！', 'error')

    return redirect(url_for('terminology.manage_terminology'))


# 获取全局纠错器实例的函数
def get_corrector():
    """获取全局纠错器实例"""
    return corrector