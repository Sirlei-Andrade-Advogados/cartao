# -*- coding: utf-8 -*-
"""Quem tem cartão digital no site, e os dados de cada um.

Para incluir um advogado novo: copie o bloco de "alessandro", troque os
dados, ponha a foto quadrada na pasta dele e rode, na ordem:

    python gerar_paginas.py
    python gerar_vcf.py
    python gerar_contato.py

A Dra. Sirlei é a matriz: a página dela (index.html na raiz) é o modelo
de onde as outras são derivadas.

CONGELADO: os arquivos da Dra. Sirlei (página, contatos .vcf, tela de
contato e QR codes) já estão publicados e o QR já foi para a gráfica.
Nenhum gerador escreve nada dela. Não edite o index.html da raiz nem os
arquivos dela; ajustes para os outros cartões são feitos em gerar_paginas.py.
"""

ESCRITORIO = {
    "empresa": "Sirlei Andrade Advogados Associados",
    "site": "https://www.sirleiadv.com.br",
    "rua": "Rua Barão de Itaim, 83-A - Granja Julieta",
    "cidade": "São Paulo",
    "uf": "SP",
    "cep": "04720-030",
    "pais": "Brasil",
}

URL_BASE = "https://sirlei-andrade-advogados.github.io/cartao/"

PESSOAS = {
    # ---------------------------------------------------------------- matriz
    "sirlei": {
        "pasta": "",                          # raiz do site
        "congelado": True,                    # publicado e impresso: não regerar
        "nome": "Sirlei",
        "sobrenome": "Andrade",
        "completo": "Sirlei Andrade",
        "celular": "+5511947234782",
        "email": "sirlei@sirleiadv.com.br",
        "foto": "sirlei.jpg",
        "cargo": {"pt": "Sócia-fundadora", "en": "Founding Partner"},
    },
    # ------------------------------------------------------------------------
    "alessandro": {
        "pasta": "alessandro",
        "nome": "Alessandro",
        "sobrenome": "Louzado",
        "completo": "Alessandro Louzado",
        "iniciais": "AL",
        "celular": "+5511982072944",
        "email": "alessandro@sirleiadv.com.br",
        "foto": "alessandro.jpg",
        "cargo": {"pt": "Advogado", "en": "Attorney"},
        "bio": {
            "pt": ["Especializado em Direito Empresarial.",
                   "Responsável pela gestão e coordenação da equipe do "
                   "contencioso estratégico do escritório."],
            "en": ["Specialized in Business Law.",
                   "Responsible for managing and coordinating the firm's "
                   "strategic litigation team."],
        },
        # (chave, português, inglês)
        "areas": [
            ("area_empresarial", "Direito Empresarial", "Business Law"),
            ("area_contencioso", "Contencioso Estratégico", "Strategic Litigation"),
        ],
        # A linha da OAB na seção Empresa é a da Dra. Sirlei. Preencha com o
        # número dele para exibir a própria; vazio, a linha some.
        "oab": "",
    },
}


def telefone_br(e164: str) -> str:
    """+5511982072944 -> (11) 98207-2944"""
    d = e164.lstrip("+")[2:]
    return f"({d[:2]}) {d[2:-4]}-{d[-4:]}"
