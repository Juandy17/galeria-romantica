from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recuerdos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "romantico"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 💌 Modelo
class Recuerdo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    archivo = db.Column(db.String(300))
    tipo = db.Column(db.String(10))
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
                tipo = 'video' if ext in ['mp4', 'mov', 'avi', 'webm'] else 'imagen'

        nuevo = Recuerdo(titulo=titulo, descripcion=descripcion, archivo=archivo, tipo=tipo)
        db.session.add(nuevo)
        db.session.commit()
        flash("Recuerdo agregado con éxito 💖", "success")
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    recuerdo = Recuerdo.query.get_or_404(id)
    if request.method == 'POST':
        recuerdo.titulo = request.form['titulo']
        recuerdo.descripcion = request.form['descripcion']

        if 'archivo' in request.files:
            file = request.files['archivo']
            if file.filename:
                carpeta = os.path.join('static', 'uploads')
                os.makedirs(carpeta, exist_ok=True)
                ruta = os.path.join(carpeta, file.filename)
                file.save(ruta)
                recuerdo.archivo = f'uploads/{file.filename}'
                ext = file.filename.split('.')[-1].lower()
                recuerdo.tipo = 'video' if ext in ['mp4', 'mov', 'avi', 'webm'] else 'imagen'

        db.session.commit()
        flash("Recuerdo editado con amor 💕", "success")
        return redirect(url_for('index'))

    return render_template('edit.html', recuerdo=recuerdo)

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    recuerdo = Recuerdo.query.get_or_404(id)
    db.session.delete(recuerdo)
    db.session.commit()
    flash("Recuerdo eliminado 💔", "danger")
    return redirect(url_for('index'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
