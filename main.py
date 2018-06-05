from datetime     import datetime, timedelta, timezone
from flask        import Flask, render_template, request, redirect, session, flash
from google.cloud import datastore
from common       import Common
from task         import Task
from memo         import Memo
from figure       import Figure
from blog         import Blog

app = Flask(__name__)
app.secret_key = 'some secret key'

CLIENT = datastore.Client('management-tool-y')
JST = timezone(timedelta(hours=+9), 'JST')
CATEGORIES = ['danger', 'warning', 'success']

# ログイン画面
@app.route('/')
def top():
  common = Common()
  if common.authentication_check():
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
  common = Common()
  login_check = common.user_exists(login_id, password)

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
  common = Common()
  if not common.authentication_check():
    return redirect('/')

  # 今日の日付を取得
  today = (datetime.now(JST)).strftime("%Y-%m-%d")

  # 検索対象日の取得
  start_date = request.args.get('start_date_input', default=None)
  end_date = request.args.get('end_date_input', default=None)

  # すべてのタスクを取得
  query = CLIENT.query(kind='task')
  all_tasks = list(query.fetch())

  task = Task()
  everyday_tasks = task.get_everyday_tasks(all_tasks)
  expired_tasks  = task.get_expired_tasks(all_tasks, today)
  danger_tasks   = task.get_danger_tasks(all_tasks, today)
  other_tasks    = task.get_other_tasks(all_tasks, today)
  if start_date and end_date:
    search_tasks = task.get_search_tasks(all_tasks, start_date, end_date)
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
  task = Task()
  task.register_task(request)
  return redirect('/task')

# タスク完了
@app.route('/complete_task', methods=['POST'])
def complete_task():
  task = Task()
  task.complete_task(request)
  return redirect('/task')

# タスク編集
@app.route('/edit_task', methods=['POST'])
def edit_task():
  task = Task()
  task.edit_task(request)
  return redirect('/task')

# タスク削除
@app.route('/delete_task', methods=['POST'])
def delete_task():
  task = Task()
  task.delete_task(request)
  return redirect('/task')

# 実績画面
@app.route('/treated')
def treated():
  common = Common()
  if not common.authentication_check():
    return redirect('/')

  query   = CLIENT.query(kind='treated')
  results = list(query.fetch())
  results = sorted(results,key=lambda x:x["treated_date"],reverse=True)
  return render_template(
    'treated.html',
    title='実績',
    tasks=results,
    categories=CATEGORIES)

# メモ帳画面
@app.route('/memo')
def memo():
  common = Common()
  if not common.authentication_check():
    return redirect('/')

  memo = Memo()
  results = memo.get_memo()

  return render_template(
    'memo.html',
    title='メモ帳',
    memo=results,
    categories=CATEGORIES)

# メモ登録
@app.route('/register_memo', methods=['POST'])
def register_memo():
  memo = Memo()
  memo.register_memo(request)
  return redirect('/memo')

# トレーニング画面
@app.route('/training')
def training():
  common = Common()
  if common.authentication_check():
    return render_template(
      'training.html',
      title='トレーニング',
      categories=CATEGORIES)
  else:
    return redirect('/')

# 体型管理画面
@app.route('/figure')
def figure():
  common = Common()
  if common.authentication_check():
    return render_template(
      'figure.html',
      title='体型管理',
      categories=CATEGORIES)
  else:
    return redirect('/')

# 体型情報登録
@app.route('/register_figure', methods=['POST'])
def register_figure():
  figure = Figure()
  figure.register_figure(request)
  return redirect('/figure')

#体型情報取得
@app.route('/get_figure', methods=['GET'])
def get_figure():
  figure = Figure()
  data = figure.get_figure(request)
  return data

# ブログ管理画面
@app.route('/blog')
def blog():
  common = Common()
  if common.authentication_check():
    return render_template(
      'blog.html',
      title='ブログ管理',
      categories=CATEGORIES)
  else:
    return redirect('/')

# ブログデータ登録
@app.route('/register_blog', methods=['POST'])
def register_blog():
  blog = Blog()
  blog.main_function(request)
  return redirect('/blog')

# ブログデータ取得
@app.route('/get_blog', methods=['GET'])
def get_blog():
  blog = Blog()
  data = blog.get_blog(request)
  return data

# 持ち物リスト画面
@app.route('/belongings')
def belongings():
  common = Common()
  if common.authentication_check():
    return render_template(
      'belongings.html',
      title='持ち物リスト')
  else:
    return redirect('/')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)
