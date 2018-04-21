from datetime import datetime, timedelta, timezone
from flask import Flask, session
from google.cloud import datastore
import hashlib
import random
import string

JST = timezone(timedelta(hours=+9), 'JST')

class Common:
  def __init__(self):
    self.client = datastore.Client('management-tool-y')

  # ユーザーの存在チェック
  def user_exists(self, login_id, password):
    # 入力されたパスワードを暗号化
    encode_password = password.encode('utf-8')
    hashed_password = hashlib.sha256(encode_password).hexdigest()
    
    query = self.client.query(kind='users')
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
      self.delete_token()
      query = self.client.query(kind='auth')
      query.add_filter('token', '=', token)
      results = list(query.fetch())

      if len(results) != 0:
        print("Token duplication error")
        return False

      # トークンを保存(有効期限は24時間)
      key = self.client.key('auth')
      task = datastore.Entity(key)
      task.update({
        'login_id': login_id,
        'token': token,
        'expiration_datetime': expiration_datetime
      })
      self.client.put(task)
      # セッションにトークンを保存
      session['login_token'] = token
      return True

  # 認証チェックを行う
  def authentication_check(self):
    if not 'login_token' in session:
      return False

    # セッションに保存されているトークンが有効かどうか確認
    self.delete_token()
    login_token = session['login_token']
    query = self.client.query(kind='auth')
    query.add_filter('token', '=', login_token)
    results = list(query.fetch())

    if len(results) == 0:
      return False
    else:
      return True

  # 有効期限切れのトークンをDatastoreから削除
  def delete_token(self):
    now = datetime.now(JST)
    query = self.client.query(kind='auth')
    query.add_filter('expiration_datetime', '<', now)
    targets = list(query.fetch())

    for target in targets:
      key = target.__dict__['key']
      self.client.delete(key)