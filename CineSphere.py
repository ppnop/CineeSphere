import customtkinter as ctk
from PIL import Image
import urllib.request, io, os, requests, urllib3, webbrowser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

###############  APP       ###################
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CinéSphere")
        self.geometry("1000x740")
        self.resizable(False, False)
        self.iconbitmap(os.path.join(os.path.dirname(__file__), "logo.ico"))
        ctk.set_appearance_mode("dark")
        ctk.set_widget_scaling(1.0)

        # conteneur  pages
        conteneur = ctk.CTkFrame(self)
        conteneur.pack(fill="both", expand=True)
        self.frames = {}
        for Page in (page_accueil, page_details, page_aucun_res):
            frame = Page(conteneur, self)
            self.frames[Page] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.afficher_page(page_accueil)

    def afficher_page(self, page):
        self.frames[page].tkraise()
        
    def afficher_details(self, type_element, titre, affiche_img, synopsis=None, release_date=None, note=None):
        details_frame = self.frames[page_details]
        details_frame.update_contenu(type_element, titre, affiche_img, synopsis, release_date, note)
        self.afficher_page(page_details)

    def afficher_aucun_res(self, titre, image_path, synopsis = None, release_date = None, note= None):
        recherche_frame = self.frames[page_aucun_res]
        recherche_frame.update_contenu(titre, image_path,synopsis, release_date, note)
        self.afficher_page(page_aucun_res)


###############  Page d'accueil     ###################
class page_accueil(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Top
        self.top_frame = ctk.CTkFrame(self, height=120, fg_color="#2C2C2C", border_width=0, corner_radius=0)
        self.top_frame.pack(fill="x")
        self.top_frame.pack_propagate(False)
        ctk.CTkLabel(self.top_frame, text="CinéSphere", fg_color="transparent", text_color="#dadada", font=("Arial", 24, "bold")).pack(pady=40)

        # recherche
        self.mid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mid_frame.pack(pady=20)
        self.recherche_entry = ctk.CTkEntry(self.mid_frame, width=500, height=40, fg_color="#c0c0c0",text_color="black", placeholder_text="Rechercher un film ou une série", corner_radius=100)
        self.recherche_entry.grid(row=0, column=0, padx=10)
        self.recherche_button = ctk.CTkButton(self.mid_frame, text="Rechercher", width=120, height=40,fg_color="#251ab3", hover_color="#0000bb", text_color="#FFFFFF", corner_radius=100,command=self.button_rechercher)
        self.recherche_button.grid(row=0, column=1, padx=10)

        # Films tendances
        self.creer_carousel("🔥 Tendances", "film", self.controller.afficher_details) 
        # Séries tendances
        self.creer_carousel("📺 Séries", "série", self.controller.afficher_details)          

    def button_rechercher(self):
        recherche = self.recherche_entry.get().strip()
        if not recherche:
            return
        titre, image_path, synopsis, release_date, note = rechercher(recherche)
        if image_path is None:
            self.controller.afficher_aucun_res(recherche, None)
        else:
            image = ctk.CTkImage(light_image=Image.open(image_path),size=(100, 150))
            self.controller.afficher_details("film", titre, image, synopsis, release_date, note)


    def creer_carousel(self, titre_text, type_element, appel_button):
        frame = ctk.CTkFrame(self, height=240, fg_color="#0f0f0f", corner_radius=12)
        frame.pack(fill="x", padx=40, pady=(0,30))
        frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=titre_text, font=("Arial",18,"bold"), anchor="w").pack(fill="x", padx=20, pady=(10,5))

        canvas = ctk.CTkCanvas(frame, height=200, bg="#0f0f0f", highlightthickness=0)
        canvas.pack(fill="x", expand=True, padx=10)
        carousel_frame = ctk.CTkFrame(canvas, fg_color="#0f0f0f")
        canvas.create_window((0,0), window=carousel_frame, anchor="nw")

        carousel_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.xview_scroll(int(-1*(ev.delta/120)), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        if type_element == "film" :
            elements = get_films_tendances()
        else :
            elements = get_series_tendances()
        
        for i in range(len(elements)):
            titre_btn, path_btn = elements[i]
            
            image_ctk = ctk.CTkImage(light_image=Image.open(os.path.join(os.path.dirname(__file__), path_btn)), size=(100, 150))
            titre_info, file_path,synopsis, release_date, note = rechercher(titre_btn)
            
            ctk.CTkButton(
                carousel_frame,
                width=120, height=190, fg_color="#1c1c1c", corner_radius=12,
                text=titre_btn,
                image=image_ctk,
                compound="top",
                font=("Arial",12),
                command=lambda it=type_element, t=titre_info, img=image_ctk, syn=synopsis, date=release_date, n=note: appel_button(it, t, img, syn, date, n)
            ).grid(row=0, column=i, padx=10)


# ############## Page Détails   #####################

class page_details(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.affiche_label = ctk.CTkLabel(self, text=None)
        self.affiche_label.pack(pady=20)

        self.titre_label = ctk.CTkLabel(self, font=("Arial", 20, "bold"))
        self.titre_label.pack(pady=10)

        self.synopsis_label = ctk.CTkLabel(self, font=("Arial", 14), wraplength=800, justify="left")
        self.synopsis_label.pack(pady=10)
        self.date_label = ctk.CTkLabel(self, font=("Arial", 14))
        self.date_label.pack(pady=5)
        self.note_label = ctk.CTkLabel(self, font=("Arial", 14))
        self.note_label.pack(pady=5)

        ctk.CTkButton(self, text="Retour", command=lambda: controller.afficher_page(page_accueil)).pack(pady=20)

        self.ba_frame = ctk.CTkFrame(self, fg_color="#1c1c1c", corner_radius=12)
        self.ba_frame.pack(pady=10)
        self.ba_button = None

    def update_contenu(self, type_element, titre, affiche_img, synopsis=None, release_date=None, note=None):
        self.titre_label.configure(text=f"{titre} ({type_element})")
        self.affiche_label.configure(image=affiche_img)
        self.synopsis_label.configure(text=f"Synopsis : {synopsis}" if synopsis else "")
        self.date_label.configure(text=f"Date de sortie : {release_date}" if release_date else "")
        self.note_label.configure(text=f"Note : {note}/10" if note else "")

        if self.ba_button:
            self.ba_button.destroy()
        youtube_id = get_ba(titre)
        if youtube_id:
            ba_url = f"https://www.youtube.com/watch?v={youtube_id}"
            thumb_url = f"https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg"
            with urllib.request.urlopen(thumb_url) as u:
                raw_data = u.read()
            image_pil = Image.open(io.BytesIO(raw_data))
            image_ctk = ctk.CTkImage(light_image=image_pil, size=(320,180))
            self.ba_button = ctk.CTkButton(
                self.ba_frame,
                text="▶ Voir la bande-annonce",
                image=image_ctk,
                compound="top",
                font=("Arial", 14),
                height=220,
                command=lambda: webbrowser.open(ba_url))
            self.ba_button.pack(pady=10)


# ############## Page Aucun résultat #####################

class page_aucun_res(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Label 
        self.message_label = ctk.CTkLabel(self, text="🔍 Aucun résultat trouvé", font=("Arial",24,"bold"))
        self.message_label.pack(pady=100)

        ctk.CTkButton(self, text="Retour à l'accueil", command=lambda: controller.afficher_page(page_accueil)).pack()

    def update_contenu(self, recherche, img, synopsis=None, release_date=None, note=None):
        self.message_label.configure(text=f"🔍 Aucun résultat trouvé pour : {recherche}")

##### Requêtes api #######    ==> modifier

def rechercher(recherche):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer TOKEN"
    }
    
    searchfi = recherche.replace(" ", "+")
    url = f"https://api.themoviedb.org/3/search/movie?query={searchfi}&language=fr-FR"
    reponse = requests.get(url, headers=headers, verify=False)
    data = reponse.json()

    dossier = os.path.join(os.path.dirname(os.path.abspath(__file__)), "affiche_recherche")
    os.makedirs(dossier, exist_ok=True)

    if not data.get("results"):
        return recherche, None, None, None, None

    film = data["results"][0]
    poster_path = film.get("poster_path")
    synopsis = film.get("overview")
    title = film.get("title")
    release_date = film.get("release_date")
    note = film.get("vote_average") 

    if poster_path:
        img_url = "https://image.tmdb.org/t/p/w500" + poster_path
        file_name = title.replace(" ", "_").replace("/", "_").replace(":", "_") + ".jpg"
        file_path = os.path.join(dossier, file_name)
        img_data = requests.get(img_url, verify=False).content
        with open(file_path, "wb") as f:
            f.write(img_data)
    else:
        file_path = None

    return title, file_path, synopsis, release_date, note


def get_ba(titre):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer TOKEN"
    }

    searchfi = titre.replace(" ", "+")
    url_search = f"https://api.themoviedb.org/3/search/movie?query={searchfi}&language=fr-FR"
    reponse = requests.get(url_search, headers=headers, verify=False)
    data = reponse.json()
    if not data.get("results"):
        return None
    film_id = data["results"][0]["id"]

    url_videos = f"https://api.themoviedb.org/3/movie/{film_id}/videos?language=fr-FR"
    reponse = requests.get(url_videos, headers=headers, verify=False)
    videos = reponse.json().get("results", [])

    trailers = [
        v for v in videos
        if v.get("site") == "YouTube" and v.get("type") == "Trailer"
    ]

    if not trailers:
        return None

    trailers.sort(key=lambda v: (v.get("official", False), v.get("published_at", "")), reverse=True)
    return trailers[0]["key"]


def get_films_tendances():
    headers = {
    "accept": "application/json",
    "Authorization": "Bearer TOKEN"
    }
    url = "https://api.themoviedb.org/3/movie/popular?language=fr-FR&page=1"
    reponse = requests.get(url, headers=headers, verify = False)
    data = reponse.json()

    if not data.get("results"):
        print("Aucun film trouvé.")
        return []

    dossier = os.path.join(os.path.dirname(os.path.abspath(__file__)), "affiche_film")
    os.makedirs(dossier, exist_ok=True)
    films = data["results"][:15]
    downloaded_files = []
    for film in films:
        title = film["title"]
        poster_path = film.get("poster_path")
        if not poster_path:
            print(f"Aucune affiche pour : {title}")
            downloaded_files.append(None)
            continue
        img_url = "https://image.tmdb.org/t/p/w500" + poster_path
        file_name = title.replace(" ", "_").replace("/", "_").replace(":","_")+ ".jpg"
        file_path = os.path.join(dossier, file_name)
        img_data = requests.get(img_url, verify = False).content
        with open(file_path, "wb") as f:
            f.write(img_data)
        downloaded_files.append((title, file_path))
    return downloaded_files
 
def get_series_tendances():
    headers = {
    "accept": "application/json",
    "Authorization": "Bearer TOKEN"
    }
    url = "https://api.themoviedb.org/3/tv/popular?language=fr-FR&page=1"
    reponse = requests.get(url, headers=headers, verify = False)
    data = reponse.json()

    if not data.get("results"):
        print("Aucune serie trouvé.")
        return []

    dossier = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serie")
    os.makedirs(dossier, exist_ok=True)
    series = data["results"][:15]
    downloaded_files = []
    for serie in series:
        title = serie["name"]
        poster_path = serie.get("poster_path")
        if not poster_path:
            print(f"Aucune affiche pour : {title}")
            downloaded_files.append(None)
            continue
        img_url = "https://image.tmdb.org/t/p/w500" + poster_path
        file_name = title.replace(" ", "_").replace("/", "_").replace(":","_")+ ".jpg"
        file_path = os.path.join(dossier, file_name)
        img_data = requests.get(img_url, verify = False).content
        with open(file_path, "wb") as f:
            f.write(img_data)
        downloaded_files.append((title, file_path))
    return downloaded_files





if __name__ == "__main__":
    app = App()
    app.mainloop()

