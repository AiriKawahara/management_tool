from flask import Flask, request, flash, jsonify
from google.cloud import datastore
from werkzeug import secure_filename
import os
import csv
import socket

class Blog:
  def __init__(self):
    self.client = datastore.Client('management-tool-y')

  # main.pyから呼び出される関数
  def main_function(self, request):
    self.upload_folder      = './uploads'
    self.allowed_extensions = set(['csv'])

    self.month     = request.form['month']
    self.blog_file = request.files['blog_data']
    self.host_file = request.files['host_data']
    self.blog_file_name = secure_filename(self.blog_file.filename)
    self.host_file_name = secure_filename(self.host_file.filename)
    self.check_blog_ext = '.' in self.blog_file_name and \
      self.blog_file_name.rsplit('.', 1)[1] in self.allowed_extensions
    self.check_host_ext = '.' in self.host_file_name and \
      self.host_file_name.rsplit('.', 1)[1] in self.allowed_extensions

    if self.check_blog_ext is False or self.check_host_ext is False:
      flash('CSVファイルを指定してください。', 'danger')
      return

    self.blog_file_path = os.path.join(self.upload_folder, self.blog_file_name)
    self.host_file_path = os.path.join(self.upload_folder, self.host_file_name)

    self.blog_file.save(self.blog_file_path)
    self.host_file.save(self.host_file_path)

    self.get_exclusion_hosts()
    self.get_blog_data()

    # BOMありなしを判別
    self.line_first  = open(self.blog_file_path, encoding='utf-8').readline()
    self.is_with_bom = self.line_first[0] == '\ufeff'
    self.encoding    = 'utf-8-sig' if self.is_with_bom else 'utf-8'

    self.register_blog()

  # アクセス解析対象外ホスト名を取得
  def get_exclusion_hosts(self):
    self.exclusion_hosts = []
    try:
      with open(self.host_file_path, 'r') as f:
        self.host_reader = csv.reader(f)
        for row in self.host_reader:
          if row:
            self.exclusion_hosts.append(row[0])
    except FileNotFoundError as e:
      print(e)
      flash('アクセス解析対象外ホスト名を取得することができませんでした。', 'danger')
    except csv.Error as e:
      print(e)
      flash('アクセス解析対象外ホスト名を取得することができませんでした。', 'danger')

  # 対象月のブログデータを取得
  def get_blog_data(self):
    query = self.client.query(kind='blog')
    query.add_filter('month', '=', self.month)
    results = list(query.fetch())

    if len(results) > 0:
      self.key = results[0].__dict__['key']
    else:
      self.key = self.client.key('blog')

  # ブログデータをDatastoreに登録する
  def register_blog(self):
    try:
      with open(self.blog_file_path, 'r', encoding=self.encoding) as f:
        self.reader = csv.reader(f)
        self.analysis_blog_data()
        self.task = datastore.Entity(self.key)
        self.task.update({
          'month':             self.month,
          'total_access':      self.blog_data['total_access'],
          'other_user_access': self.blog_data['other_user_access'],
          'posts_count':       self.blog_data['posts_count'],
          'visitors_count':    self.blog_data['visitors_count']
        })
        self.client.put(self.task)
      os.remove(self.blog_file_path)
      os.remove(self.host_file_path)
      flash('ブログデータを登録しました。', 'success')
    except FileNotFoundError as e:
      print(e)
      flash('CSVファイルの読み込みに失敗しました。', 'danger')
    except csv.Error as e:
      print(e)
      flash('CSVファイルの読み込みに失敗しました。', 'danger')
    except:
      flash('予期せぬエラーが発生しました。', 'danger')

  # ブログデータの解析を行う
  def analysis_blog_data(self):
    try:
      self.total_access      = 0
      self.other_user_access = 0
      self.visitors_count    = 0
      self.posts_count       = int(self.line_first.split(',')[3])

      for row in self.reader:
        if row is None:
          continue
        self.total_access += int(row[1])
        try:
          self.host_name = socket.gethostbyaddr(row[0])[0]
          if self.host_name.endswith('.au-net.ne.jp'):
            print(row)
            continue
          elif self.host_name in self.exclusion_hosts:
            print(row)
            continue
          self.other_user_access += int(row[1])
          self.visitors_count    += 1
        except socket.error:
          self.other_user_access += int(row[1])
          self.visitors_count    += 1

      self.blog_data = {
        'total_access':      self.total_access,
        'other_user_access': self.other_user_access,
        'visitors_count':    self.visitors_count,
        'posts_count':       self.posts_count
      }
    except IndexError as e:
      print(e)
      flash('CSVファイルのフォーマットが正しくありません。', 'danger')
    except ValueError as e:
      print(e)
      flash('CSVファイルのフォーマットが正しくありません。', 'danger')
    except:
      flash('予期せぬエラーが発生しました。')

  # ユーザーがブログデータ検索を行った際に実行される関数
  def get_blog(self, request):
    blog_start_month = request.args['blog_start_month']
    blog_end_month   = request.args['blog_end_month']

    query = self.client.query(kind='blog')
    query.add_filter('month', '>=', blog_start_month)
    query.add_filter('month', '<=', blog_end_month)
    results = list(query.fetch())

    if len(results) == 0:
      flash('検索条件に一致するデータが存在しません。', 'warning')

    return jsonify(results)
