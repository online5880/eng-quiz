from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        api_key = request.form.get('openai_api_key')
        if api_key and api_key.startswith('sk-'):
            session['openai_api_key'] = api_key
            flash('API 키가 성공적으로 저장되었습니다. (브라우저 세션에만 임시 저장됩니다)')
        else:
            flash('유효하지 않은 API 키입니다.')
        return redirect(url_for('settings.index'))
        
    return render_template('settings/index.html')