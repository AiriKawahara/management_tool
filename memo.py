from flask        import Flask, request, flash
from google.cloud import datastore

class Memo:
  def __init__(self):
    self.client = datastore.Client('management-tool-y')

  # メモ取得
  def get_memo(self):
    query = self.client.query(kind='memo')
    memo  = list(query.fetch())
    memo  = sorted(memo,key=lambda x:x['sort'])

    for m in memo:
      m.content = m['content'].replace('\r\n', '<br>')
      m.content = m['content'].replace('\n', '<br>')

    return memo

  # メモ登録
  def register_memo(self, request):
    sort    = len(self.get_memo()) + 1
    content = request.form['content']

    key = self.client.key('memo')
    memo = datastore.Entity(key)
    memo.update({
      'sort': sort,
      'content': content
    })
    self.client.put(memo)
    flash('メモを登録しました。', 'success')
