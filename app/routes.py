import os
from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for, current_app, Markup
)
from werkzeug.utils import secure_filename
from .openai_utils import evaluate_exam
import jinja2

bp = Blueprint('main', __name__)

# Custom Jinja2 filter to convert newlines to <br> tags
try:
    @jinja2.pass_eval_context
    def nl2br(eval_ctx, value):
        result = str(value).replace('\n', '<br>')
        if eval_ctx.autoescape:
            result = Markup(result)  # Using Flask's Markup instead of jinja2.Markup
        return result
except (AttributeError, ImportError):
    # Simpler fallback implementation if the pass_eval_context is not available
    def nl2br(value):
        result = str(value).replace('\n', '<br>')
        try:
            return Markup(result)
        except:
            # Last resort fallback - return string directly
            return result

# Register the filter
bp.add_app_template_filter(nl2br, 'nl2br')

ALLOWED_EXTENSIONS = {'txt', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'exam_file' not in request.files:
            flash('沒有選擇檔案')
            return redirect(request.url)

        file = request.files['exam_file']

        # If user does not select file, browser submits an empty part without filename
        if file.filename == '':
            flash('沒有選擇檔案')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Get file extension
            file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

            # For text files, read content directly
            if file_extension == 'txt':
                with open(filepath, 'r') as f:
                    exam_content = f.read()
                # Send to OpenAI for evaluation
                result = evaluate_exam(exam_content=exam_content)
            # For image files, pass the file path directly
            elif file_extension in ['jpg', 'jpeg', 'png']:
                # Send to OpenAI for evaluation with image processing
                result = evaluate_exam(exam_content='', file_path=filepath, file_type=file_extension)
            else:
                flash('不支援的檔案格式，請上傳 .txt, .jpg, .jpeg 或 .png 檔案')
                return redirect(url_for('main.index'))

            if result['success']:
                # Pass the file info to the template if it's an image
                file_info = None
                if file_extension in ['jpg', 'jpeg', 'png']:
                    file_info = {
                        'path': '/'.join(['static', 'uploads', filename]),
                        'type': file_extension
                    }
                # Get available filters to allow for template fallbacks
                available_filters = current_app.jinja_env.filters.keys() if hasattr(current_app, 'jinja_env') else []
                return render_template('result.html', result=result['result'], file_info=file_info, filters=available_filters)
            else:
                error_message = result.get("error", "未知錯誤")
                print(f"API Error: {error_message}")
                flash(f'評分過程中發生錯誤: {error_message}', 'error')
                available_filters = current_app.jinja_env.filters.keys() if hasattr(current_app, 'jinja_env') else []
                return render_template('error.html', error=error_message, file_path=filepath, filters=available_filters)
        else:
            flash('不支援的檔案格式')
            return redirect(request.url)

    return render_template('index.html')