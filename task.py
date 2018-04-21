from flask import Flask, request, flash
from google.cloud import datastore

class Task:
  def __init__(self):
    self.client = datastore.Client('management-tool-y')

  # タスク登録
  def register_task(self, request):
    task_name = request.form['task_name_input']
    deadline = request.form['deadline_input']

    # すでに同じタスクが登録されている場合は登録しない
    query = self.client.query(kind='task')
    query.add_filter('task_name', '=', task_name)
    query.add_filter('deadline', '=', deadline)
    tasks = list(query.fetch())
    if len(tasks) > 0:
      flash('すでに同じタスクが登録されています。', 'danger')
      return

    key = self.client.key('task')
    task = datastore.Entity(key)
    task.update({
      'task_name': task_name,
      'deadline': deadline
    })
    self.client.put(task)
    flash('タスクを登録しました。', 'success')

  # タスク完了
  def complete_task(self, request):
    task_name = request.form['task_name']
    deadline = request.form['deadline']
    complete_date = request.form['complete_date']

    # 実績登録
    key = self.client.key('treated')
    task = datastore.Entity(key)
    task.update({
      'task_name': task_name,
      'treated_date': complete_date,
      'deadline': deadline
    })
    self.client.put(task)

    # タスク削除
    query = self.client.query(kind='task')
    query.add_filter('task_name', '=', task_name)
    query.add_filter('deadline', '=', deadline)
    target = list(query.fetch())
    if len(target) > 0:
      key = target[0].__dict__['key']
      self.client.delete(key)
    flash('タスクを完了しました。', 'success')

  # タスク編集
  def edit_task(self, request):
    old_task_name = request.form['old_task_name']
    new_task_name = request.form['new_task_name']
    old_deadline = request.form['old_deadline']
    new_deadline = request.form['new_deadline']

    query = self.client.query(kind='task')
    query.add_filter('task_name', '=', old_task_name)
    query.add_filter('deadline', '=', old_deadline)
    target = list(query.fetch())

    if len(target) == 0:
      flash('タスクの更新に失敗しました。', 'danger')
      return

    key = target[0].__dict__['key']
    task = datastore.Entity(key)
    task.update({
      'task_name': new_task_name,
      'deadline': new_deadline
    })
    self.client.put(task)
    flash('タスクを更新しました。', 'success')

  # タスク削除
  def delete_task(self, request):
    task_name = request.form['task_name']
    deadline = request.form['deadline']

    query = self.client.query(kind='task')
    query.add_filter('task_name', '=', task_name)
    query.add_filter('deadline', '=', deadline)
    target = list(query.fetch())

    if len(target) == 0:
      flash('タスクの削除に失敗しました。', 'danger')
      return

    key = target[0].__dict__['key']
    self.client.delete(key)
    flash('タスクを削除しました。', 'success')

  # 毎日のタスクを取得
  def get_everyday_tasks(self, all_tasks):
    const_day = '2099-12-31'
    results = []
    for task in all_tasks:
      if task['deadline'] == const_day:
        results.append(task)
    return results

  # 期限切れのタスクを取得
  def get_expired_tasks(self, all_tasks, today):
    results = []
    for task in all_tasks:
      if task['deadline'] < today:
        results.append(task)
    return sorted(results,key=lambda x:x["deadline"])

  # 今日までのタスクを取得
  def get_danger_tasks(self, all_tasks, today):
    results = []
    for task in all_tasks:
      if task['deadline'] == today:
        results.append(task)
    return results

  # 期日が今日以降のタスクを取得
  def get_other_tasks(self, all_tasks, today):
    const_day = '2099-12-31'
    results = []
    for task in all_tasks:
      if task['deadline'] > today and task['deadline'] != const_day:
        results.append(task)
    return sorted(results,key=lambda x:x["deadline"])

  # 検索範囲内のタスクを取得
  def get_search_tasks(self, all_tasks, start_date, end_date):
    results = []
    for task in all_tasks:
      if task['deadline'] >= start_date and task['deadline'] <= end_date:
        results.append(task)
    return sorted(results,key=lambda x:x["deadline"])