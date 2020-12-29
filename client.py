import os
import socket as sc
import sys
import tkinter as tk
from threading import Thread
from decouple import config


class Client:
    def __init__(self):
        self.IP = config("IP")
        self.PORT = int(config("PORT"))
        self.address = (self.IP, self.PORT)
        self.socket = sc.socket(family=sc.AF_INET, type=sc.SOCK_DGRAM)
        self.name = None
        self.messages = None

    def start(self):
        self.name = input('Your name is:')
        print()
        stop = Thread(target=self.stop)
        stop.start()

    def send_text(self, txt):
        message = f"{self.name}: {txt.get()}".encode()
        self.messages.insert(tk.END, message)
        txt.delete(0, tk.END)
        self.socket.sendto(message, self.address)
        data, server = self.socket.recvfrom(4096)
        if data:
            print(data.decode())
            self.messages.insert(tk.END, data.decode())
        else:
            self.socket.close()
            os._exit(0)

    def stop(self):
        while True:
            key = input('')
            if key == 'q':
                self.socket.close()
                os._exit(0)


class GUI:
    def __init__(self):
        self.cl = Client()
        self.cl.start()

    def main(self):
        window = tk.Tk()
        window.title(f'Client | {self.cl.name}')
        frm_messages = tk.Frame(master=window)
        scrollbar = tk.Scrollbar(master=frm_messages)
        messages = tk.Listbox(
            master=frm_messages,
            yscrollcommand=scrollbar.set
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cl.messages = messages
        frm_messages.grid(row=0, column=0, columnspan=3, sticky="nsew")

        frm_entry = tk.Frame(master=window)
        text_input = tk.Entry(master=frm_entry)
        text_input.pack(fill=tk.BOTH, expand=True)
        text_input.bind("<Return>", lambda x: self.cl.send_text(text_input))
        text_input.insert(0, "Your message here.")

        btn_send = tk.Button(
            master=window,
            text='Send',
            command=lambda: self.cl.send_text(text_input)
        )

        frm_entry.grid(row=1, column=0, padx=10, sticky="ew")
        btn_send.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        window.rowconfigure(0, minsize=400, weight=1)
        window.rowconfigure(1, minsize=50, weight=0)
        window.columnconfigure(0, minsize=200, weight=1)
        window.columnconfigure(1, minsize=50, weight=0)

        window.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()
