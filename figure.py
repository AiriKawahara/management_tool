from flask import Flask, request, flash, jsonify
from google.cloud import datastore

class Figure:
  def __init__(self):
    self.client = datastore.Client('management-tool-y')

  def register_figure(self, request):
    thickness_r = float(request.form['thickness_r']) if request.form['thickness_r'] else None
    thickness_l = float(request.form['thickness_l']) if request.form['thickness_l'] else None
    figure_date = request.form['figure_date']        if request.form['figure_date'] else None

    query = self.client.query(kind='figure')
    query.add_filter('figure_date', '=', figure_date)
    results = list(query.fetch())

    if len(results) > 0:
      key = results[0].__dict__['key']
      # 入力値が空の場合はDBの値を保持する
      thickness_r = thickness_r if thickness_r else results[0]['right_thickness']
      thickness_l = thickness_l if thickness_l else results[0]['left_thickness']
    else:
      key = self.client.key('figure')

    task = datastore.Entity(key)
    task.update({
      'right_thickness': thickness_r,
      'left_thickness': thickness_l,
      'figure_date': figure_date
    })
    self.client.put(task)
    flash('体型情報を登録しました。', 'success')

  def get_figure(self, request):
    figure_start_date = request.args['figure_start_date']
    figure_end_date   = request.args['figure_end_date']

    query = self.client.query(kind='figure')
    query.add_filter('figure_date', '>=', figure_start_date)
    query.add_filter('figure_date', '<=', figure_end_date)
    results = list(query.fetch())

    if len(results) == 0:
      flash('検索条件に一致するデータが存在しません。', 'warning')

    return jsonify(results)
