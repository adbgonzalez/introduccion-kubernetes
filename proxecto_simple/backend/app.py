from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return "Benvido á aplicación Flask!"

@app.route('/api/saudo/<nome>')
def saudo(nome):
    return f"Ola, {nome}!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
