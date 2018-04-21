from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug import secure_filename
from google.cloud import datastore
import hashlib
import random
import string
import os
import csv
import socket

app = Flask(__name__)
app.secret_key = 'some secret key'

CLIENT = datastore.Client('management-tool-y')
JST = timezone(timedelta(hours=+9), 'JST')
CATEGORIES = ['danger', 'warning', 'success']

# ログイン画面
@app.route('/')
def top():
  if authentication_check():
    return redirect('/task')
  else:
    return render_template(
      'login.html',
      title='ログイン',
      categories=CATEGORIES)

# ログイン処理
@app.route('/login', methods=['POST'])
def login():
  login_id = request.form['login_id']
  password = request.form['password']
  login_check = user_exists(login_id, password)

  if login_check:
    return redirect('/task')
  else:
    flash('ログインIDまたはパスワードが不正です。', 'danger')
    return redirect('/')

# ログアウト処理
@app.route('/logout')
def logout():
  if 'login_token' in session:
    session.pop('login_token', None)
  return redirect('/')

# タスク管理画面
@app.route('/task')
def task():
  if not authentication_check():
    return redirect('/')

  # 今日の日付を取得
  today = (datetime.now(JST)).strftime("%Y-%m-%d")

  # 検索対象日の取得
  start_date = request.args.get('start_date_input', default=None)
  end_date = request.args.get('end_date_input', default=None)

  # すべてのタスクを取得
  query = CLIENT.query(kind='task')
  all_tasks = list(query.fetch())

  everyday_tasks = get_everyday_tasks(all_tasks)
  expired_tasks = get_expired_tasks(all_tasks, today)
  danger_tasks = get_danger_tasks(all_tasks, today)
  other_tasks = get_other_tasks(all_tasks, today)
  if start_date and end_date:
    search_tasks = get_search_tasks(all_tasks, start_date, end_date)
    if len(search_tasks) == 0:
      flash('検索条件に一致するタスクが存在しません。', 'warning')
  else:
    search_tasks = []

  return render_template(
    'task.html',
    title='タスク管理',
    everyday_tasks=everyday_tasks,
    expired_tasks=expired_tasks,
    danger_tasks=danger_tasks,
    other_tasks=other_tasks,
    search_tasks=search_tasks,
    categories=CATEGORIES)

# タスク登録
@app.route('/register_task', methods=['POST'])
def register_task():
  task_name = request.form['task_name_input']
  deadline = request.form['deadline_input']

  # すでに同じタスクが登録されている場合は登録しない
  query = CLIENT.query(kind='task')
  query.add_filter('task_name', '=', task_name)
  query.add_filter('deadline', '=', deadline)
  tasks = list(query.fetch())
  if len(tasks) > 0:
    flash('すでに同じタスクが登録されています。', 'danger')
    return redirect('/task')

  key = CLIENT.key('task')
  task = datastore.Entity(key)
  task.update({
    'task_name': task_name,
    'deadline': deadline
  })
  CLIENT.put(task)
  flash('タスクを登録しました。', 'success')
  return redirect('/task')

# タスク完了
@app.route('/complete_task', methods=['POST'])
def complete_task():
  task_name = request.form['task_name']
  deadline = request.form['deadline']
  complete_date = request.form['complete_date']

  # 実績登録
  key = CLIENT.key('treated')
  task = datastore.Entity(key)
  task.update({
    'task_name': task_name,
    'treated_date': complete_date,
    'deadline': deadline
  })
  CLIENT.put(task)

  # タスク削除
  query = CLIENT.query(kind='task')
  query.add_filter('task_name', '=', task_name)
  query.add_filter('deadline', '=', deadline)
  target = list(query.fetch())
  if len(target) > 0:
    key = target[0].__dict__['key']
    CLIENT.delete(key)
  flash('タスクを完了しました。', 'success')
  return redirect('/task')

# タスク編集
@app.route('/edit_task', methods=['POST'])
def edit_task():
  old_task_name = request.form['old_task_name']
  new_task_name = request.form['new_task_name']
  old_deadline = request.form['old_deadline']
  new_deadline = request.form['new_deadline']

  query = CLIENT.query(kind='task')
  query.add_filter('task_name', '=', old_task_name)
  query.add_filter('deadline', '=', old_deadline)
  target = list(query.fetch())

  if len(target) == 0:
    flash('タスクの更新に失敗しました。', 'danger')
    return redirect('/task')

  key = target[0].__dict__['key']
  task = datastore.Entity(key)
  task.update({
    'task_name': new_task_name,
    'deadline': new_deadline
  })
  CLIENT.put(task)
  flash('タスクを更新しました。', 'success')
  return redirect('/task')

# タスク削除
@app.route('/delete_task', methods=['POST'])
def delete_task():
  task_name = request.form['task_name']
  deadline = request.form['deadline']

  query = CLIENT.query(kind='task')
  query.add_filter('task_name', '=', task_name)
  query.add_filter('deadline', '=', deadline)
  target = list(query.fetch())

  if len(target) == 0:
    flash('タスクの削除に失敗しました。', 'danger')
    return redirect('/task')

  key = target[0].__dict__['key']
  CLIENT.delete(key)
  flash('タスクを削除しました。', 'success')
  return redirect('/task')

# 実績画面
@app.route('/treated')
def treated():
  if authentication_check():
    return render_template(
      'treated.html',
      title='実績',
      categories=CATEGORIES)
  else:
    return redirect('/')

# トレーニング画面
@app.route('/training')
def training():
  if authentication_check():
    return render_template(
      'training.html',
      title='トレーニング',
      categories=CATEGORIES)
  else:
    return redirect('/')

# 体型管理画面
@app.route('/figure')
def figure():
  if authentication_check():
    return render_template(
      'figure.html',
      title='体型管理',
      categories=CATEGORIES)
  else:
    return redirect('/')

# 体型情報登録
@app.route('/register_figure', methods=['POST'])
def register_figure():
  thickness_r = float(request.form['thickness_r']) if request.form['thickness_r'] else None
  thickness_l = float(request.form['thickness_l']) if request.form['thickness_l'] else None
  figure_date = request.form['figure_date']        if request.form['figure_date'] else None

  query = CLIENT.query(kind='figure')
  query.add_filter('figure_date', '=', figure_date)
  results = list(query.fetch())

  if len(results) > 0:
    key = results[0].__dict__['key']
    # 入力値が空の場合はDBの値を保持する
    thickness_r = thickness_r if thickness_r else results[0]['right_thickness']
    thickness_l = thickness_l if thickness_l else results[0]['left_thickness']
  else:
    key = CLIENT.key('figure')

  task = datastore.Entity(key)
  task.update({
    'right_thickness': thickness_r,
    'left_thickness': thickness_l,
    'figure_date': figure_date
  })
  CLIENT.put(task)
  flash('体型情報を登録しました。', 'success')
  return redirect('/figure')

#体型情報取得
@app.route('/get_figure', methods=['GET'])
def get_figure():
  figure_start_date = request.args['figure_start_date']
  figure_end_date   = request.args['figure_end_date']

  query = CLIENT.query(kind='figure')
  query.add_filter('figure_date', '>=', figure_start_date)
  query.add_filter('figure_date', '<=', figure_end_date)
  results = list(query.fetch())

  if len(results) == 0:
    flash('検索条件に一致するデータが存在しません。', 'warning')
  
  return jsonify(results)

# ブログ管理画面
@app.route('/blog')
def blog():
  if authentication_check():
    return render_template(
      'blog.html',
      title='ブログ管理',
      categories=CATEGORIES)
  else:
    return redirect('/')

# ブログデータ登録
@app.route('/register_blog', methods=['POST'])
def register_blog():
  UPLOAD_FOLDER = './uploads'
  ALLOWED_EXTENSIONS = set(['csv'])
  LIST_FILE = 'exclusion_list.csv'

  month = request.form['month']
  input_file = request.files['blog_data']
  filename = secure_filename(input_file.filename)
  check_extension = '.' in filename and \
    filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

  if check_extension is False:
    flash('CSVファイルを指定してください。', 'danger')
    return redirect('/blog')

  exclusion_hosts = get_exclusion_hosts(LIST_FILE)
  key = get_blog_data(month)
  file_path = os.path.join(UPLOAD_FOLDER, filename)
  input_file.save(file_path)

  # BOMありなしを見分ける
  line_first = open(file_path, encoding='utf-8').readline()
  is_with_bom = line_first[0] == '\ufeff'
  encoding = 'utf-8-sig' if is_with_bom else 'utf-8'

  try:
    with open(file_path, 'r', encoding=encoding) as f:
      reader = csv.reader(f)
      blog_data = analysis_blog_data(reader, exclusion_hosts)
      task = datastore.Entity(key)
      task.update({
        'month': month,
        'total_access': blog_data['total_access'],
        'other_user_access': blog_data['other_user_access'],
        'posts_count': blog_data['posts_count'],
        'visitors_count': blog_data['visitors_count']
      })
      CLIENT.put(task)
    flash('ブログデータを登録しました。', 'success')
    return redirect('/blog')
  except FileNotFoundError as e:
    print(e)
    flash('CSVファイルの読み込みに失敗しました。', 'danger')
    return redirect('/blog')
  except csv.Error as e:
    print(e)
    flash('CSVファイルの読み込みに失敗しました。', 'danger')
    return redirect('/blog')

# ユーザーの存在チェック
def user_exists(login_id, password):
  # 入力されたパスワードを暗号化
  encode_password = password.encode('utf-8')
  hashed_password = hashlib.sha256(encode_password).hexdigest()
  
  query = CLIENT.query(kind='users')
  query.add_filter('login_id', '=', login_id)
  query.add_filter('password', '=', hashed_password)
  users = list(query.fetch())

  if len(users) == 0:
    return False
  else:
    # トークンを生成
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    token = ''.join([random.choice(letters) for _ in range(32)])
    expiration_datetime = datetime.now(JST) + timedelta(days=+1)

    # トークンが既にDatastoreに登録されていないかチェック
    delete_token()
    query = CLIENT.query(kind='auth')
    query.add_filter('token', '=', token)
    results = list(query.fetch())

    if len(results) != 0:
      print("Token duplication error")
      return False

    # トークンを保存(有効期限は24時間)
    key = CLIENT.key('auth')
    task = datastore.Entity(key)
    task.update({
      'login_id': login_id,
      'token': token,
      'expiration_datetime': expiration_datetime
    })
    CLIENT.put(task)
    # セッションにトークンを保存
    session['login_token'] = token
    return True

# 認証チェックを行う
def authentication_check():
  if not 'login_token' in session:
    return False

  # セッションに保存されているトークンが有効かどうか確認
  delete_token()
  login_token = session['login_token']
  query = CLIENT.query(kind='auth')
  query.add_filter('token', '=', login_token)
  results = list(query.fetch())

  if len(results) == 0:
    return False
  else:
    return True

# 有効期限切れのトークンをDatastoreから削除
def delete_token():
  now = datetime.now(JST)
  query = CLIENT.query(kind='auth')
  query.add_filter('expiration_datetime', '<', now)
  targets = list(query.fetch())

  for target in targets:
    key = target.__dict__['key']
    CLIENT.delete(key)

# 毎日のタスクを取得
def get_everyday_tasks(all_tasks):
  const_day = '2099-12-31'
  results = []
  for task in all_tasks:
    if task['deadline'] == const_day:
      results.append(task)
  return results

# 期限切れのタスクを取得
def get_expired_tasks(all_tasks, today):
  results = []
  for task in all_tasks:
    if task['deadline'] < today:
      results.append(task)
  return sorted(results,key=lambda x:x["deadline"])

# 今日までのタスクを取得
def get_danger_tasks(all_tasks, today):
  results = []
  for task in all_tasks:
    if task['deadline'] == today:
      results.append(task)
  return results

# 期日が今日以降のタスクを取得
def get_other_tasks(all_tasks, today):
  const_day = '2099-12-31'
  results = []
  for task in all_tasks:
    if task['deadline'] > today and task['deadline'] != const_day:
      results.append(task)
  return sorted(results,key=lambda x:x["deadline"])

# 検索範囲内のタスクを取得
def get_search_tasks(all_tasks, start_date, end_date):
  results = []
  for task in all_tasks:
    if task['deadline'] >= start_date and task['deadline'] <= end_date:
      results.append(task)
  return sorted(results,key=lambda x:x["deadline"])

# アクセス解析対象外ホスト名を取得
def get_exclusion_hosts(file_path):
  exclusion_hosts = []
  try:
    with open(file_path, 'r') as f:
      reader = csv.reader(f)
      for row in reader:
        if row:
          exclusion_hosts.append(row[0])
  except FileNotFoundError as e:
    print(e)
    flash('アクセス解析対象外ホスト名を取得することができませんでした。', 'danger')
  except csv.Error as e:
    print(e)
    flash('アクセス解析対象外ホスト名を取得することができませんでした。', 'danger')
  return exclusion_hosts

# 対象月のブログデータを取得
def get_blog_data(month):
  query = CLIENT.query(kind='blog')
  query.add_filter('month', '=', month)
  results = list(query.fetch())

  if len(results) > 0:
    key = results[0].__dict__['key']
  else:
    key = CLIENT.key('blog')

  return key

# ブログデータの解析を行う
def analysis_blog_data(reader, exclusion_hosts):
  total_access = 0
  other_user_access = 0
  visitors_count = 0
  posts_count = None

  for row in reader:
    total_access += int(row[1])
    if row[3]:
      posts_count = row[3]
    try:
      host_name = socket.gethostbyaddr(row[0])[0]
      if host_name.endswith('.au-net.ne.jp'):
        continue
      elif host_name in exclusion_hosts:
        continue
      other_user_access += int(row[1])
      visitors_count += 1
    except socket.error:
      other_user_access += int(row[1])
      visitors_count += 1

  blog_data = {'total_access': total_access,
    'other_user_access': other_user_access,
    'visitors_count': visitors_count,
    'posts_count': posts_count}
  return blog_data

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)
