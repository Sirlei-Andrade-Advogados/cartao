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
        "cargo": {"pt": "Coordenador do Contencioso", "en": "Litigation Coordinator"},
        "bio": {
            "pt": ["Sócio Sênior da Sirlei Andrade Advogados, com mais de 25 anos de "
                   "atuação jurídica. Bacharel em Direito pela FIG, com formação "
                   "complementar em Processo Civil (PUC-SP), Direito Empresarial, "
                   "Constitucional e Imobiliário (ESA OAB/SP). Mestrando pela PUC-SP.",
                   "Atua em contratos, contencioso estratégico, due diligence "
                   "imobiliária e aquisição de ativos."],
            "en": ["Senior Partner at Sirlei Andrade Advogados, with more than 25 years "
                   "of legal practice. Bachelor of Laws from FIG, with complementary "
                   "training in Civil Procedure (PUC-SP) and in Business, Constitutional "
                   "and Real Estate Law (ESA OAB/SP). Master's candidate at PUC-SP.",
                   "He practices in contracts, strategic litigation, real estate due "
                   "diligence and asset acquisitions."],
        },
        # (chave, português, inglês)
        "areas": [
            ("area_empresarial", "Direito Empresarial", "Business Law"),
            ("area_contratual", "Direito Contratual", "Contract Law"),
            ("area_contencioso", "Contencioso Estratégico", "Strategic Litigation"),
            ("area_due_diligence", "Due Diligence Imobiliária", "Real Estate Due Diligence"),
            ("area_aquisicao", "Aquisição de Ativos", "Asset Acquisitions"),
        ],
        # Número da OAB exibido na seção Empresa (vazio = a linha some)
        "oab": "198.911",
    },
}


def telefone_br(e164: str) -> str:
    """+5511982072944 -> (11) 98207-2944"""
    d = e164.lstrip("+")[2:]
    return f"({d[:2]}) {d[2:-4]}-{d[-4:]}"
