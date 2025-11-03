from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recuerdos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 🩷 Modelo
class Recuerdo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    archivo = db.Column(db.String(300))  # imagen o video
    tipo = db.Column(db.String(10))      # 'imagen' o 'video'
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    recuerdos = Recuerdo.query.order_by(Recuerdo.fecha.desc()).all()
    return render_template('index.html', recuerdos=recuerdos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        archivo = None
        tipo = None

        if 'archivo' in request.files:
            file = request.files['archivo']
            if file.filename:
                carpeta = os.path.join('static', 'uploads')
                os.makedirs(carpeta, exist_ok=True)
                ruta = os.path.join(carpeta, file.filename)
                file.save(ruta)

                archivo = f'uploads/{file.filename}'
                ext = file.filename.split('.')[-1].lower()
                if ext in ['mp4', 'mov', 'avi', 'webm']:
                    tipo = 'video'
                else:
                    tipo = 'imagen'

        nuevo = Recuerdo(titulo=titulo, descripcion=descripcion, archivo=archivo, tipo=tipo)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)
