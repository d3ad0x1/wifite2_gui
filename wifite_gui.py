import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import re

class WifiteApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wifite2 GUI - Networks by signal strength")
        self.root.geometry("850x600")

        # --- Notebook ---
        self.tab_control = ttk.Notebook(self.root)
        self.tab_scan = ttk.Frame(self.tab_control)
        self.tab_attack = ttk.Frame(self.tab_control)
        self.tab_logs = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_scan, text='Scanning')
        self.tab_control.add(self.tab_attack, text='Attack')
        self.tab_control.add(self.tab_logs, text='Logs')
        self.tab_control.pack(expand=1, fill="both")

        # --- Scanning ---
        tk.Label(self.tab_scan, text="Select interface:").pack(pady=5)
        self.interface_var = tk.StringVar()
        self.interface_combo = ttk.Combobox(self.tab_scan, textvariable=self.interface_var)
        self.interface_combo['values'] = self.get_interfaces()
        self.interface_combo.pack(pady=5)

        self.btn_scan = tk.Button(self.tab_scan, text="Scan networks", command=self.scan_networks)
        self.btn_scan.pack(pady=5)

        self.list_networks = tk.Listbox(self.tab_scan)
        self.list_networks.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.progress_scan = ttk.Progressbar(self.tab_scan, mode='indeterminate')
        self.progress_scan.pack(fill=tk.X, padx=10, pady=5)

        # --- Attack ---
        tk.Label(self.tab_attack, text="Select network to attack:").pack(pady=5)
        self.attack_network_var = tk.StringVar()
        self.combo_attack_network = ttk.Combobox(self.tab_attack, textvariable=self.attack_network_var)
        self.combo_attack_network.pack(pady=5)

        self.btn_attack = tk.Button(self.tab_attack, text="Start attack", command=self.start_attack)
        self.btn_attack.pack(pady=5)

        # --- Logs ---
        self.txt_logs = tk.Text(self.tab_logs, bg="#1e1e1e", fg="white")
        self.txt_logs.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.scroll_logs = tk.Scrollbar(self.tab_logs, command=self.txt_logs.yview)
        self.scroll_logs.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_logs.config(yscrollcommand=self.scroll_logs.set)

        # --- Auto-update ---
        self.auto_update_interval = 5000  # 5 seconds
        self.auto_update_running = False
        self.known_networks = {}  # {BSSID: signal_strength}

    def get_interfaces(self):
        try:
            result = subprocess.run(["ip", "-o", "link", "show"], capture_output=True, text=True)
            interfaces = [line.split(":")[1].strip() for line in result.stdout.splitlines()]
            return interfaces
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get interfaces: {e}")
            return []

    def scan_networks(self):
        iface = self.interface_var.get()
        if not iface:
            messagebox.showwarning("Select Interface", "Please select an interface for scanning!")
            return
        self.list_networks.delete(0, tk.END)
        self.log(f"Starting scan on interface {iface}...\n")
        self.progress_scan.start()
        threading.Thread(target=self.run_wifite_scan, args=(iface,), daemon=True).start()
        if not self.auto_update_running:
            self.auto_update_running = True
            self.root.after(self.auto_update_interval, self.auto_update_networks)

    def run_wifite_scan(self, iface):
        try:
            process = subprocess.Popen(["sudo", "wifite", "-i", iface, "--show"], 
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self.log(line)
                # Searching for BSSID and signal
                if "BSSID:" in line and "Power:" in line:
                    match_bssid = re.search(r'BSSID:\s*([0-9A-F:]{17})', line)
                    match_power = re.search(r'Power:\s*([-\d]+) dBm', line)
                    if match_bssid and match_power:
                        bssid = match_bssid.group(1)
                        power = int(match_power.group(1))
                        self.known_networks[bssid] = power
                        display_text = f"{bssid} | Power: {power} dBm"
                        idx = self.list_networks.size()
                        self.list_networks.insert(tk.END, display_text)
                        self.combo_attack_network['values'] = list(self.known_networks.keys())
                        # Color based on signal strength
                        if power >= -50:
                            color = '#00ff00'  # Strong signal — green
                        elif power >= -70:
                            color = '#ffff00'  # Medium — yellow
                        else:
                            color = '#ff4d4d'  # Weak — red
                        self.list_networks.itemconfig(idx, {'bg': color})
            self.progress_scan.stop()
            self.log("Scanning completed.\n")
        except Exception as e:
            self.progress_scan.stop()
            messagebox.showerror("Error", f"Error during scanning: {e}")

    def auto_update_networks(self):
        iface = self.interface_var.get()
        if iface:
            self.log("Auto-updating network list...\n")
            threading.Thread(target=self.run_wifite_scan, args=(iface,), daemon=True).start()
        self.root.after(self.auto_update_interval, self.auto_update_networks)

    def start_attack(self):
        bssid = self.attack_network_var.get()
        iface = self.interface_var.get()
        if not bssid:
            messagebox.showwarning("Select Network", "Please select a network to attack!")
            return
        self.log(f"Starting attack on {bssid}...\n")
        threading.Thread(target=self.run_wifite_attack, args=(iface, bssid), daemon=True).start()

    def run_wifite_attack(self, iface, bssid):
        try:
            process = subprocess.Popen(["sudo", "wifite", "-i", iface, "-b", bssid], 
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self.log(line)
            self.log(f"Attack on {bssid} completed.\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error during attack: {e}")

    def log(self, text):
        if "ERROR" in text or "error" in text.lower():
            self.txt_logs.insert(tk.END, text, 'error')
            self.txt_logs.tag_config('error', foreground='red')
        else:
            self.txt_logs.insert(tk.END, text)
        self.txt_logs.see(tk.END)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WifiteApp()
    app.run()
