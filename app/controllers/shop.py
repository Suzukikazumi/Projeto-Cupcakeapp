from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import Cupcake, Pedido, ItemPedido, Usuario, Cupom, Avaliacao, Notificacao, CupcakePersonalizado
from .. import db
from decimal import Decimal

bp = Blueprint("shop", __name__, url_prefix="")

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/catalog")
def catalog():
    cupcakes = Cupcake.query.all()
    return render_template("catalog.html", cupcakes=cupcakes)

@bp.route("/add-to-cart/<int:cupcake_id>", methods=["POST"])
def add_to_cart(cupcake_id):
    qty = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    cart_item = cart.get(str(cupcake_id), {"quantity": 0})
    cart_item["quantity"] = cart_item.get("quantity", 0) + qty
    cart_item["cupcake_id"] = cupcake_id
    cart[str(cupcake_id)] = cart_item
    session["cart"] = cart
    flash("Adicionado ao carrinho.", "success")
    return redirect(url_for("shop.catalog"))

@bp.route("/remove-from-cart/<int:cupcake_id>", methods=["POST"])
def remove_from_cart(cupcake_id):
    cart = session.get("cart", {})
    cupcake_key = str(cupcake_id)
    
    if cupcake_key in cart:
        cart.pop(cupcake_key)  # remove o item do dicionário
        session["cart"] = cart
        flash("Item removido do carrinho.", "success")
    else:
        flash("Item não encontrado no carrinho.", "warning")

    return redirect(url_for("shop.cart"))


@bp.route("/cart")
def cart():
    cart = session.get("cart", {})
    items = []
    total = Decimal("0.00")
    for key, it in cart.items():
        cup = Cupcake.query.get(int(key))
        if not cup:
            continue
        sub = cup.preco * it["quantity"]
        items.append({"cupcake": cup, "quantity": it["quantity"], "subtotal": sub})
        total += sub
    return render_template("cart.html", items=items, total=total)

@bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user_id" not in session:
        flash("Faça login para finalizar a compra.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        acao = request.form.get("acao")
        user_id = session["user_id"]
        endereco = request.form.get("endereco")
        forma_pagamento = request.form.get("forma_pagamento")
        cupom_codigo = request.form.get("cupom")
        cart = session.get("cart", {})

        if acao == "aplicar_cupom":
            if cupom_codigo:
                cupom = Cupom.query.filter_by(codigo=cupom_codigo, ativo=True).first()
                if cupom:
                    session["cupom_codigo"] = cupom.codigo
                    session["cupom_desconto"] = float(cupom.valor_desconto)
                    flash(f"Cupom '{cupom.codigo}' aplicado ({cupom.valor_desconto:.0f}% OFF)!", "success")
                else:
                    flash("Cupom inválido ou expirado.", "danger")
            else:
                flash("Digite um código de cupom.", "warning")
            return redirect(url_for("shop.checkout"))

        if not endereco or not forma_pagamento:
            flash("Por favor, preencha o endereço e a forma de pagamento.", "warning")
            return redirect(url_for("shop.checkout"))

        if not cart:
            flash("Carrinho vazio.", "warning")
            return redirect(url_for("shop.catalog"))

        total = 0
        for k, v in cart.items():
            cup = Cupcake.query.get(int(k))
            total += float(cup.preco) * int(v["quantity"])

        if "cupom_desconto" in session:
            valor_desconto = float(session["cupom_desconto"])
            total *= (1 - valor_desconto / 100)

        order = Pedido(
            id_usuario=user_id,
            status="Aguardando Pagamento",
            valor_total=total,
            forma_pagamento=forma_pagamento,
            endereco_entrega=endereco,
            cupom_utilizado=session.get("cupom_codigo")
        )

        db.session.add(order)
        db.session.flush()
        db.session.commit()

        session.pop("cart", None)
        session.pop("cupom_codigo", None)
        session.pop("cupom_desconto", None)

        flash("Pedido criado com sucesso!", "success")
        return redirect(url_for("shop.index", id_pedido=order.id_pedido))

    
    return render_template("checkout.html")




@bp.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Faça login primeiro.", "warning")
        return redirect(url_for("auth.login"))
    user = Usuario.query.get(session["user_id"])
    return render_template("profile.html", user=user)
@bp.route("/orders")
def orders():
    if "user_id" not in session:
        flash("Faça login para ver seus pedidos.", "warning")
        return redirect(url_for("auth.login"))

    pedidos = Pedido.query.filter_by(id_usuario=session["user_id"]).all()
    return render_template("orders.html", pedidos=pedidos)

@bp.route("/reviews")
def reviews():
    avaliacoes = Avaliacao.query.all()
    return render_template("reviews.html", avaliacoes=avaliacoes)

@bp.route("/review/<int:cupcake_id>", methods=["GET", "POST"])
def review(cupcake_id):
    if "user_id" not in session:
        flash("Você precisa estar logado para avaliar um cupcake.", "warning")
        return redirect(url_for("auth.login"))

    cupcake = Cupcake.query.get_or_404(cupcake_id)

    if request.method == "POST":
        nota = int(request.form.get("nota"))
        comentario = request.form.get("comentario")

        nova_avaliacao = Avaliacao(
            id_usuario=session["user_id"],
            id_cupcake=cupcake_id,
            nota=nota,
            comentario=comentario
        )
        db.session.add(nova_avaliacao)
        db.session.commit()

        flash("Avaliação enviada com sucesso!", "success")
        return redirect(url_for("shop.reviews"))

    return render_template("review_form.html", cupcake=cupcake)

@bp.route("/apply-coupon", methods=["POST"])
def apply_coupon():
    codigo = request.form.get("codigo")
    cupom = Cupom.query.filter_by(codigo=codigo, ativo=True).first()

    if not cupom:
        flash("Cupom inválido ou expirado.", "danger")
        return redirect(url_for("shop.checkout"))

    session["cupom_codigo"] = cupom.codigo
    session["cupom_desconto"] = cupom.desconto
    flash(f"Cupom '{cupom.codigo}' aplicado! Desconto de {cupom.desconto:.0f}%.", "success")
    return redirect(url_for("shop.checkout"))

@bp.route("/custom", methods=["GET", "POST"])
def custom_cupcake():
    if "user_id" not in session:
        flash("Faça login para criar um cupcake personalizado.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        massa = request.form.get("massa")
        cobertura = request.form.get("cobertura")
        recheio = request.form.get("recheio")
        decoracao = request.form.get("decoracao")
        observacoes = request.form.get("observacoes")
        endereco = request.form.get("endereco")
        forma_pagamento = request.form.get("forma_pagamento")
        cupom_codigo = request.form.get("cupom")

        if not massa or not cobertura or not recheio:
            flash("Por favor, selecione sabor, cobertura e recheio.", "warning")
            return redirect(url_for("shop.custom_cupcake"))
        if not endereco or not forma_pagamento:
            flash("Informe o endereço e a forma de pagamento.", "warning")
            return redirect(url_for("shop.custom_cupcake"))

        preco_base = 5.0
        extras = 0
        if cobertura: extras += 1.0
        if recheio: extras += 1.5
        if decoracao: extras += 1.0
        preco_final = preco_base + extras

        cupom_usado = None
        if cupom_codigo:
            cupom = Cupom.query.filter_by(codigo=cupom_codigo, ativo=True).first()
            if cupom:
                desconto = float(cupom.valor_desconto)
                preco_final *= (1 - desconto / 100)
                cupom_usado = cupom.codigo
                flash(f"Cupom '{cupom_usado}' aplicado ({cupom.valor_desconto:.0f}% OFF)!", "success")
            else:
                flash("Cupom inválido ou expirado.", "danger")

        novo = CupcakePersonalizado(
            id_usuario=session["user_id"],
            massa=massa,
            cobertura=cobertura,
            recheio=recheio,
            decoracao=decoracao,
            observacoes=observacoes,
            preco_final=preco_final,
            endereco_entrega=endereco,
            forma_pagamento=forma_pagamento,
            cupom_utilizado=cupom_usado
        )

        db.session.add(novo)
        db.session.commit()

        pedido = Pedido(
            id_usuario=session["user_id"],
            status="Em produção",
            valor_total=preco_final,
            forma_pagamento=forma_pagamento,
            endereco_entrega=endereco,
            cupom_utilizado=cupom_usado
        )
        db.session.add(pedido)
        db.session.flush()

        notificacao = Notificacao(
            id_usuario=session["user_id"],
            titulo="Cupcake Personalizado Criado",
            mensagem=f"Seu cupcake personalizado foi criado com sucesso! Valor final: R$ {preco_final:.2f}"
        )
        db.session.add(notificacao)
        db.session.commit()

        flash("Cupcake personalizado criado e pedido registrado com sucesso!", "success")
        return redirect(url_for("shop.index"))

    return render_template("custom_cupcake.html")



