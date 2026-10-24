import os
import random
import string
from datetime import datetime

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import routeros_api

# خلفية داكنة عصرية مريحة للعين
Window.clearcolor = (0.08, 0.10, 0.15, 1)

# --- إعدادات المايكروتيك ---
ROUTER_IP = "10.10.10.1"
ROUTER_USER = "admin"
ROUTER_PASS = "asdf4411"

# تم تعديل التصميم هنا بحيث يملى مساحة الشاشة بالكامل ويوزع الأزرار بمرونة
KV_LAYOUT = """
<FazlakaUI>:
    orientation: 'vertical'
    padding: [15, 20, 15, 20]
    spacing: 8
    size_hint: (1, 1)
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}

    # 1. عنوان الشبكة العلوي
    Label:
        text: "FAZLAKA NET MANAGER"
        font_size: '22sp'
        bold: True
        color: 0.2, 0.7, 1, 1
        size_hint_y: 0.08

    # حالة الطابعة
    Label:
        id: printer_status
        text: "Printer: Disconnected"
        font_size: '13sp'
        color: 0.9, 0.3, 0.3, 1
        size_hint_y: 0.05

    # 2. زر ربط طابعة البلوتوث (بنفسجي)
    Button:
        text: "Connect Bluetooth Printer"
        background_normal: ''
        background_color: 0.45, 0.25, 0.85, 1
        color: 1, 1, 1, 1
        font_size: '15sp'
        bold: True
        size_hint_y: 0.09

    # 3. الأزرار المزدوجة (User Manager والنشطين)
    BoxLayout:
        orientation: 'horizontal'
        spacing: 8
        size_hint_y: 0.09

        Button:
            text: "User Manager"
            background_normal: ''
            background_color: 0.12, 0.65, 0.45, 1
            color: 1, 1, 1, 1
            font_size: '14sp'
            bold: True

        Button:
            text: "Active Users"
            background_normal: ''
            background_color: 0.15, 0.55, 0.75, 1
            color: 1, 1, 1, 1
            font_size: '14sp'
            bold: True

    # 4. زر دفتر الأجل والديون (برتقالي)
    Button:
        text: "Debts & Ledger"
        background_normal: ''
        background_color: 0.85, 0.45, 0.12, 1
        color: 1, 1, 1, 1
        font_size: '14sp'
        bold: True
        size_hint_y: 0.08

    # 5. زر مصروفات الشبكة (فوشيا)
    Button:
        text: "Network Expenses"
        background_normal: ''
        background_color: 0.75, 0.15, 0.45, 1
        color: 1, 1, 1, 1
        font_size: '14sp'
        bold: True
        size_hint_y: 0.08

    # 6. زر تقرير الخزنة والأرباح (أخضر غامق)
    Button:
        text: "Treasury & Profits Report"
        background_normal: ''
        background_color: 0.10, 0.50, 0.35, 1
        color: 1, 1, 1, 1
        font_size: '14sp'
        bold: True
        size_hint_y: 0.08

    # 7. اختيار فئة الكارت
    Label:
        text: "Select Voucher Category:"
        font_size: '13sp'
        color: 0.7, 0.75, 0.8, 1
        size_hint_y: 0.05
        halign: 'left'

    Spinner:
        id: profile_spinner
        text: '20 EGP Profile (2 GB)'
        values: ('20 EGP Profile (2 GB)', '50 EGP Profile (8 GB)', '100 EGP Profile (20 GB)', '200 EGP Profile (45 GB)')
        size_hint_y: 0.09
        font_size: '15sp'

    # 8. الإجمالي
    Label:
        id: sales_label
        text: "Today's Total: 0.00 EGP"
        font_size: '15sp'
        bold: True
        color: 0.2, 0.9, 1, 1
        size_hint_y: 0.06

    # زر التوليد الرئيسي (برتقالي بارز)
    Button:
        text: "Generate & Print Voucher"
        background_normal: ''
        background_color: 0.9, 0.5, 0.1, 1
        color: 1, 1, 1, 1
        font_size: '16sp'
        bold: True
        size_hint_y: 0.1
        on_press: root.process_voucher()

    # زر حفظ نسخة احتياطية
    Button:
        text: "Backup Data"
        background_normal: ''
        background_color: 0.25, 0.3, 0.4, 1
        color: 1, 1, 1, 1
        font_size: '13sp'
        size_hint_y: 0.07
"""

Builder.load_string(KV_LAYOUT)

class FazlakaUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_sales = 0.0

    def generate_code(self):
        return ''.join(random.choices(string.digits, k=7))

    def process_voucher(self):
        username = self.generate_code()
        password = ""  
        
        selected = self.ids.profile_spinner.text
        
        if '20 EGP' in selected:
            price = 20.0
            profile_name = "profile_20_2GB"
            ar_profile = "كارت 20 ج.م (2 جيجا)"
        elif '50 EGP' in selected:
            price = 50.0
            profile_name = "profile_50_8GB"
            ar_profile = "كارت 50 ج.م (8 جيجا)"
        elif '100 EGP' in selected:
            price = 100.0
            profile_name = "profile_100_20GB"
            ar_profile = "كارت 100 ج.م (20 جيجا)"
        else:
            price = 200.0
            profile_name = "profile_200_45GB"
            ar_profile = "كارت 200 ج.م (45 جيجا)"

        try:
            connection = routeros_api.RouterOsApiPool(
                ROUTER_IP, 
                username=ROUTER_USER, 
                password=ROUTER_PASS, 
                plaintext_login=True
            )
            api = connection.get_api()
            hotspot_user = api.get_resource('/ip/hotspot/user')
            
            hotspot_user.add(
                name=username,
                password=password,
                profile=profile_name,
                comment=f"Fazlaka - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            connection.disconnect()
            router_success = True
        except Exception as e:
            router_success = False

        if router_success:
            self.total_sales += price
            self.ids.sales_label.text = f"Today's Total: {self.total_sales:.2f} EGP"
            self.print_to_bluetooth(username, ar_profile, price)
            self.ids.printer_status.text = f"Success! Code: {username}"
            self.ids.printer_status.color = (0.2, 1, 0.4, 1)
        else:
            self.ids.printer_status.text = "Error: Router Connection Failed!"
            self.ids.printer_status.color = (1, 0.3, 0.3, 1)

    def print_to_bluetooth(self, code, profile_text, price):
        receipt_text = f"""
==============================
         شبكة فذلكا          
==============================
الباقة    : {profile_text}
كود الكارت: {code}
كلمة السر : (بدون كلمة سر)
السعر     : {price} ج.م
التاريخ   : {datetime.now().strftime('%Y-%m-%d %H:%M')}
==============================
    نتمنى لكم إقامة سعيدة    
==============================
\n\n\n
"""
        try:
            os.system(f'echo "{receipt_text}" > /dev/rfcomm0')
        except:
            pass

class MainApp(App):
    def build(self):
        return FazlakaUI()

if __name__ == '__main__':
    MainApp().run()
  
