"""
🌐 لوحة تحكم ويب لبوت المكتبة
Web Dashboard for Library Bot

المميزات:
- عرض جميع الطلبات
- عرض جميع الطلاب ورصيدهم
- شحن رصيد الطلاب
- عرض الإيصالات المعلقة
- إحصائيات شاملة
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# ملفات البيانات
DATA_FILE = "bot_data.json"
RECEIPTS_FILE = "pending_receipts.json"
FILES_CONFIG = "files_config.json"

# كلمة مرور بسيطة للحماية (غيّرها!)
ADMIN_PASSWORD = "admin123"

def load_data():
    """تحميل بيانات البوت"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "files": {}, "orders": []}

def save_data(data):
    """حفظ بيانات البوت"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_receipts():
    """تحميل الإيصالات المعلقة"""
    if os.path.exists(RECEIPTS_FILE):
        with open(RECEIPTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def load_files_config():
    """تحميل تكوين الملفات"""
    if os.path.exists(FILES_CONFIG):
        with open(FILES_CONFIG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# قالب HTML للوحة التحكم
DASHBOARD_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 لوحة تحكم بوت المكتبة</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            text-align: center;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card .icon {
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        .stat-card .number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        
        .stat-card .label {
            color: #666;
            font-size: 1.1em;
        }
        
        .section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: right;
            font-weight: bold;
        }
        
        td {
            padding: 15px;
            border-bottom: 1px solid #eee;
            text-align: right;
        }
        
        tr:hover {
            background: #f8f9ff;
        }
        
        .btn {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            background: #5568d3;
        }
        
        .btn-success {
            background: #48bb78;
        }
        
        .btn-success:hover {
            background: #38a169;
        }
        
        .btn-danger {
            background: #f56565;
        }
        
        .btn-danger:hover {
            background: #e53e3e;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .badge-success {
            background: #c6f6d5;
            color: #22543d;
        }
        
        .badge-warning {
            background: #feebc8;
            color: #744210;
        }
        
        .badge-info {
            background: #bee3f8;
            color: #2c5282;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.2em;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .tab {
            padding: 12px 25px;
            background: #e2e8f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        
        .tab.active {
            background: #667eea;
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
            
            table {
                font-size: 0.9em;
            }
            
            th, td {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- الهيدر -->
        <div class="header">
            <h1>🤖 لوحة تحكم بوت المكتبة</h1>
            <p style="color: #666; font-size: 1.1em;">إدارة شاملة للطلبات والطلاب</p>
        </div>
        
        <!-- الإحصائيات -->
        <div class="stats">
            <div class="stat-card">
                <div class="icon">👥</div>
                <div class="number">{{ stats.total_users }}</div>
                <div class="label">إجمالي الطلاب</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">📦</div>
                <div class="number">{{ stats.total_orders }}</div>
                <div class="label">إجمالي الطلبات</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">💰</div>
                <div class="number">{{ stats.total_revenue }}</div>
                <div class="label">إجمالي المبيعات (جنيه)</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">📸</div>
                <div class="number">{{ stats.pending_receipts }}</div>
                <div class="label">إيصالات معلقة</div>
            </div>
        </div>
        
        <!-- التابات -->
        <div class="section">
            <div class="tabs">
                <button class="tab active" onclick="showTab('orders')">📦 الطلبات</button>
                <button class="tab" onclick="showTab('users')">👥 الطلاب</button>
                <button class="tab" onclick="showTab('receipts')">📸 الإيصالات</button>
                <button class="tab" onclick="showTab('charge')">💰 شحن رصيد</button>
                <button class="tab" onclick="showTab('files')">📁 الملفات</button>
            </div>
            
            <!-- تاب الطلبات -->
            <div id="orders" class="tab-content active">
                <h2>📦 جميع الطلبات</h2>
                {% if orders %}
                <table>
                    <thead>
                        <tr>
                            <th>رقم الطلب</th>
                            <th>User ID</th>
                            <th>الملف</th>
                            <th>الصفحات</th>
                            <th>السعر</th>
                            <th>التاريخ</th>
                            <th>الحالة</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for order in orders %}
                        <tr>
                            <td><strong>#{{ order.order_number }}</strong></td>
                            <td><code>{{ order.user_id }}</code></td>
                            <td>{{ order.file_name }}</td>
                            <td>{{ order.pages }} ورقة</td>
                            <td><strong>{{ order.price }} جنيه</strong></td>
                            <td>{{ order.date }}</td>
                            <td><span class="badge badge-info">{{ order.status }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">
                    <p>📭 لا توجد طلبات بعد</p>
                </div>
                {% endif %}
            </div>
            
            <!-- تاب الطلاب -->
            <div id="users" class="tab-content">
                <h2>👥 جميع الطلاب</h2>
                {% if users %}
                <table>
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>الرصيد الحالي</th>
                            <th>عدد الطلبات</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user_id, user_info in users.items() %}
                        <tr>
                            <td><code>{{ user_id }}</code></td>
                            <td>
                                <strong style="color: {% if user_info.balance > 0 %}#48bb78{% else %}#f56565{% endif %}">
                                    {{ user_info.balance }} جنيه
                                </strong>
                            </td>
                            <td>{{ user_info.orders|length }} طلب</td>
                            <td>
                                <a href="{{ url_for('charge_user', user_id=user_id) }}" class="btn btn-success">
                                    💰 شحن رصيد
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">
                    <p>👤 لا يوجد طلاب بعد</p>
                </div>
                {% endif %}
            </div>
            
            <!-- تاب الإيصالات -->
            <div id="receipts" class="tab-content">
                <h2>📸 الإيصالات المعلقة</h2>
                {% if receipts %}
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>User ID</th>
                            <th>Username</th>
                            <th>التاريخ</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for receipt in receipts %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td><code>{{ receipt.user_id }}</code></td>
                            <td>{{ receipt.username or 'غير متوفر' }}</td>
                            <td>{{ receipt.date }}</td>
                            <td>
                                <a href="{{ url_for('charge_user', user_id=receipt.user_id) }}" class="btn btn-success">
                                    💰 شحن رصيد
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <p style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px; color: #856404;">
                    💡 <strong>ملاحظة:</strong> راجع الإيصالات على تليجرام ثم اضغط "شحن رصيد" للطالب المطلوب
                </p>
                {% else %}
                <div class="empty-state">
                    <p>✅ لا توجد إيصالات معلقة</p>
                </div>
                {% endif %}
            </div>
            
            <!-- تاب شحن الرصيد -->
            <div id="charge" class="tab-content">
                <h2>💰 شحن رصيد طالب</h2>
                <form method="POST" action="{{ url_for('charge_balance') }}" style="max-width: 500px;">
                    <div class="form-group">
                        <label>User ID الطالب:</label>
                        <input type="text" name="user_id" required placeholder="مثال: 123456789">
                    </div>
                    
                    <div class="form-group">
                        <label>المبلغ المراد شحنه (جنيه):</label>
                        <input type="number" name="amount" step="0.01" min="0.01" required placeholder="مثال: 50">
                    </div>
                    
                    <button type="submit" class="btn btn-success">✅ شحن الرصيد</button>
                </form>
                
                {% if charge_message %}
                <div style="margin-top: 20px; padding: 15px; background: #d4edda; color: #155724; border-radius: 8px;">
                    ✅ {{ charge_message }}
                </div>
                {% endif %}
            </div>
            
            <!-- تاب الملفات -->
            <div id="files" class="tab-content">
                <h2>📁 الملفات المتاحة</h2>
                {% if files %}
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>اسم الملف</th>
                            <th>عدد الصفحات</th>
                            <th>السعر</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for file_id, file_info in files.items() %}
                        <tr>
                            <td><code>{{ file_id }}</code></td>
                            <td>{{ file_info.name }}</td>
                            <td>{{ file_info.pages }} ورقة</td>
                            <td><strong>{{ file_info.price }} جنيه</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <p style="margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px; color: #004085;">
                    💡 <strong>لإضافة ملفات جديدة:</strong> عدّل ملف files_config.json
                </p>
                {% else %}
                <div class="empty-state">
                    <p>📁 لا توجد ملفات متاحة</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            // إخفاء جميع التابات
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // إزالة التنشيط من جميع الأزرار
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // تنشيط التاب المطلوب
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

# صفحة تسجيل الدخول
LOGIN_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - لوحة التحكم</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 100%;
        }
        
        .login-box h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            width: 100%;
            background: #667eea;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: bold;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #5568d3;
        }
        
        .error {
            background: #fee;
            color: #c00;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🔐 تسجيل الدخول</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <div class="form-group">
                <label>كلمة المرور:</label>
                <input type="password" name="password" required autofocus>
            </div>
            <button type="submit" class="btn">دخول</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            return redirect(url_for('dashboard'))
        else:
            error = "كلمة المرور غير صحيحة!"
    
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم الرئيسية"""
    data = load_data()
    receipts = load_receipts()
    files = load_files_config()
    
    # حساب الإحصائيات
    stats = {
        'total_users': len(data.get('users', {})),
        'total_orders': len(data.get('orders', [])),
        'total_revenue': sum(order.get('price', 0) for order in data.get('orders', [])),
        'pending_receipts': len(receipts)
    }
    
    # ترتيب الطلبات من الأحدث للأقدم
    orders = sorted(data.get('orders', []), key=lambda x: x.get('order_number', 0), reverse=True)
    
    return render_template_string(
        DASHBOARD_HTML,
        stats=stats,
        orders=orders,
        users=data.get('users', {}),
        receipts=receipts,
        files=files,
        charge_message=request.args.get('message')
    )

@app.route('/charge/<user_id>')
def charge_user(user_id):
    """إعادة توجيه لصفحة شحن رصيد طالب معين"""
    return redirect(url_for('dashboard') + '#charge')

@app.route('/charge', methods=['POST'])
def charge_balance():
    """شحن رصيد طالب"""
    user_id = request.form.get('user_id')
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        return redirect(url_for('dashboard', message='المبلغ يجب أن يكون أكبر من صفر!'))
    
    data = load_data()
    
    # إنشاء حساب جديد إذا لم يكن موجوداً
    if user_id not in data['users']:
        data['users'][user_id] = {'balance': 0, 'orders': []}
    
    # شحن الرصيد
    data['users'][user_id]['balance'] += amount
    save_data(data)
    
    message = f'تم شحن {amount} جنيه لحساب {user_id}. الرصيد الجديد: {data["users"][user_id]["balance"]} جنيه'
    return redirect(url_for('dashboard', message=message) + '#charge')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("🌐 لوحة التحكم الويب شغالة!")
    print("=" * 50)
    if port == 5000:
        print("📍 افتح المتصفح على: http://localhost:5000")
    else:
        print(f"📍 اللوحة شغالة على البورت: {port}")
    print("🔐 كلمة المرور الافتراضية: admin123")
    print("💡 لتغيير كلمة المرور، عدّل المتغير ADMIN_PASSWORD في الكود")
    print("=" * 50)
    app.run(debug=False, host='0.0.0.0', port=port)
