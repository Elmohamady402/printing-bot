#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت لشحن رصيد الطلاب بسهولة
Admin Script for Charging Student Balance
"""

import json
import os

DATA_FILE = "bot_data.json"

def load_data():
    """تحميل البيانات"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    print("❌ ملف البيانات غير موجود! شغّل البوت الأول مرة.")
    return None

def save_data(data):
    """حفظ البيانات"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def show_all_users(data):
    """عرض كل المستخدمين"""
    if not data["users"]:
        print("\n❌ لا يوجد مستخدمين بعد!")
        return
    
    print("\n" + "="*50)
    print("📋 قائمة المستخدمين:")
    print("="*50)
    
    for user_id, user_info in data["users"].items():
        print(f"\n👤 User ID: {user_id}")
        print(f"   💰 الرصيد: {user_info['balance']:.2f} جنيه")
        print(f"   📦 عدد الطلبات: {len(user_info['orders'])}")
    
    print("="*50)

def charge_balance(data):
    """شحن رصيد طالب"""
    print("\n" + "="*50)
    print("💰 شحن رصيد طالب")
    print("="*50)
    
    user_id = input("\n📝 أدخل User ID الطالب: ").strip()
    
    if user_id not in data["users"]:
        create_new = input(f"\n⚠️ المستخدم {user_id} غير موجود. هل تريد إنشاء حساب جديد؟ (y/n): ")
        if create_new.lower() == 'y':
            data["users"][user_id] = {"balance": 0, "orders": []}
        else:
            print("❌ تم الإلغاء")
            return data
    
    current_balance = data["users"][user_id]["balance"]
    print(f"\n💳 الرصيد الحالي: {current_balance:.2f} جنيه")
    
    try:
        amount = float(input("\n💵 أدخل المبلغ المراد شحنه: "))
        
        if amount <= 0:
            print("❌ المبلغ يجب أن يكون أكبر من صفر!")
            return data
        
        data["users"][user_id]["balance"] += amount
        new_balance = data["users"][user_id]["balance"]
        
        print("\n✅ تم الشحن بنجاح!")
        print(f"💰 الرصيد الجديد: {new_balance:.2f} جنيه")
        
        save_data(data)
        print("✅ تم حفظ البيانات")
        
    except ValueError:
        print("❌ خطأ! أدخل رقماً صحيحاً")
    
    return data

def view_pending_receipts():
    """عرض الإيصالات المعلقة"""
    if not os.path.exists("pending_receipts.json"):
        print("\n❌ لا توجد إيصالات معلقة")
        return
    
    with open("pending_receipts.json", 'r', encoding='utf-8') as f:
        receipts = json.load(f)
    
    if not receipts:
        print("\n✅ لا توجد إيصالات معلقة")
        return
    
    print("\n" + "="*50)
    print("📸 الإيصالات المعلقة:")
    print("="*50)
    
    for i, receipt in enumerate(receipts, 1):
        print(f"\n{i}. User ID: {receipt['user_id']}")
        print(f"   Username: {receipt.get('username', 'غير متوفر')}")
        print(f"   التاريخ: {receipt['date']}")
        print(f"   Photo ID: {receipt['photo_id'][:30]}...")
    
    print("="*50)
    print("\n💡 نصيحة: راجع الإيصالات على تليجرام ثم استخدم خيار 'شحن رصيد'")

def view_orders(data):
    """عرض كل الطلبات"""
    if not data["orders"]:
        print("\n❌ لا توجد طلبات بعد!")
        return
    
    print("\n" + "="*50)
    print("📦 جميع الطلبات:")
    print("="*50)
    
    for order in data["orders"]:
        print(f"\n🔢 رقم الطلب: {order['order_number']}")
        print(f"   👤 User ID: {order['user_id']}")
        print(f"   📄 الملف: {order['file_name']}")
        print(f"   📃 الصفحات: {order['pages']}")
        print(f"   💵 السعر: {order['price']:.2f} جنيه")
        print(f"   📅 التاريخ: {order['date']}")
        print(f"   ✅ الحالة: {order['status']}")
    
    print("="*50)

def main():
    """البرنامج الرئيسي"""
    print("\n" + "🎯"*25)
    print("🤖 لوحة تحكم بوت المكتبة")
    print("🎯"*25)
    
    data = load_data()
    if not data:
        return
    
    while True:
        print("\n" + "="*50)
        print("📋 القائمة الرئيسية:")
        print("="*50)
        print("1. 👥 عرض جميع المستخدمين")
        print("2. 💰 شحن رصيد طالب")
        print("3. 📸 عرض الإيصالات المعلقة")
        print("4. 📦 عرض جميع الطلبات")
        print("5. 🚪 خروج")
        print("="*50)
        
        choice = input("\n👉 اختر رقم (1-5): ").strip()
        
        if choice == "1":
            show_all_users(data)
        elif choice == "2":
            data = charge_balance(data)
        elif choice == "3":
            view_pending_receipts()
        elif choice == "4":
            view_orders(data)
        elif choice == "5":
            print("\n👋 مع السلامة!")
            break
        else:
            print("\n❌ اختيار غير صحيح!")
    
if __name__ == "__main__":
    main()
