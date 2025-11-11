def block_user(user_id):
    db_path = '/tmp/bot_database.db'
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_blocked = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def unblock_user(user_id):
    db_path = '/tmp/bot_database.db'
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_blocked = 0, warning_count = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def is_user_blocked(user_id):
    db_path = '/tmp/bot_database.db'
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT is_blocked FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_user_info(user_id):
    db_path = '/tmp/bot_database.db'
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT username, first_name, warning_count FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None, 0)

def get_user_survey_stats(user_id):
    db_path = '/tmp/bot_database.db'
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_surveys,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_surveys,
            SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as incorrect_surveys,
            SUM(ton_earned) as total_ton_earned
        FROM user_surveys 
        WHERE user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return {
        'total_surveys': result[0] if result else 0,
        'correct_surveys': result[1] if result else 0,
        'incorrect_surveys': result[2] if result else 0,
        'total_ton_earned': result[3] if result else 0
    }

def add_user_survey(user_id, survey_type, is_correct, ton_earned=0):
    db_path = '/tmp/bot_database.db'
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    survey_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO user_surveys 
        (user_id, survey_type, is_correct, survey_date, ton_earned)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, survey_type, is_correct, survey_date, ton_earned))
    
    conn.commit()
    conn.close()

def get_user_purchases(user_id):
    db_path = '/tmp/bot_database.db'
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT file_name, file_category, ton_cost, purchase_date, download_count
        FROM user_purchases 
        WHERE user_id = ?
        ORDER BY purchase_date DESC
    ''', (user_id,))
    
    purchases = cursor.fetchall()
    conn.close()
    
    return purchases

def add_user_purchase(user_id, file_name, file_category, ton_cost):
    db_path = '/tmp/bot_database.db'
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    purchase_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO user_purchases 
        (user_id, file_name, file_category, ton_cost, purchase_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, file_name, file_category, ton_cost, purchase_date))
    
    conn.commit()
    conn.close()
