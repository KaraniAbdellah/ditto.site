import os
import io
import json
import time
import tarfile
import threading
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class ModernDittoCloner:
    def __init__(self, root):
        self.root = root
        self.root.title("Ditto Web Cloner")
        self.root.geometry("620x760")
        self.root.configure(bg="#0f172a")  # Deep slate background
        self.root.resizable(False, False)

        # Color Palette (Matching the Tailwind Snippet)
        self.BG_DARK = "#0f172a"
        self.CARD_BG = "#1e293b"
        self.ACCENT_VIOLET = "#7c3aed"
        self.ACCENT_VIOLET_HOVER = "#6d28d9"
        self.TEXT_PRIMARY = "#f8fafc"
        self.TEXT_MUTED = "#94a3b8"
        self.BORDER_COLOR = "#334155"
        self.ROSE_GLOW = "#f43f5e"

        # Apply TTK Theme Styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        # Main Scrollable / Padding Container
        main_container = tk.Frame(self.root, bg=self.BG_DARK, padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- Header Card ---
        header_card = tk.Frame(main_container, bg=self.CARD_BG, highlightbackground=self.BORDER_COLOR, highlightthickness=1, padx=20, pady=16)
        header_card.pack(fill=tk.X, pady=(0, 15))

        title_label = tk.Label(
            header_card, 
            text="Get more updates...", 
            font=("Segoe UI", 16, "bold"), 
            fg=self.ACCENT_VIOLET, 
            bg=self.CARD_BG
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_card, 
            text="Clone landing pages and component structures directly into clean React code.", 
            font=("Segoe UI", 9), 
            fg=self.TEXT_MUTED, 
            bg=self.CARD_BG,
            wraplength=540,
            justify="left"
        )
        subtitle_label.pack(anchor="w", pady=(4, 0))

        # --- Section 1: Authentication ---
        auth_card = tk.LabelFrame(
            main_container, 
            text=" 1. Authentication ", 
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_PRIMARY, 
            bg=self.CARD_BG,
            bd=1,
            relief="solid",
            padx=15, 
            pady=12
        )
        auth_card.pack(fill=tk.X, pady=(0, 15))

        tk.Label(auth_card, text="API Key:", font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=0, column=0, sticky="w", pady=6)
        self.api_key_entry = tk.Entry(auth_card, font=("Segoe UI", 10), bg="#090d16", fg=self.TEXT_PRIMARY, insertbackground="white", bd=1, relief="solid", show="*")
        self.api_key_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=6)

        tk.Label(auth_card, text="Request Key:", font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=1, column=0, sticky="w", pady=6)
        self.email_entry = tk.Entry(auth_card, font=("Segoe UI", 10), bg="#090d16", fg=self.TEXT_PRIMARY, insertbackground="white", bd=1, relief="solid")
        self.email_entry.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=6)

        req_btn = tk.Button(
            auth_card, 
            text="Send Request", 
            font=("Segoe UI", 9, "bold"), 
            bg=self.ACCENT_VIOLET, 
            fg="white", 
            activebackground=self.ACCENT_VIOLET_HOVER, 
            activeforeground="white",
            bd=0, 
            padx=10, 
            pady=3,
            cursor="hand2",
            command=self.request_key
        )
        req_btn.grid(row=1, column=2, sticky="e", pady=6)

        auth_card.columnconfigure(1, weight=1)

        # --- Section 2: Configuration ---
        config_card = tk.LabelFrame(
            main_container, 
            text=" 2. Clone Configuration ", 
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_PRIMARY, 
            bg=self.CARD_BG,
            bd=1,
            relief="solid",
            padx=15, 
            pady=12
        )
        config_card.pack(fill=tk.X, pady=(0, 15))

        tk.Label(config_card, text="Target URL:", font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=0, column=0, sticky="w", pady=6)
        self.url_entry = tk.Entry(config_card, font=("Segoe UI", 10), bg="#090d16", fg=self.TEXT_PRIMARY, insertbackground="white", bd=1, relief="solid")
        self.url_entry.insert(0, "https://saaslandingpage.com/")
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=6)

        tk.Label(config_card, text="Output Folder:", font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=1, column=0, sticky="w", pady=6)
        self.folder_entry = tk.Entry(config_card, font=("Segoe UI", 10), bg="#090d16", fg=self.TEXT_PRIMARY, insertbackground="white", bd=1, relief="solid")
        self.folder_entry.insert(0, "cloned-site")
        self.folder_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=6)

        tk.Label(config_card, text="Mode:", font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=2, column=0, sticky="w", pady=6)
        self.mode_var = tk.StringVar(value="multi-page")
        
        mode_frame = tk.Frame(config_card, bg=self.CARD_BG)
        mode_frame.grid(row=2, column=1, columnspan=2, sticky="w", padx=(10, 0))
        
        tk.Radiobutton(mode_frame, text="Multi-Page", variable=self.mode_var, value="multi-page", bg=self.CARD_BG, fg=self.TEXT_PRIMARY, selectcolor=self.BG_DARK, activebackground=self.CARD_BG, activeforeground=self.TEXT_PRIMARY).pack(side="left", padx=(0, 15))
        tk.Radiobutton(mode_frame, text="Single Page", variable=self.mode_var, value="single", bg=self.CARD_BG, fg=self.TEXT_PRIMARY, selectcolor=self.BG_DARK, activebackground=self.CARD_BG, activeforeground=self.TEXT_PRIMARY).pack(side="left")

        tk.Label(config_card, text="Framework:", font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.CARD_BG).grid(row=3, column=0, sticky="w", pady=6)
        self.fw_var = tk.StringVar(value="next")
        
        fw_frame = tk.Frame(config_card, bg=self.CARD_BG)
        fw_frame.grid(row=3, column=1, columnspan=2, sticky="w", padx=(10, 0))
        
        tk.Radiobutton(fw_frame, text="Next.js", variable=self.fw_var, value="next", bg=self.CARD_BG, fg=self.TEXT_PRIMARY, selectcolor=self.BG_DARK, activebackground=self.CARD_BG, activeforeground=self.TEXT_PRIMARY).pack(side="left", padx=(0, 15))
        tk.Radiobutton(fw_frame, text="Vite", variable=self.fw_var, value="vite", bg=self.CARD_BG, fg=self.TEXT_PRIMARY, selectcolor=self.BG_DARK, activebackground=self.CARD_BG, activeforeground=self.TEXT_PRIMARY).pack(side="left")

        config_card.columnconfigure(1, weight=1)

        # --- Primary Action Button ---
        self.clone_btn = tk.Button(
            main_container, 
            text="Subscribe & Start Clone", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.ACCENT_VIOLET, 
            fg="white", 
            activebackground=self.ACCENT_VIOLET_HOVER, 
            activeforeground="white",
            bd=0, 
            pady=10, 
            cursor="hand2",
            command=self.start_cloning_thread
        )
        self.clone_btn.pack(fill=tk.X, pady=(0, 15))

        # --- Section 3: Terminal Console ---
        log_card = tk.LabelFrame(
            main_container, 
            text=" Process Output ", 
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_PRIMARY, 
            bg=self.CARD_BG,
            bd=1,
            relief="solid",
            padx=10, 
            pady=10
        )
        log_card.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_card, 
            height=8, 
            state="disabled", 
            bg="#020617", 
            fg="#a7f3d0", 
            font=("Consolas", 9),
            bd=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def configure_styles(self):
        self.style.configure(".", background=self.BG_DARK, foreground=self.TEXT_PRIMARY)

    def log(self, message):
        """Safely append logs to the console window"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def request_key(self):
        email = self.email_entry.get().strip()
        if not email:
            messagebox.showerror("Error", "Please enter an email address.")
            return

        def _req():
            self.log(f"📩 Requesting API key for {email}...")
            url = "https://api.ditto.site/v1/signup/request"
            payload = json.dumps({"email": email}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

            try:
                with urllib.request.urlopen(req) as resp:
                    self.log("✅ Key requested successfully! Check your email and paste the key above.")
            except Exception as e:
                self.log(f"❌ Failed to request key: {e}")

        threading.Thread(target=_req, daemon=True).start()

    def start_cloning_thread(self):
        """Execute non-blocking clone pipeline in background thread"""
        api_key = self.api_key_entry.get().strip()
        target_url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip() or "cloned-site"
        mode = self.mode_var.get()
        framework = self.fw_var.get()

        if not api_key:
            messagebox.showerror("Error", "Please enter your Ditto API Key.")
            return

        if not target_url:
            messagebox.showerror("Error", "Please enter a Target Website URL.")
            return

        self.clone_btn.config(state="disabled", bg="#475569")
        threading.Thread(target=self.run_clone_pipeline, args=(api_key, target_url, folder, mode, framework), daemon=True).start()

    def run_clone_pipeline(self, api_key, target_url, folder, mode, framework):
        try:
            self.log("==========================================")
            self.log(f"🚀 Submitting clone request for {target_url}...")
            self.log(f"Mode: {mode} | Framework: {framework}")

            req_url = "https://api.ditto.site/v1/clones"
            payload = json.dumps({
                "url": target_url,
                "options": {
                    "mode": mode,
                    "framework": framework,
                    "styling": "tailwind"
                }
            }).encode("utf-8")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            req = urllib.request.Request(req_url, data=payload, headers=headers, method="POST")

            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            job_id = data.get("jobId") or data.get("id")
            if not job_id:
                self.log(f"❌ Failed to parse Job ID from response: {data}")
                return

            self.log(f"✅ Job Created! ID: {job_id}")
            self.log("⏳ Processing on server...")

            status_url = f"https://api.ditto.site/v1/clones/{job_id}"
            poll_headers = {"Authorization": f"Bearer {api_key}"}

            while True:
                poll_req = urllib.request.Request(status_url, headers=poll_headers)
                with urllib.request.urlopen(poll_req) as resp:
                    status_data = json.loads(resp.read().decode("utf-8"))

                status = status_data.get("status", "running")
                self.log(f"   └─ Status: {status}")

                if status in ["succeeded", "completed"]:
                    self.log("🎉 Clone completed successfully on server!")
                    break
                elif status == "failed":
                    self.log(f"❌ Job failed on server: {status_data}")
                    return

                time.sleep(5)

            bundle_url = f"https://api.ditto.site/v1/clones/{job_id}/bundle?format=tgz"
            self.log(f"📦 Extracting bundle into './{folder}'...")

            dl_req = urllib.request.Request(bundle_url, headers=poll_headers)
            with urllib.request.urlopen(dl_req) as resp:
                tar_bytes = resp.read()

            os.makedirs(folder, exist_ok=True)
            with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as tar:
                tar.extractall(path=folder)

            self.log("==========================================")
            self.log(f"✨ Project saved to './{folder}'.")
            self.log(f"Run: cd {folder} && npm install && npm run dev")

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else ""
            self.log(f"❌ HTTP Error {e.code}: {err_body}")
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
        finally:
            self.clone_btn.config(state="normal", bg=self.ACCENT_VIOLET)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernDittoCloner(root)
    root.mainloop()