from flask import Flask

class Task:
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