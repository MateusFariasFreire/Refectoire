from refectorymanager import RefectoryManager
from user import User
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import cv2
import face_recognition
import os

# Identifiants de l'administrateur
id_admin = "Admin"
password_admin = "admin"
is_logged_in = False

# Chemin vers le fichier de données des utilisateurs
file_path = "users_data.json"
refectory_manager = RefectoryManager(file_path)

# Fonction pour sauvegarder une image
def save_image(image, filename):
    cv2.imwrite(filename, image)

# Fonction pour ouvrir le panneau d'administration
def openAdminPanel():
    admin_window = tk.Tk()
    admin_window.title("Panneau d'administration")
    admin_window.geometry("600x500")

    # Création des cadres pour chaque section
    main_menu_frame = tk.Frame(admin_window)
    user_management_frame = None
    access_control_frame = None

    # Fonction pour créer et afficher la frame de gestion des utilisateurs
    def createUserManagementFrame():
        # Mettre à jour les données des utilisateurs
        refectory_manager.updateUsersData()
        nonlocal user_management_frame, main_menu_frame
        if user_management_frame:
            user_management_frame.pack_forget()
            user_management_frame.destroy()

        user_management_frame = tk.Frame(admin_window)

        label_user_management = tk.Label(user_management_frame, text="Gestion des utilisateurs", font=("Helvetica", 16))
        label_user_management.pack(pady=20)

        # Création du Treeview pour afficher les utilisateurs
        columns = ("id", "nom", "solde", "role")
        user_treeview = ttk.Treeview(user_management_frame, columns=columns, show='headings')

        # Configuration des colonnes
        user_treeview.heading("id", text="ID")
        user_treeview.heading("nom", text="Nom")
        user_treeview.heading("solde", text="Solde")
        user_treeview.heading("role", text="Rôle")

        user_treeview.column("id", width=50)
        user_treeview.column("nom", width=150)
        user_treeview.column("solde", width=100)
        user_treeview.column("role", width=100)

        # Ajout des utilisateurs au Treeview
        for user in refectory_manager.getAllUsers():
            user_treeview.insert("", tk.END, values=(user["id"], user["name"], user["balance"], user["role"]))

        user_treeview.pack(pady=10)

        # Fonction pour ouvrir une nouvelle fenêtre avec les détails de l'utilisateur sélectionné
        def openUserDetails(event):
            selected_item = user_treeview.selection()[0]
            selected_user = user_treeview.item(selected_item, "values")
            if selected_user:
                user_details_window = tk.Toplevel(admin_window)
                user_details_window.title(f"Détails de {selected_user[1]}")
                user_details_window.geometry("400x300")

                # Champs de saisie pour les détails de l'utilisateur
                id_label = tk.Label(user_details_window, text=f"ID:{selected_user[0]}", font=("Helvetica", 12))
                id_label.pack(pady=5)

                name_label = tk.Label(user_details_window, text="Nom:", font=("Helvetica", 12))
                name_label.pack(pady=5)
                name_entry = tk.Entry(user_details_window, font=("Helvetica", 12))
                name_entry.insert(0, selected_user[1])
                name_entry.pack(pady=5)

                balance_label = tk.Label(user_details_window, text="Solde:", font=("Helvetica", 12))
                balance_label.pack(pady=5)
                balance_entry = tk.Entry(user_details_window, font=("Helvetica", 12))
                balance_entry.insert(0, selected_user[2])
                balance_entry.pack(pady=5)

                role_label = tk.Label(user_details_window, text="Rôle:", font=("Helvetica", 12))
                role_label.pack(pady=5)
                role_entry = tk.Entry(user_details_window, font=("Helvetica", 12))
                role_entry.insert(0, selected_user[3])
                role_entry.pack(pady=5)

                # Fonction pour sauvegarder les modifications
                def saveChanges():
                    new_name = name_entry.get()
                    new_balance = balance_entry.get()
                    new_role = role_entry.get()

                    user_from_db = refectory_manager.findUserByID(int(selected_user[0]))
                    user_from_db.setName(new_name)
                    user_from_db.setBalance(float(new_balance))
                    user_from_db.setRole(new_role)

                    refectory_manager.saveUserData(user_from_db)

                    # Mettre à jour le Treeview
                    user_treeview.item(selected_item, values=(selected_user[0], new_name, new_balance, new_role))
                    user_details_window.destroy()

                save_button = tk.Button(user_details_window, text="Sauvegarder", font=("Helvetica", 12), command=saveChanges)
                save_button.pack(pady=10)

        def addUser():
            add_user_window = tk.Toplevel(admin_window)
            add_user_window.title("Ajouter un utilisateur")
            add_user_window.geometry("400x350")

            # Variable pour stocker l'image capturée
            captured_image = None

            # Champs de saisie pour les détails du nouvel utilisateur
            name_label = tk.Label(add_user_window, text="Nom:", font=("Helvetica", 12))
            name_label.pack(pady=5)
            name_entry = tk.Entry(add_user_window, font=("Helvetica", 12))
            name_entry.pack(pady=5)

            role_label = tk.Label(add_user_window, text="Rôle:", font=("Helvetica", 12))
            role_label.pack(pady=5)
            role_entry = tk.Entry(add_user_window, font=("Helvetica", 12))
            role_entry.pack(pady=5)

            # Bouton pour ouvrir la caméra
            def openCamera():
                nonlocal captured_image
                cap = cv2.VideoCapture(0)

                # Créer une nouvelle fenêtre pour afficher la caméra
                camera_window = tk.Toplevel(add_user_window)
                camera_window.title("Caméra")
                camera_window.geometry("640x480")

                # Afficher la caméra en temps réel
                while True:
                    ret, frame = cap.read()
                    if ret:
                        cv2.imshow("Camera", frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                        if cv2.waitKey(1) & 0xFF == ord('c'):
                            nonlocal captured_image
                            ret, frame = cap.read()
                            if ret:
                                captured_image = frame
                            cap.release()
                            cv2.destroyAllWindows()
                            break
                    if captured_image is not None:
                        break

                cap.release()
                cv2.destroyAllWindows()
                camera_window.destroy()

            open_camera_button = tk.Button(add_user_window, text="Ouvrir la caméra", font=("Helvetica", 12),
                                           command=openCamera)
            open_camera_button.pack(pady=10)

            # Fonction pour sauvegarder le nouvel utilisateur
            def saveNewUser():
                nonlocal captured_image
                new_name = name_entry.get()
                new_role = role_entry.get()

                new_user_id = refectory_manager.addUser(new_name, new_role)

                # Sauvegarder l'image si elle a été capturée
                if captured_image is not None:
                    image_filename = f"dossier_images/{new_name}_{new_user_id}.jpg"
                    save_image(captured_image, image_filename)

                # Mettre à jour le Treeview
                user_treeview.insert("", tk.END, values=(new_user_id, new_name, "0", new_role))
                add_user_window.destroy()

            save_button = tk.Button(add_user_window, text="Ajouter", font=("Helvetica", 12), command=saveNewUser)
            save_button.pack(pady=10)

        # Lier l'événement de clic à la Treeview
        user_treeview.bind('<<TreeviewSelect>>', openUserDetails)

        add_user_button = tk.Button(user_management_frame, text="Ajouter un utilisateur", font=("Helvetica", 12), command=addUser)
        add_user_button.pack(pady=10)

        button_back_to_main_user = tk.Button(user_management_frame, text="Retour au menu principal", font=("Helvetica", 12), command=lambda: showFrame(main_menu_frame))
        button_back_to_main_user.pack(pady=10)

        showFrame(user_management_frame)

    # Fonction pour créer et afficher la frame de contrôle d'accès
    def createAccessControlFrame():
        nonlocal access_control_frame, main_menu_frame
        if access_control_frame:
            access_control_frame.pack_forget()
            access_control_frame.destroy()

        access_control_frame = tk.Frame(admin_window)

        label_access_control = tk.Label(access_control_frame, text="Contrôle d'accès", font=("Helvetica", 16))
        label_access_control.pack(pady=20)

        button_back_to_main_access = tk.Button(access_control_frame, text="Retour au menu principal", font=("Helvetica", 12), command=lambda: showFrame(main_menu_frame))
        button_back_to_main_access.pack(pady=10)

        showFrame(access_control_frame)
        detection_visages()

    # Fonction pour afficher un cadre spécifique
    def showFrame(frame):
        main_menu_frame.pack_forget()
        if user_management_frame:
            user_management_frame.pack_forget()
        if access_control_frame:
            access_control_frame.pack_forget()
        frame.pack(pady=20)

    # Contenu du menu principal
    label_welcome = tk.Label(main_menu_frame, text="Bienvenue dans le panneau d'administration!", font=("Helvetica", 16))
    label_welcome.pack(pady=20)

    button_user_management = tk.Button(main_menu_frame, text="Gestion des utilisateurs", font=("Helvetica", 12), command=createUserManagementFrame)
    button_user_management.pack(pady=10)

    button_access_control = tk.Button(main_menu_frame, text="Contrôle d'accès", font=("Helvetica", 12), command=createAccessControlFrame)
    button_access_control.pack(pady=10)

    main_menu_frame.pack(pady=20)

    admin_window.mainloop()

# Fonction pour la connexion de l'administrateur
def adminLogin():
    global is_logged_in
    def checkLogin():
        username = admin_username.get()
        password = admin_password.get()
        if username == id_admin and password == password_admin:
            main_window.destroy()
            global is_logged_in
            is_logged_in = True
        else:
            messagebox.showerror("Erreur de connexion", "Nom d'utilisateur ou mot de passe incorrect.")

    main_window = tk.Tk()
    main_window.title("Refectoire")
    main_window.geometry("400x200")

    # Configuration de la grille pour centrer les éléments
    main_window.grid_rowconfigure(0, weight=1)
    main_window.grid_rowconfigure(1, weight=1)
    main_window.grid_rowconfigure(2, weight=1)
    main_window.grid_rowconfigure(3, weight=1)
    main_window.grid_columnconfigure(0, weight=1)
    main_window.grid_columnconfigure(1, weight=1)
    main_window.grid_columnconfigure(2, weight=1)

    # Ajout de labels pour les champs de saisie
    label_username = tk.Label(main_window, text="Nom d'utilisateur:", font=("Helvetica", 12))
    label_password = tk.Label(main_window, text="Mot de passe:", font=("Helvetica", 12))

    admin_username = tk.Entry(main_window, font=("Helvetica", 12))
    admin_password = tk.Entry(main_window, show="*", font=("Helvetica", 12))

    label_username.grid(row=1, column=1, pady=10)
    admin_username.grid(row=1, column=2, pady=10)
    label_password.grid(row=2, column=1, pady=10)
    admin_password.grid(row=2, column=2, pady=10)

    button_detection = tk.Button(main_window, text="Se connecter", font=("Helvetica", 12), command=checkLogin)
    button_detection.grid(row=3, column=1, columnspan=2, pady=20)

    main_window.mainloop()

# Fonction pour charger les visages connus
def load_known_faces():
    known_encodings = []
    known_names = []
    known_ids = []  # Ajouter une liste pour les IDs

    for file in os.listdir("dossier_images"):
        if file.endswith(".jpg") or file.endswith(".png"):
            image_path = os.path.join("dossier_images", file)
            # Charger l'image et encoder le visage
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:  # S'assurer qu'un visage est détecté
                known_encodings.append(encodings[0])

                # Extraire le nom et l'ID à partir du fichier
                name, id_part = file.split('_')[0], file.split('_')[1].split('.')[0]
                known_names.append(name)
                known_ids.append(id_part)
    return known_encodings, known_names, known_ids

# Fonction pour la détection des visages
def detection_visages():
    known_encodings, known_names, known_ids = load_known_faces()

    if not known_encodings:
        messagebox.showwarning("Erreur", "Aucune image enregistrée pour la reconnaissance.")
        return

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Erreur", "Impossible d'accéder à la caméra.")
        return

    messagebox.showinfo("Info", "Appuyez sur 'q' pour quitter la détection.")

    frame_skip = 120  # Nombre de cadres à ignorer entre les traitements
    current_frame = 0
    last_scanned_id = None  # Variable pour garder l'ID de la dernière personne scannée

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Redimensionner pour un traitement plus rapide
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        if current_frame % frame_skip == 0:
            # Localiser les visages dans le cadre
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # Prendre seulement le premier visage détecté
            if face_locations:
                face_locations = [face_locations[0]]
                face_encodings = [face_encodings[0]]
                face_names = []
                face_ids = []

                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_encodings, face_encoding)
                    name = "Inconnu"
                    face_id = "N/A"

                    if True in matches:
                        match_index = matches.index(True)
                        name = known_names[match_index]
                        face_id = known_ids[match_index]

                    face_names.append(name)
                    face_ids.append(face_id)
            else:
                face_names = []
                face_ids = []

        current_frame += 1

        # Dessiner le rectangle et afficher le nom et l'ID pour le visage détecté
        for (top, right, bottom, left), name, face_id in zip(face_locations, face_names, face_ids):
            # Remettre les coordonnées à l'échelle originale
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            text = f"{name} (ID: {face_id})"
            cv2.putText(frame, text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            if face_id != last_scanned_id and face_id != "N/A":
                found_user = refectory_manager.findUserByID(int(face_id))
                if found_user:
                    if refectory_manager.payMeal(found_user):
                        payment_status = "Paiement reussi"
                    else:
                        payment_status = "Fonds Insuffisants"

                    # Afficher le statut du paiement à l'écran
                    cv2.putText(frame, payment_status, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    # Mettre à jour l'ID de la dernière personne scannée
                    last_scanned_id = face_id

        cv2.imshow("Detection et reconnaissance des visages", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    adminLogin()
    if not is_logged_in:
        exit()

    openAdminPanel()
