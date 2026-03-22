import json
import os
from database import db
from datetime import datetime

def migrate_users_from_json():
    post_map_file = 'post_user_map.json'
    delete_map_file = 'delete_user_map.json'
    
    users_data = {}
    
    if os.path.exists(post_map_file):
        with open(post_map_file, 'r') as f:
            post_map = json.load(f)
        for user_id in post_map.values():
            user_id_int = int(user_id)
            if user_id_int not in users_data:
                users_data[user_id_int] = {'posts': 0, 'deletes': 0}
            users_data[user_id_int]['posts'] += 1
    
    if os.path.exists(delete_map_file):
        with open(delete_map_file, 'r') as f:
            delete_map = json.load(f)
        for user_id in delete_map.values():
            user_id_int = int(user_id)
            if user_id_int not in users_data:
                users_data[user_id_int] = {'posts': 0, 'deletes': 0}
            users_data[user_id_int]['deletes'] += 1
    
    for user_id, data in users_data.items():
        try:
            db.conn.execute('''
                INSERT OR REPLACE INTO users (id, username, full_name, first_used, last_used, posts_count, delete_requests_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, None, f'user_{user_id}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data['posts'], data['deletes']))
        except Exception as e:
            print(f"Ошибка при добавлении {user_id}: {e}")
    
    db.conn.commit()
    print(f"✅ Добавлено {len(users_data)} пользователей из JSON")
    for user_id, data in users_data.items():
        print(f"   ID: {user_id}, постов: {data['posts']}, удалений: {data['deletes']}")

if __name__ == '__main__':
    migrate_users_from_json()
    db.close()
