from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, session
from google.cloud import datastore
import hashlib
import random
import string

app = Flask(__name__)
app.secret_key = 'some secret key'

CLIENT = datastore.Client('management-tool-y')
JST = timezone(timedelta(hours=+9), 'JST')

# ログイン画面
@app.route('/')
def top():
  if authentication_check():
    return redirect('/task')
  else:
    return render_template(
      'login.html',
      title='ログイン',
      login=True, error=False)

# ログイン処理
@app.route('/login', methods=['POST'])
def login():
  login_id = request.form['login_id']
  password = request.form['password']
  login_check = user_exists(login_id, password)

  if login_check:
    return redirect('/task')
  else:
    return redirect('/login')

# ログインエラーの場合は再度ログイン画面を表示
@app.route('/login')
def login_failed():
  if authentication_check():
    return redirect('/task')
  else:
    return render_template(
      'login.html',
      title='ログイン',
      login=True,
      error=True)

# ログアウト処理
@app.route('/logout')
def logout():
  if 'login_token' in session:
    session.pop('login_token', None)
  return redirect('/')

# タスク管理画面
@app.route('/task', methods=['GET'])
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
  else:
    search_tasks = []

  return render_template(
    'task.html',
    title='タスク管理',
    everyday_tasks=everyday_tasks,
    expired_tasks=expired_tasks,
    danger_tasks=danger_tasks,
    other_tasks=other_tasks,
    search_tasks=search_tasks)

# 計画登録
@app.route('/register_task', methods=['POST'])
def register_task():
  task_name = request.form['task_name_input']
  deadline = request.form['deadline_input']
  key = CLIENT.key('task')
  task = datastore.Entity(key)
  task.update({
    'task_name': task_name,
    'deadline': deadline
  })
  CLIENT.put(task)
  return redirect('/task')

# 計画完了
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

  # 計画削除
  query = CLIENT.query(kind='task')
  query.add_filter('task_name', '=', task_name)
  query.add_filter('deadline', '=', deadline)
  target = list(query.fetch())
  key = target[0].__dict__['key']
  CLIENT.delete(key)
  return redirect('/task')

# 計画削除
@app.route('/delete_task', methods=['POST'])
def delete_task():
  print('aaa')

# 実績画面
@app.route('/treated')
def treated():
  if authentication_check():
    return render_template('treated.html', title='実績')
  else:
    return redirect('/')

# トレーニング画面
@app.route('/training')
def training():
  if authentication_check():
    return render_template('training.html', title='トレーニング')
  else:
    return redirect('/')

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
  return results

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
  return results

# 検索範囲内のタスクを取得
def get_search_tasks(all_tasks, start_date, end_date):
  results = []
  for task in all_tasks:
    if task['deadline'] >= start_date and task['deadline'] <= end_date:
      results.append(task)
  return results

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)
