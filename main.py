"""
🚀 مشغّل موحد للبوت ولوحة التحكم
Unified Bot + Dashboard Launcher

يشغل البوت ولوحة التحكم في نفس البرنامج
عشان يقروا من نفس الملفات ويتزامنوا
"""

import threading
import logging
import os
import sys

# تعطيل رسائل Flask الكتيرة
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def run_bot():
    """تشغيل البوت في Thread منفصل"""
    try:
        print("🤖 بدء تشغيل البوت...")
        # استيراد وتشغيل البوت
        import printing_bot
        printing_bot.main()
    except Exception as e:
        print(f"❌ خطأ في البوت: {e}")

def run_dashboard():
    """تشغيل لوحة التحكم في Thread منفصل"""
    try:
        print("🌐 بدء تشغيل لوحة التحكم...")
        # استيراد وتشغيل اللوحة
        import web_dashboard
        port = int(os.environ.get('PORT', 5000))
        web_dashboard.app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
    except Exception as e:
        print(f"❌ خطأ في اللوحة: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 تشغيل البوت ولوحة التحكم معاً")
    print("=" * 60)
    print("✅ البوت ولوحة التحكم سيعملان من نفس البيانات")
    print("=" * 60)
    
    # تشغيل البوت في Thread منفصل
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # تشغيل لوحة التحكم في Thread الرئيسي
    # (لازم تكون في الـ main thread عشان Flask)
    run_dashboard()
