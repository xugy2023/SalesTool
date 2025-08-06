# routes/analysis.py
from flask import Blueprint, request, render_template, current_app
import os

from utils.hybrid_scorer import HybridIntentScorer
from utils.logger import log_failed_analysis
from utils.scoring import get_combined_score
from utils.transcriber import transcribe_with_speakers
from utils.highlighter import highlight_keywords
from utils.pdf_generator import generate_pdf
from utils.cache import save_analysis, get_analysis
from utils.analyzer import analyze_sales_text, score_transcript

# 导入动态纠错管理
from routes.terminology_management import get_corrector

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        try:
            file = request.files.get('file')
            if not file or file.filename == '':
                return "❌ 未上传文件", 400

            customer = request.form.get('customer_name', '').strip() or "未命名客户"
            filename = file.filename
            filepath = os.path.join('uploads', filename)
            file.save(filepath)

            print(f"✅ 开始转写文件: {filename}")
            transcript_raw = transcribe_with_speakers(filepath)

            if not transcript_raw or not isinstance(transcript_raw, str) or transcript_raw.strip() == "":
                log_failed_analysis(filename, "语音转写失败，未获取到有效文本")
                return render_template(
                    'result.html',
                    filename=filename,
                    transcript=None,
                    customer=customer,
                    feedback={"score": 0, "summary": "❌ 无法获取有效文本内容，语音转写失败。"}
                )

            # 使用动态纠错器进行术语纠错
            print("✅ 开始术语纠错")
            corrector = get_corrector()
            corrected_text = corrector.correct_text(transcript_raw)

            print("✅ 开始关键词高亮")
            transcript = highlight_keywords(corrected_text)

            # 容错处理：如果关键词高亮失败，使用纠错后的文本
            if transcript is None:
                print("⚠️ 关键词高亮失败，使用纠错后的文本")
                transcript = corrected_text

            print("✅ 开始分析销售内容")
            feedback = analyze_sales_text(transcript)

            # 容错处理：如果分析失败，提供默认反馈
            if feedback is None:
                print("⚠️ 销售分析失败，使用默认反馈")
                feedback = {"summary": "分析功能暂时不可用，但转写内容正常。"}

            print("✅ 开始打分")
            feedback = get_combined_score(transcript)

            # 调试信息
            print(f"🐛 调试信息：")
            print(f"原始转写长度: {len(transcript_raw)}")
            print(f"纠错后长度: {len(corrected_text)}")
            print(f"最终transcript长度: {len(transcript) if transcript else 'None'}")

            # 保存结果
            save_analysis(filename, transcript, feedback)

            return render_template(
                'result.html',
                filename=filename,
                transcript=transcript,
                feedback=feedback,
                customer=customer,

            )
        except Exception as e:
            current_app.logger.error(f"[上传处理异常] {e}", exc_info=True)

            # 返回错误信息也渲染 result.html，防止页面挂掉
            return render_template(
                'result.html',
                filename="未知文件",
                transcript=None,
                feedback={
                    "score": 0,
                    "summary": f"❌ 上传失败：{str(e)}"
                },
                customer="未知客户"
            )

    return render_template('upload.html')


@analysis_bp.route('/batch_upload', methods=['GET', 'POST'])
def batch_upload():
    if request.method == 'POST':
        files = request.files.getlist("files")
        customer = request.form.get("customer_name", "").strip() or "未命名客户"
        results = []

        # 获取动态纠错器实例
        corrector = get_corrector()

        for file in files:
            filename = file.filename
            filepath = os.path.join("uploads", filename)
            file.save(filepath)

            transcript_raw = transcribe_with_speakers(filepath)
            if not transcript_raw:
                log_failed_analysis(filename, "语音转写失败，未获取到文本")
                return render_template('result.html',
                                       customer=customer,
                                       transcript=None,
                                       feedback={"score": 0, "summary": "❌ 无法获取有效文本内容，语音转写失败。"})

            # 使用动态纠错器进行术语纠错
            corrected_text = corrector.correct_text(transcript_raw)

            transcript = highlight_keywords(corrected_text)
            if transcript is None:
                transcript = corrected_text

            feedback = analyze_sales_text(transcript)
            if feedback is None:
                feedback = {"summary": "分析功能暂时不可用，但转写内容正常。"}

            score = score_transcript(transcript)
            if score is None:
                score = 0

            feedback["score"] = score

            save_analysis(filename, transcript, feedback)

            results.append({
                "filename": filename,
                "transcript": transcript,
                "feedback": feedback
            })

        return render_template("batch_result.html", results=results)

    return render_template("index.html")


@analysis_bp.route("/export_pdf/<filename>")
def export_pdf(filename):
    result = get_analysis(filename)
    if not result:
        return f"❌ 无法找到名为 {filename} 的分析结果", 404

    return generate_pdf(
        filename,
        result["transcript"],
        result["feedback"]
    )


# 动态添加纠错规则的API接口
@analysis_bp.route('/api/add_correction', methods=['POST'])
def api_add_correction():
    """API接口：动态添加纠错规则"""
    from flask import jsonify

    data = request.get_json()
    if not data or 'wrong_term' not in data:
        return jsonify({'error': '缺少必要参数'}), 400

    wrong_term = data['wrong_term'].strip()
    correct_term = data.get('correct_term', '').strip()

    if not wrong_term:
        return jsonify({'error': '错误词汇不能为空'}), 400

    corrector = get_corrector()
    corrector.add_correction(wrong_term, correct_term)
    corrector.save_dictionary("data/terminology_dictionary.json")

    return jsonify({
        'message': f'成功添加规则: "{wrong_term}" -> "{correct_term}"',
        'total_rules': len(corrector.corrections)
    }), 200
