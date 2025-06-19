from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user
from sqlalchemy import or_
from . import bp
from app import db
from app.models import User, Role
from app.decorators import admin_required
from app.admin.forms import EditUserProfileAdminForm


@bp.route('/users')
@admin_required
def list_users():
    query = User.query
    search_term = request.args.get('q')

    if search_term:
        # Филтрираме по потребителско име ИЛИ по имейл
        # or_() ни позволява да комбинираме няколко условия
        query = query.filter(or_(
            User.username.ilike(f'%{search_term}%'),
            User.email.ilike(f'%{search_term}%')
        ))

    # Изпълняваме финалната заявка
    users = query.order_by(User.created_at.desc()).all()

    # --- ДОБАВИ ТАЗИ ЛОГИКА ЗА СТАТИСТИКА ---
    total_users = User.query.count()
    confirmed_users = User.query.filter_by(email_confirmed=True).count()
    # ----------------------------------------

    return render_template('admin/users.html',
                           users=users,
                           title="Управление на потребители",
                           total_users=total_users,
                           confirmed_users=confirmed_users)


@bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Профилът е обновен успешно.', 'success')
        return redirect(url_for('admin.list_users'))

    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role_id
    return render_template('admin/edit_user.html', form=form, user=user, title="Редакция на потребител")


@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    # Не позволявай администратор да изтрие себе си
    if user == current_user:
        flash('Не можете да изтриете собствения си акаунт.', 'danger')
        return redirect(url_for('admin.list_users'))
    db.session.delete(user)
    db.session.commit()
    flash('Потребителят е изтрит успешно.', 'success')
    return redirect(url_for('admin.list_users'))