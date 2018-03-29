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
  authentication_check()
  return render_template('login.html', title='LOGIN', error=False)

# ログインエラーの際は再度ログイン画面を表示する
@app.route('/login', methods=['POST'])
def login():
  login_id = request.form['login_id']
  password = request.form['password']
  login_check = user_exists(login_id, password)

  if login_check:
    return redirect('/schedule')
  else:
    return render_template('login.html', title='LOGIN', error=True)

# スケジュール画面
@app.route('/schedule')
def schedule():
  authentication_check()
  return render_template('schedule.html', title='SCHEDULE')

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
    # トークンを保存(有効期限は24時間)
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    token = ''.join([random.choice(letters) for _ in range(32)])
    expiration_datetime = datetime.now(JST) + timedelta(days=+1)
    key = CLIENT.key('auth')
    task = datastore.Entity(key)
    task.update({
      'login_id': login_id,
      'token': token,
      'expiration_datetime': expiration_datetime
    })
    CLIENT.put(task)

    # セッションにログイン情報を保存
    
    return True

# 認証チェックを行う
def authentication_check():
  token = session.get('token')
  print(token)

if __name__ == '__main__':
  app.secret_key = 'some secret key'
  app.run(host='0.0.0.0')
