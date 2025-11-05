from flask import Blueprint, render_template, session, redirect, url_for, flash
from ..models import Notificacao
from .. import db

bp = Blueprint("notifications", __name__, url_prefix="/notifications")

@bp.route("/")
def list_notifications():
    if "user_id" not in session:
        flash("Faça login para visualizar suas notificações.", "warning")
        return redirect(url_for("auth.login"))
    
    notificacoes = Notificacao.query.filter_by(id_usuario=session["user_id"]).order_by(Notificacao.data_envio.desc()).all()
    return render_template("notifications.html", notificacoes=notificacoes)

@bp.route("/read/<int:notificacao_id>")
def mark_as_read(notificacao_id):
    notificacao = Notificacao.query.get_or_404(notificacao_id)
    notificacao.lida = True
    db.session.commit()
    flash("Notificação marcada como lida.", "info")
    return redirect(url_for("notifications.list_notifications"))
