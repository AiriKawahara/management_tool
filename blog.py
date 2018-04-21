from flask import Flask
from google.cloud import datastore
import csv
import socket

class Blog:
  def __init__(self):
    self.client = datastore.Client('management-tool-y')

  # アクセス解析対象外ホスト名を取得
  def get_exclusion_hosts(self, file_path):
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
  def get_blog_data(self, month):
    query = self.client.query(kind='blog')
    query.add_filter('month', '=', month)
    results = list(query.fetch())

    if len(results) > 0:
      key = results[0].__dict__['key']
    else:
      key = self.client.key('blog')

    return key

  # ブログデータの解析を行う
  def analysis_blog_data(self, reader, exclusion_hosts):
    total_access = 0
    other_user_access = 0
    visitors_count = 0
    posts_count = None

    for row in reader:
      if row is None:
        continue
      if row[3]:
        posts_count = row[3]
      total_access += int(row[1])
      try:
        host_name = socket.gethostbyaddr(row[0])[0]
        if host_name.endswith('.au-net.ne.jp'):
          print(row)
          continue
        elif host_name in exclusion_hosts:
          print(row)
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
