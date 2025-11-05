from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import Usuario
from .. import db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        if not nome or not email or not senha:
            flash("Preencha todos os campos para se cadastrar.", "warning")
            return redirect(url_for("auth.register"))
    
        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.", "danger")
            return redirect(url_for("auth.register"))
        user = Usuario(nome=nome, email=email, senha=senha)
        db.session.add(user)
        db.session.commit()
        flash("Conta criada com sucesso. Faça login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        
        if not email or not senha:
            flash("Informe e-mail e senha para continuar.", "warning")
            return redirect(url_for("auth.login"))
        
        user = Usuario.query.filter_by(email=email, senha=senha).first()
        if user:
            session["user_id"] = user.id_usuario
            session["user_name"] = user.nome
            flash("Bem-vindo, " + user.nome, "success")
            return redirect(url_for("shop.index"))
        flash("Credenciais inválidas.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("login.html")

@bp.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.", "info")
    return redirect(url_for("shop.index"))
