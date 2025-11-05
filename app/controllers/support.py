from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import Suporte, Notificacao
from .. import db

bp = Blueprint("support", __name__, url_prefix="/support")

@bp.route("/new", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        if "user_id" not in session:
            flash("Faça login para abrir um chamado.", "warning")
            return redirect(url_for("auth.login"))
        canal = request.form.get("canal")
        mensagem = request.form.get("mensagem")
        
        if not canal or not mensagem:
            flash("Escolha um canal e escreva sua mensagem.", "warning")
            return redirect(url_for("support.new_ticket"))
        
        ticket = Suporte(id_usuario=session["user_id"], canal=canal, mensagem=mensagem, status="Aberto")
        nova_notificacao = Notificacao(
    id_usuario=session["user_id"],
    titulo="Resposta do Suporte",
    mensagem="Seu chamado foi atualizado pela equipe."
)
        db.session.add(nova_notificacao)
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for("support.success"))
        return redirect(url_for("shop.index"))
    return render_template("support.html")

@bp.route("/success")
def success():
    return render_template("support_success.html")


@bp.route("/list")
def list_tickets():
    tickets = Suporte.query.order_by(Suporte.data_envio.desc()).all()
    return render_template("support.html", tickets=tickets)


