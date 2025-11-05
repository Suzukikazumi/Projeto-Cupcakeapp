from flask import Blueprint, render_template, session, redirect, url_for, flash
from ..models import Usuario, Pedido, Cupcake, Suporte, Cupom
from .. import db

bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required():
    user_id = session.get("user_id")
    if not user_id:
        flash("Faça login como administrador para acessar o painel.", "warning")
        return False
    user = Usuario.query.get(user_id)
    if not user or not user.email.endswith("@admin.com"):
        flash("Acesso restrito ao administrador.", "danger")
        return False
    return True


@bp.route("/")
def dashboard():
    if not admin_required():
        return redirect(url_for("auth.login"))
    
    total_usuarios = Usuario.query.count()
    total_pedidos = Pedido.query.count()
    total_cupcakes = Cupcake.query.count()
    total_cupons = Cupom.query.count()
    total_mensagens = Suporte.query.count()
    
    return render_template("admin/dashboard.html",
                           total_usuarios=total_usuarios,
                           total_pedidos=total_pedidos,
                           total_cupcakes=total_cupcakes,
                           total_cupons=total_cupons,
                           total_mensagens=total_mensagens)


@bp.route("/pedidos")
def pedidos():
    if not admin_required():
        return redirect(url_for("auth.login"))
    pedidos = Pedido.query.all()
    return render_template("admin/pedidos.html", pedidos=pedidos)


@bp.route("/usuarios")
def usuarios():
    if not admin_required():
        return redirect(url_for("auth.login"))
    usuarios = Usuario.query.all()
    return render_template("admin/usuarios.html", usuarios=usuarios)


@bp.route("/cupcakes")
def cupcakes():
    if not admin_required():
        return redirect(url_for("auth.login"))
    cupcakes = Cupcake.query.all()
    return render_template("admin/cupcakes.html", cupcakes=cupcakes)


@bp.route("/suporte")
def suporte():
    if not admin_required():
        return redirect(url_for("auth.login"))
    mensagens = Suporte.query.all()
    return render_template("admin/suporte.html", mensagens=mensagens)
