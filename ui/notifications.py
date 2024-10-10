import tkinter as tk
from tkinter import ttk
import time

class NotificationManager:
    def __init__(self, master):
        self.master = master
        self.notifications = []
        self.notification_frame = tk.Frame(master, bg='#1E1E1E')
        self.notification_frame.pack(side=tk.TOP, fill=tk.X)
        self.notification_frame.pack_forget()  # Hide initially

    def show_notification(self, message, type='info', duration=3000):
        colors = {
            'info': ('#2196F3', '#FFFFFF'),
            'success': ('#4CAF50', '#FFFFFF'),
            'warning': ('#FFC107', '#000000'),
            'error': ('#F44336', '#FFFFFF')
        }
        bg_color, fg_color = colors.get(type, colors['info'])

        notification = tk.Frame(self.notification_frame, bg=bg_color, padx=10, pady=5)
        notification.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(notification, text=message, bg=bg_color, fg=fg_color, font=('Arial', 12)).pack(side=tk.LEFT)
        
        close_button = tk.Button(notification, text='×', bg=bg_color, fg=fg_color, bd=0, font=('Arial', 12, 'bold'),
                                 command=lambda: self.close_notification(notification))
        close_button.pack(side=tk.RIGHT)

        self.notifications.append(notification)
        self.notification_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.master.after(duration, lambda: self.close_notification(notification))

    def close_notification(self, notification):
        notification.destroy()
        self.notifications.remove(notification)
        if not self.notifications:
            self.notification_frame.pack_forget()
