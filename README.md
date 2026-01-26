# CinéSphere

> Application Python développée dans le cadre d'un projet de NSI exploitant une API REST pour rechercher et afficher des films et séries populaires.

---

**Développé par Noé Poirier/ppnop et Dylan Courapied**

## Présentation

**CinéSphere** est une application développée en Python permettant de :
- rechercher des films par titre,
- afficher les films et séries populaires du moment,
- consulter les détails d’un film (affiche, synopsis, note, date de sortie, bande-annonce).

Le projet exploite l’API **The Movie Database (TMDB)** et met en œuvre une architecture simple à base de **pages Tkinter superposées**.

---

## Architecture de l’application

L’application repose sur une fenêtre principale qui agit comme **contrôleur**, et plusieurs pages qui représentent les différentes vues.

### Principe
App (CTk)
   - conteneur (CTkFrame)
      - page_accueil
      - page_details
      - page_aucun_res
      
Navigation entre les pages avec tkraise()

