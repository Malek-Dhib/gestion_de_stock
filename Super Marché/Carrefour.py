import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from mysql.connector import errorcode

class StockManagerApp:
    def __init__(self, root, db_connection):
        self.root = root
        self.root.title("Gestion des Stocks")

        self.tree = ttk.Treeview(root, columns=("ID", "Nom", "Description", "Prix", "Quantité", "Catégorie"))
        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Prix", text="Prix")
        self.tree.heading("Quantité", text="Quantité")
        self.tree.heading("Catégorie", text="Catégorie")

        self.tree.pack(expand=True, fill="both")

        self.db_connection = db_connection

        # Charger les données depuis la base de données
        self.load_data()

        # Boutons d'action
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        btn_add = tk.Button(btn_frame, text="Ajouter Produit", command=self.add_product_window)
        btn_add.grid(row=0, column=0, padx=5)

        btn_remove = tk.Button(btn_frame, text="Supprimer Produit", command=self.remove_product)
        btn_remove.grid(row=0, column=1, padx=5)

        btn_edit = tk.Button(btn_frame, text="Modifier Produit", command=self.edit_product_window)
        btn_edit.grid(row=0, column=2, padx=5)

    def load_data(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM product")
        products = cursor.fetchall()

        for product in products:
            self.add_product(*product)

    def add_product_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Ajouter un Produit")

        # Labels et Entry pour les informations du produit
        tk.Label(add_window, text="Nom du Produit:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = tk.Entry(add_window)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(add_window, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        description_entry = tk.Entry(add_window)
        description_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(add_window, text="Prix:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        price_entry = tk.Entry(add_window)
        price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(add_window, text="Quantité:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        quantity_entry = tk.Entry(add_window)
        quantity_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Bouton d'ajout
        tk.Button(add_window, text="Ajouter", command=lambda: self.add_product_from_window(
            name_entry.get(), description_entry.get(), price_entry.get(), quantity_entry.get())).grid(row=4, column=0, columnspan=2, pady=10)

    def add_product_from_window(self, name, description, price, quantity):
        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Erreur", "Le prix doit être un nombre et la quantité doit être un entier.")
            return

        if name and price >= 0 and quantity >= 0:
            cursor = self.db_connection.cursor()
            cursor.execute("INSERT INTO product (name, description, price, quantity) VALUES (%s, %s, %s, %s)",
                           (name, description, price, quantity))
            self.db_connection.commit()
            self.add_product(cursor.lastrowid, name, description, price, quantity, "")
            messagebox.showinfo("Succès", "Produit ajouté avec succès.")
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs et assurer que le prix et la quantité sont des valeurs positives.")

    def add_product(self, product_id, name, description, price, quantity, category):
        self.tree.insert("", "end", values=(product_id, name, description, price, quantity, category))

    def remove_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            product_id = self.tree.item(selected_item, "values")[0]
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM product WHERE id=%s", (product_id,))
            self.db_connection.commit()
            self.tree.delete(selected_item)

    def edit_product_window(self):
        selected_item = self.tree.selection()
        if selected_item:
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Modifier un Produit")

            # Récupérer les informations du produit sélectionné
            product_id, name, description, price, quantity, category = self.tree.item(selected_item, "values")

            # Labels et Entry pour les informations mises à jour du produit
            tk.Label(edit_window, text="Nouveau Nom du Produit:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            name_entry = tk.Entry(edit_window)
            name_entry.insert(0, name)
            name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

            tk.Label(edit_window, text="Nouvelle Description:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            description_entry = tk.Entry(edit_window)
            description_entry.insert(0, description)
            description_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

            tk.Label(edit_window, text="Nouveau Prix:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
            price_entry = tk.Entry(edit_window)
            price_entry.insert(0, price)
            price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

            tk.Label(edit_window, text="Nouvelle Quantité:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
            quantity_entry = tk.Entry(edit_window)
            quantity_entry.insert(0, quantity)
            quantity_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

            # Bouton de modification
            tk.Button(edit_window, text="Modifier", command=lambda: self.edit_product_from_window(
                selected_item, name_entry.get(), description_entry.get(), price_entry.get(), quantity_entry.get())).grid(row=4, column=0, columnspan=2, pady=10)

    def edit_product_from_window(self, selected_item, name, description, price, quantity):
        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Erreur", "Le prix doit être un nombre et la quantité doit être un entier.")
            return

        if name and quantity >= 0:
            product_id = selected_item[0]

            # Débogage
            print(f"Product ID: {product_id}, Name: {name}, Description: {description}, Price: {price}, Quantity: {quantity}")

            cursor = self.db_connection.cursor()
            cursor.execute("UPDATE product SET name=%s, description=%s, price=%s, quantity=%s WHERE id=%s",
                        (name, description, price, quantity, product_id))
            self.db_connection.commit()

            # Mettre à jour les valeurs dans l'interface
            updated_values = (product_id, name, description, price, quantity, "")
            self.tree.item(selected_item, values=updated_values)

            messagebox.showinfo("Succès", "Produit modifié avec succès.")
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs et assurer que la quantité est une valeur positive.")




if __name__ == "__main__":
    # Connexion à la base de données MySQL
    try:
        conn = mysql.connector.connect(
            user='root',
            password='Malek2004',
            host='localhost',
            database='store'
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Accès refusé. Vérifiez votre nom d'utilisateur et votre mot de passe.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Base de données non existante. Créez la base de données 'store'.")
        else:
            print(err)
        exit()

    root = tk.Tk()
    app = StockManagerApp(root, conn)
    root.mainloop()

    # Fermer la connexion à la base de données après la fermeture de l'application
    conn.close()

