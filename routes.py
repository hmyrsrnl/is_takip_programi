from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from models import db, User, Task, TaskHistory, Category, Tag, TaskStatus, TaskPriority, UserRole

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (current_user.is_admin or current_user.role == UserRole.ADMIN.value):
            flash("Bu işlem için yetkiniz yok!", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def can_view_all_tasks():
    return (current_user.is_admin or 
            current_user.role in [UserRole.ADMIN.value])

def can_edit_all_tasks():
    return (current_user.is_admin or 
            current_user.role in [UserRole.ADMIN.value])

def init_routes(app, bcrypt):
    @app.route('/')
    def index():
        return render_template("base.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]

            if User.query.filter_by(email=email).first():
                flash("Email zaten kayıtlı!", "danger")
                return redirect(url_for("register"))

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username=username, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash("Kayıt başarılı! Lütfen giriş yapın.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash("Giriş başarılı!", "success")
                return redirect(url_for("tasks"))

            flash("Email veya şifre hatalı!", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Çıkış yapıldı!", "info")
        return redirect(url_for("login"))

    @app.route("/tasks/add", methods=["GET", "POST"])
    @login_required
    def add_task():
        if can_edit_all_tasks():
            users = User.query.all()
        else:
            users = [current_user]
        
        if request.method == "POST":
            task_name = request.form["task_name"]
            description = request.form["description"]
            status = request.form.get("status", TaskStatus.WAITING.value)
            priority = request.form.get("priority", TaskPriority.MEDIUM.value)

            start_date_str = request.form.get("start_date")
            finish_date_str = request.form.get("finish_date")

            start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
            finish_date = datetime.fromisoformat(finish_date_str) if finish_date_str else None

            if can_edit_all_tasks():
                user_id = request.form.get("user_id", current_user.id)
            else:
                user_id = current_user.id

            task = Task(
                task_name=task_name, 
                description=description, 
                status=status,
                priority=priority,
                user_id=user_id,
                start_date=start_date,
                finish_date=finish_date
            )
            db.session.add(task)
            db.session.commit()
            flash("Görev başarıyla eklendi!", "success")
            return redirect(url_for("tasks"))

        return render_template("add_task.html", 
                             status_options=TaskStatus, 
                             priority_options=TaskPriority,
                             users=users,
                             can_edit_all=can_edit_all_tasks())

    @app.route('/tasks/')
    @login_required
    def tasks():
        if can_view_all_tasks():
            all_tasks = Task.query.all()
        else:
            all_tasks = Task.query.filter_by(user_id=current_user.id).all()
        
        return render_template('tasks.html', 
                             tasks=all_tasks, 
                             TaskStatus=TaskStatus, 
                             TaskPriority=TaskPriority,
                             can_view_all=can_view_all_tasks(),
                             can_edit_all=can_edit_all_tasks())

    @app.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
    @login_required
    def edit_task(task_id):
        task = Task.query.get_or_404(task_id)
        
        if task.user_id != current_user.id and not can_edit_all_tasks():
            flash("Bu görevi düzenleme yetkiniz yok!", "danger")
            return redirect(url_for('tasks'))
        
        if can_edit_all_tasks():
            users = User.query.all()
        else:
            users = [current_user]
        
        if request.method == 'POST':
            changes = []
            
            if task.task_name != request.form['task_name']:
                changes.append(('Görev adı', task.task_name, request.form['task_name']))
                task.task_name = request.form['task_name']
                
            if task.description != request.form['description']:
                changes.append(('Görev Tanımı', task.description, request.form['description']))
                task.description = request.form['description']
                
            if task.status != request.form['status']:
                changes.append(('Görev Durumu', task.status, request.form['status']))
                task.status = request.form['status']
                
            if task.priority != request.form['priority']:
                changes.append(('Görev Önceliği', task.priority, request.form['priority']))
                task.priority = request.form['priority']

            start_date_str = request.form.get('start_date')
            finish_date_str = request.form.get('finish_date')
            
            if start_date_str:
                new_start_date = datetime.fromisoformat(start_date_str)
                if task.start_date != new_start_date:
                    changes.append(('start_date', str(task.start_date), str(new_start_date)))
                    task.start_date = new_start_date
            
            if finish_date_str:
                new_finish_date = datetime.fromisoformat(finish_date_str)
                if task.finish_date != new_finish_date:
                    changes.append(('finish_date', str(task.finish_date), str(new_finish_date)))
                    task.finish_date = new_finish_date
    
            if can_edit_all_tasks():
                new_user_id = request.form.get('user_id', task.user_id)
                if task.user_id != new_user_id:
                    old_user = User.query.get(task.user_id)
                    new_user = User.query.get(new_user_id)
                    changes.append(('user_id', old_user.username, new_user.username))
                    task.user_id = new_user_id

            for field, old_val, new_val in changes:
                history = TaskHistory(
                    task_id=task.id,
                    changed_by=current_user.id,
                    field_name=field,
                    old_value=str(old_val),
                    new_value=str(new_val)
                )
                db.session.add(history)

            
            
            db.session.commit()
            flash('Görev başarıyla güncellendi!', 'success')
            return redirect(url_for('tasks'))
        
        return render_template('edit_task.html', 
                             task=task, 
                             status_options=TaskStatus, 
                             priority_options=TaskPriority,
                             users=users,
                             can_edit_all=can_edit_all_tasks())

    @app.route('/tasks/<int:task_id>')
    @login_required
    def task_detail(task_id):
        task = Task.query.get_or_404(task_id)
        return render_template('task_detail.html', 
                             task=task, 
                             TaskStatus=TaskStatus, 
                             TaskPriority=TaskPriority)

    @app.route('/tasks/delete/<int:task_id>')
    @login_required
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        flash('Görev başarıyla silindi!', 'success')
        return redirect(url_for('tasks'))

    @app.route('/calendar')
    @login_required
    def calendar():
        return render_template('calendar.html')

    @app.route('/search')
    @login_required
    def search():
        query = request.args.get('q', '')
        if query:
            if can_view_all_tasks():
                tasks = Task.query.filter(
                    (Task.task_name.ilike(f'%{query}%')) | 
                    (Task.description.ilike(f'%{query}%'))
                ).all()
            else:
                tasks = Task.query.filter(
                    (Task.task_name.ilike(f'%{query}%')) | 
                    (Task.description.ilike(f'%{query}%'))
                ).filter_by(user_id=current_user.id).all()
        else:
            tasks = []
        return render_template('search.html', tasks=tasks, query=query)

    @app.route('/admin')
    @login_required
    @admin_required
    def admin_panel():
        users = User.query.all()
        return render_template('admin.html', users=users)

    @app.route('/admin/user/add', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_add_user():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']
            
            if User.query.filter_by(email=email).first():
                flash('Bu email zaten kayıtlı!', 'danger')
                return redirect(url_for('admin_add_user'))
            
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(
                username=username,
                email=email,
                password=hashed_password,
                role=role
            )
            db.session.add(user)
            db.session.commit()
            flash('Kullanıcı başarıyla eklendi!', 'success')
            return redirect(url_for('admin_panel'))
        
        return render_template('admin_add_user.html', roles=UserRole)

    @app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_edit_user(user_id):
        user = User.query.get_or_404(user_id)
        
        if request.method == 'POST':
            user.username = request.form['username']
            user.email = request.form['email']
            user.role = request.form['role']
        
            if request.form['password']:
                user.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            
            db.session.commit()
            flash('Kullanıcı başarıyla güncellendi!', 'success')
            return redirect(url_for('admin_panel'))
        
        return render_template('admin_edit_user.html', user=user, roles=UserRole)

    @app.route('/admin/user/delete/<int:user_id>')
    @login_required
    @admin_required
    def admin_delete_user(user_id):
        user = User.query.get_or_404(user_id)
        
        Task.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        flash('Kullanıcı başarıyla silindi!', 'success')
        return redirect(url_for('admin_panel'))

    #-----Backup ve Restore 
    @app.route('/backup')
    @login_required
    @admin_required
    def backup():
        import subprocess
        try:
            result = subprocess.run(['./backup.sh'], capture_output=True, text=True)
            flash(f"Yedekleme başarılı: {result.stdout}", "success")
        except Exception as e:
            flash(f"Yedekleme hatası: {str(e)}", "danger")
        return redirect(url_for('index'))

    @app.route('/restore')
    @login_required
    @admin_required
    def restore_page():
        return render_template('restore.html')

    @app.route('/restore/upload', methods=['POST'])
    @login_required
    @admin_required
    def restore_upload():
        pass