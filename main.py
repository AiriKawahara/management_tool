from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, session
from google.cloud import datastore
import hashlib
import random
import string

app = Flask(__name__)

CLIENT = datastore.Client('management-tool-y')
JST = timezone(timedelta(hours=+9), 'JST')

# ログイン画面
@app.route('/')
def top():
  if authentication_check():
    return redirect('/schedule')
  else:
    return render_template('login.html', title='LOGIN', error=False)

# ログイン処理
@app.route('/login', methods=['POST'])
def login():
  login_id = request.form['login_id']
  password = request.form['password']
  login_check = user_exists(login_id, password)

  if login_check:
    return redirect('/schedule')
  else:
    return redirect('/login')

# ログインエラーの場合は再度ログイン画面を表示
@app.route('/login')
def login_failed():
  return render_template('login.html', title='LOGIN', error=True)

# ログアウト処理
@app.route('/logout')
def logout():
  if 'login_token' in session:
    session.pop('login_token', None)
  return redirect('/')

# スケジュール画面
@app.route('/schedule')
def schedule():
  if authentication_check():
    return render_template('schedule.html', title='SCHEDULE')
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
  try:
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
  except:
    print("Unexpected error:" + sys.exc_info()[0])
    raise

# 認証チェックを行う
def authentication_check():
  if not 'login_token' in session:
    return False

  # セッションに保存されているトークンが有効かどうか確認
  delete_token()
  login_token = session['login_token']
  query = CLIENT.query(kind='auth')
  query.add_filter('token', '=', login_token)
  try:
    results = list(query.fetch())
    if len(results) == 0:
      return False
    else:
      return True
  except:
    print("Unexpected error:" + sys.exc_info()[0])
    raise

# 有効期限切れのトークンをDatastoreから削除
def delete_token():
  now = datetime.now(JST)
  query = CLIENT.query(kind='auth')
  query.add_filter('expiration_datetime', '<', now)
  try:
    targets = list(query.fetch())
    for target in targets:
      key = target.__dict__['key']
      CLIENT.delete(key)
  except:
    print("Unexpected error:" + sys.exc_info()[0])
    raise

if __name__ == '__main__':
  app.secret_key = 'some secret key'
  app.run(host='0.0.0.0')
