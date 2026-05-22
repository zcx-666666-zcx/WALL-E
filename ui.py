# ui.py
import time
import tkinter as tk
import config as project_config
from shared import state, ui_queue
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class RobotUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        
        # 颜色主题 (保留你的原版配色)
        self.COLOR_BG_NORMAL = "#FFF8E1" # 暖黄色背景
        self.COLOR_BG_ALERT  = "#FFEBEE"
        self.COLOR_EYES      = "#4E342E"
        self.COLOR_HAPPY     = "#FF8F00"
        self.COLOR_ALERT     = "#D32F2F"
        self.COLOR_TRACK     = "#00838F"
        self.COLOR_CALL_BG   = "#E1F5FE" # 通话时的淡蓝色背景

        self.root.configure(bg=self.COLOR_BG_NORMAL)
        self.root.bind("<Escape>", lambda e: self.close())
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
        # ==================== 1. 顶部健康数据 (始终置顶显示) ====================
        self.data_frame = tk.Frame(self.root, bg=self.COLOR_BG_NORMAL)
        self.data_frame.pack(side="top", fill="x", pady=(20, 10))
        self.data_frame.columnconfigure((0,1,2,3), weight=1)
        label_font = ("Microsoft YaHei", 15, "bold")
        
        self.lbl_temp = tk.Label(self.data_frame, text="🌡️ 温度: -- °C", font=label_font, fg="#5D4037", bg=self.COLOR_BG_NORMAL)
        self.lbl_temp.grid(row=0, column=0)
        self.lbl_hum = tk.Label(self.data_frame, text="💧 湿度: -- %", font=label_font, fg="#5D4037", bg=self.COLOR_BG_NORMAL)
        self.lbl_hum.grid(row=0, column=1)
        self.lbl_hr = tk.Label(self.data_frame, text="❤️ 心率: -- bpm", font=label_font, fg="#D32F2F", bg=self.COLOR_BG_NORMAL)
        self.lbl_hr.grid(row=0, column=2)
        self.lbl_resp = tk.Label(self.data_frame, text="🫁 呼吸: -- 次/分", font=label_font, fg="#0277BD", bg=self.COLOR_BG_NORMAL)
        self.lbl_resp.grid(row=0, column=3)
        
        # ==================== 2. 中央表情画布 (巡逻时显示) ====================
        self.canvas = tk.Canvas(self.root, bg=self.COLOR_BG_NORMAL, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # ==================== 3. 底部状态栏 ====================
        self.status_bar = tk.Label(self.root, text="系统运行中", font=("Microsoft YaHei", 16), fg=self.COLOR_EYES, bg="#FFECB3", pady=10)
        self.status_bar.pack(side="bottom", fill="x")

        # ==================== 4. 温馨版：双向视频分屏容器 ====================
        # 使用清新的淡蓝色作为通话大背景
        self.call_container = tk.Frame(self.root, bg=self.COLOR_CALL_BG)
        
        # --- 左侧：家人画面卡片 ---
        self.remote_frame = tk.Frame(self.call_container, bg="#FFFFFF", bd=0, highlightbackground="#81D4FA", highlightthickness=4)
        self.remote_frame.pack(side="left", fill="both", expand=True, padx=(40, 20), pady=(10, 40))
        
        tk.Label(self.remote_frame, text="💖 亲爱的家人", fg="#0277BD", bg="#FFFFFF", font=("Microsoft YaHei", 18, "bold"), pady=15).pack(side="top")
        
        self.remote_video_label = tk.Label(self.remote_frame, bg="#F5F5F5", text="正在等待家人画面...", fg="#9E9E9E", font=("Microsoft YaHei", 14))
        self.remote_video_label.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- 右侧：本机(老人)画面卡片 ---
        self.local_frame = tk.Frame(self.call_container, bg="#FFFFFF", bd=0, highlightbackground="#FFCC80", highlightthickness=4)
        self.local_frame.pack(side="right", fill="both", expand=True, padx=(20, 40), pady=(10, 40))
        
        tk.Label(self.local_frame, text="🤖 小瓦陪伴视角", fg="#EF6C00", bg="#FFFFFF", font=("Microsoft YaHei", 18, "bold"), pady=15).pack(side="top")
        
        self.local_video_label = tk.Label(self.local_frame, bg="#F5F5F5", text="正在开启摄像头", fg="#9E9E9E", font=("Microsoft YaHei", 14))
        self.local_video_label.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- 初始状态 ---
        self.current_expr = None
        self.is_video_visible = False
        self.current_reminder_text = ""  # 【新增】存储当前提醒内容
        self.last_health_check_at = 0.0
        self.health_refresh_interval = getattr(project_config, "HEALTH_UI_REFRESH_INTERVAL", 1.0)
        self.draw_expression("happy") 
        
        self.root.after(100, self.update_loop)

    def draw_expression(self, expr_type):
        if self.current_expr == expr_type: return
        self.current_expr = expr_type
        self.canvas.delete("all")
        
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        
        bg_color = self.COLOR_BG_NORMAL
        if expr_type == "call": bg_color = self.COLOR_CALL_BG
        elif expr_type == "alert": bg_color = self.COLOR_BG_ALERT
        elif expr_type == "track": bg_color = "#E0F7FA"
        elif expr_type == "reminder": bg_color = "#FFF9C4" # 【新增】提醒时的明亮黄背景
        
        self.root.configure(bg=bg_color)
        self.canvas.configure(bg=bg_color)
        self.data_frame.configure(bg=bg_color)
        self.lbl_temp.configure(bg=bg_color)
        self.lbl_hum.configure(bg=bg_color)
        self.lbl_hr.configure(bg=bg_color)
        self.lbl_resp.configure(bg=bg_color)
        
        if expr_type == "happy" or expr_type == "normal":
            self.status_bar.configure(bg="#FFECB3", fg=self.COLOR_EYES)
            line_w = 20
            self.canvas.create_arc(w*0.25, h*0.35, w*0.40, h*0.55, start=0, extent=180, style="arc", outline=self.COLOR_HAPPY, width=line_w)
            self.canvas.create_arc(w*0.60, h*0.35, w*0.75, h*0.55, start=0, extent=180, style="arc", outline=self.COLOR_HAPPY, width=line_w)
            self.canvas.create_arc(w*0.45, h*0.60, w*0.55, h*0.70, start=180, extent=180, fill=self.COLOR_HAPPY, outline="")
            
        elif expr_type == "track":
            self.status_bar.configure(bg="#B2EBF2", fg=self.COLOR_TRACK)
            self.canvas.create_oval(w*0.25, h*0.35, w*0.40, h*0.60, outline=self.COLOR_TRACK, width=15)
            self.canvas.create_oval(w*0.30, h*0.45, w*0.35, h*0.50, fill=self.COLOR_TRACK, outline="")
            self.canvas.create_oval(w*0.60, h*0.35, w*0.75, h*0.60, outline=self.COLOR_TRACK, width=15)
            self.canvas.create_oval(w*0.65, h*0.45, w*0.70, h*0.50, fill=self.COLOR_TRACK, outline="")
            self.canvas.create_line(w*0.50, h*0.42, w*0.50, h*0.52, fill=self.COLOR_TRACK, width=4)
            self.canvas.create_line(w*0.48, h*0.47, w*0.52, h*0.47, fill=self.COLOR_TRACK, width=4)
            
        elif expr_type == "call":
            self.status_bar.configure(bg="#B3E5FC", fg="#0277BD")
            line_width = 25
            self.canvas.create_line(w*0.25, h*0.55, w*0.35, h*0.45, w*0.45, h*0.55, smooth=True, width=line_width, fill=self.COLOR_HAPPY, capstyle="round")
            self.canvas.create_line(w*0.55, h*0.55, w*0.65, h*0.45, w*0.75, h*0.55, smooth=True, width=line_width, fill=self.COLOR_HAPPY, capstyle="round")
            self.canvas.create_oval(w*0.48, h*0.7, w*0.52, h*0.75, fill=self.COLOR_HAPPY, outline="")
            
        elif expr_type == "alert":
            self.status_bar.configure(bg="#FFCDD2", fg=self.COLOR_ALERT)
            self.canvas.create_oval(w*0.3, h*0.3, w*0.4, h*0.6, fill=self.COLOR_ALERT, outline="")
            self.canvas.create_oval(w*0.3, h*0.65, w*0.4, h*0.75, fill=self.COLOR_ALERT, outline="")
            self.canvas.create_oval(w*0.6, h*0.3, w*0.7, h*0.6, fill=self.COLOR_ALERT, outline="")
            self.canvas.create_oval(w*0.6, h*0.65, w*0.7, h*0.75, fill=self.COLOR_ALERT, outline="")
            
        # ==========================================
        # 【新增】：专门给老人看的全屏温馨提醒界面
        # ==========================================
        elif expr_type == "reminder":
            self.status_bar.configure(bg="#FFECB3", fg="#E65100")
            # 屏幕正中央画一个大闹钟和超大号的提醒文字
            self.canvas.create_text(w/2, h/2 - 80, text="⏰ 温馨提醒", font=("Microsoft YaHei", 50, "bold"), fill="#E65100")
            self.canvas.create_text(w/2, h/2 + 50, text=self.current_reminder_text, font=("Microsoft YaHei", 40), fill="#424242", width=w*0.8, justify="center")

    def _refresh_health_labels_from_state(self):
        now = time.monotonic()
        if now - self.last_health_check_at < self.health_refresh_interval:
            return
        self.last_health_check_at = now

        snapshot = state.health_snapshot()
        nearlink = snapshot.get("nearlink", {})
        temperature = snapshot.get("temperature", 0.0)
        humidity = snapshot.get("humidity", 0.0)
        hr = nearlink.get("hr", 0)
        br = nearlink.get("br", 0)

        self.lbl_temp.config(text=f"🌡️ 温度: {temperature} °C")
        self.lbl_hum.config(text=f"💧 湿度: {humidity} %")
        self.lbl_hr.config(text=f"❤️ 心率: {hr} bpm")
        self.lbl_resp.config(text=f"🫁 呼吸: {br} 次/分")
        print(f"[UI] refresh health Temp:{temperature} Hum:{humidity} HR:{hr} BR:{br}")

    def _update_loop_once(self):
        while not ui_queue.empty():
            msg = ui_queue.get()

            if msg.get('reset_view'):
                if self.is_video_visible:
                    self.call_container.pack_forget()
                    self.canvas.pack(fill="both", expand=True)
                    self.status_bar.pack(side="bottom", fill="x")
                    self.is_video_visible = False
                self.current_reminder_text = ""
                self.remote_video_label.configure(image="", text="姝ｅ湪绛夊緟瀹朵汉鐢婚潰...")
                self.local_video_label.configure(image="", text="姝ｅ湪寮€鍚憚鍍忓ご")
                self.remote_video_label.imgtk = None
                self.local_video_label.imgtk = None
                self.draw_expression("happy")
                self.status_bar.config(text=" 系统运行中 ")
            
            if 'status' in msg: self.status_bar.config(text=f" {msg['status']} ")
            
            # ==========================================
            # 【新增】：接收到提醒文字时，保存并切换表情
            # ==========================================
            if 'reminder_text' in msg:
                self.current_reminder_text = msg['reminder_text']
                self.draw_expression("reminder")
                
            if 'face' in msg: self.draw_expression(msg['face'])
            
            if 'temp' in msg: self.lbl_temp.config(text=f"🌡️ 温度: {msg['temp']} °C")
            if 'hum' in msg: self.lbl_hum.config(text=f"💧 湿度: {msg['hum']} %")
            if 'hr' in msg: self.lbl_hr.config(text=f"❤️ 心率: {msg['hr']} bpm")
            if 'resp' in msg: self.lbl_resp.config(text=f"🫁 呼吸: {msg['resp']} 次/分")
            
            if 'video_frame' in msg or 'local_video_frame' in msg:
                if msg.get('video_frame') is None and msg.get('local_video_frame') is None:
                    if self.is_video_visible:
                        self.call_container.pack_forget()
                        self.canvas.pack(fill="both", expand=True)
                        self.status_bar.pack(side="bottom", fill="x")
                        self.is_video_visible = False
                        self.draw_expression("happy")
                        self.status_bar.config(text=" 系统运行中 ")
                else:
                    if not self.is_video_visible:
                        self.canvas.pack_forget() 
                        self.status_bar.pack_forget() 
                        self.call_container.pack(fill="both", expand=True) 
                        self.is_video_visible = True
                    
                    if msg.get('video_frame') is not None and HAS_PIL:
                        self._render_image(msg['video_frame'], self.remote_video_label)
                    
                    if msg.get('local_video_frame') is not None and HAS_PIL:
                        self._render_image(msg['local_video_frame'], self.local_video_label)

        self._refresh_health_labels_from_state()
        pass

    def update_loop(self):
        try:
            self._update_loop_once()
        except Exception as e:
            print(f"[UI] update loop error: {e}")
        finally:
            self.root.after(50, self.update_loop)

    def _render_image(self, cv_img, label_widget):
        import cv2
        try:
            cv_img = cv2.resize(cv_img, (480, 360))
            cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv_img_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            label_widget.imgtk = imgtk 
            label_widget.configure(image=imgtk, text="")
        except Exception:
            pass

    def run(self):
        self.root.mainloop()

    def close(self):
        try:
            self.root.quit()
            self.root.destroy()
        except tk.TclError:
            pass

# --- 全局工具函数 ---
# 【修改】: 增加了 reminder_text 参数
def update_ui(face=None, status=None, temp=None, hum=None, hr=None, resp=None, reminder_text=None, reset_view=False):
    data = {}
    if reset_view: data['reset_view'] = True
    if face: data['face'] = face
    if status: data['status'] = status
    if temp is not None: data['temp'] = temp
    if hum is not None: data['hum'] = hum
    if hr is not None: data['hr'] = hr
    if resp is not None: data['resp'] = resp
    
    # 【新增】: 处理提醒文字
    if reminder_text is not None: data['reminder_text'] = reminder_text
    
    if data: ui_queue.put(data)

def update_video_ui(frame):
    ui_queue.put({'video_frame': frame})

def update_local_video_ui(frame):
    ui_queue.put({'local_video_frame': frame})
