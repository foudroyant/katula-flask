import io
from flask import Flask, render_template,send_file, request, jsonify
import os
import threading
import time
from rembg import remove 
from PIL import Image 
import uvicorn
from werkzeug.utils import secure_filename


# Chemin du fichier à supprimer (exemple)
FILE_PATH = "static/temp_file.txt"
def delete_file_after_delay(file_path, delay):
    """Supprime le fichier après un délai spécifié."""
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Fichier supprimé : {file_path}")
    else:
        print(f"Fichier introuvable : {file_path}")

app = Flask(__name__)

# Dossier pour stocker les images uploadées
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Créer les dossiers si nécessaire
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def remove_bg():
    # Store path of the image in the variable input_path 
    input_path =  'inputs/profilcomeup.jpg' 
    
    # Store path of the output image in the variable output_path 
    output_path = 'outputs/1.png' 
    
    # Processing the image 
    input = Image.open(input_path) 
    
    # Removing the background from the given Image 
    output = remove(input) 
    
    #Saving the image in the given path 
    output.save(output_path) 


@app.route("/")
def index():
    
    # Rend la page HTML
    return render_template('index.html', data={})

@app.route('/upload', methods=['POST'])
def upload():
    """Traite l'upload et transforme l'image"""
    file = request.files.get('image')
    if file:
        # Sécuriser le nom de fichier
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], filename.rsplit('.', 1)[0] + '.png')  # Sauvegarder en PNG

        # Sauvegarder le fichier uploadé
        file.save(upload_path)

        # Supprimer l'arrière-plan
        with open(upload_path, 'rb') as input_file:
            input_data = input_file.read()
            output_data = remove(input_data)

            # Convertir les données en PNG
            image = Image.open(io.BytesIO(output_data))
            image = image.convert("RGBA")  # Assurez-vous que l'image est en mode RGBA
            image.save(processed_path, 'PNG')  # Sauvegarder l'image en PNG
        
        # Lancer un thread pour supprimer l'image après 3 minutes (180 secondes)
        threading.Thread(target=delete_file_after_delay, args=(processed_path, 180)).start()
        threading.Thread(target=delete_file_after_delay, args=(upload_path, 180)).start()
        # Retourner la réponse HTMX
        return render_template('uploaded.html', image_url=processed_path, download_url=f'/download/{filename.rsplit(".", 1)[0]}.png')
    
    return jsonify({'error': 'Aucun fichier reçu'}), 400

@app.route('/download/<filename>')
def download(filename):
    """Permet de télécharger l'image transformée"""
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(processed_path):
        return send_file(processed_path, as_attachment=True)
    return "Fichier introuvable", 404

if __name__ == '__main__':
    app.run(debug=True)
    #uvicorn.run()