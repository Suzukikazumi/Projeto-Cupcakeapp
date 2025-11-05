from . import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)  # em produção: hash
    data_nascimento = db.Column(db.Date)
    endereco = db.Column(db.String(255))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    pedidos = db.relationship("Pedido", backref="usuario", lazy=True)
    avaliacoes = db.relationship("Avaliacao", backref="usuario", lazy=True)
    personalizados = db.relationship("CupcakePersonalizado", backref="usuario", lazy=True)
    notificacoes = db.relationship("Notificacao", backref="usuario", lazy=True)
    suportes = db.relationship("Suporte", backref="usuario", lazy=True)

class Cupcake(db.Model):
    __tablename__ = "cupcake"
    id_cupcake = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Numeric(8,2), nullable=False)
    categoria = db.Column(db.String(50))
    imagem = db.Column(db.String(255))

    avaliacoes = db.relationship("Avaliacao", backref="cupcake", lazy=True)
    itens = db.relationship("ItemPedido", backref="cupcake", lazy=True)

class CupcakePersonalizado(db.Model):
    __tablename__ = "cupcake_personalizado"
    id_personalizado = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    massa = db.Column(db.String(50))
    recheio = db.Column(db.String(50))
    cobertura = db.Column(db.String(50))
    decoracao = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    preco_final = db.Column(db.Numeric(8,2))
    endereco_entrega = db.Column(db.String(200))
    forma_pagamento = db.Column(db.String(50))
    cupom_utilizado = db.Column(db.String(20), nullable=True)
    data_pedido = db.Column(db.DateTime, default=db.func.current_timestamp())


class Cupom(db.Model):
    __tablename__ = "cupom"
    id_cupom = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    valor_desconto = db.Column(db.Numeric(5,2))
    ativo = db.Column(db.Boolean, default=True)
    data_validade = db.Column(db.Date)

    pedidos = db.relationship("Pedido", backref="cupom", lazy=True)

class Pedido(db.Model):
    __tablename__ = "pedido"
    id_pedido = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_cupom = db.Column(db.Integer, db.ForeignKey("cupom.id_cupom"))
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))
    valor_total = db.Column(db.Numeric(10,2))
    forma_pagamento = db.Column(db.String(50))
    endereco_entrega = db.Column(db.String(255))
    cupom_utilizado = db.Column(db.String(20))

    itens = db.relationship("ItemPedido", backref="pedido", lazy=True)

class ItemPedido(db.Model):
    __tablename__ = "item_pedido"
    id_item = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    id_cupcake = db.Column(db.Integer, db.ForeignKey("cupcake.id_cupcake"), nullable=False)
    quantidade = db.Column(db.Integer)
    preco_unitario = db.Column(db.Numeric(8,2))

class Avaliacao(db.Model):
    __tablename__ = "avaliacao"
    id_avaliacao = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_cupcake = db.Column(db.Integer, db.ForeignKey("cupcake.id_cupcake"), nullable=False)
    nota = db.Column(db.Integer)
    comentario = db.Column(db.Text)
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)
    status_moderacao = db.Column(db.String(20))

class Notificacao(db.Model):
    __tablename__ = "notificacao"
    id_notificacao = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    titulo = db.Column(db.String(100))
    mensagem = db.Column(db.Text)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(50))

class Suporte(db.Model):
    __tablename__ = "suporte"
    id_suporte = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    canal = db.Column(db.String(20))
    mensagem = db.Column(db.Text)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))
