# -*- coding: utf-8 -*-
"""Gera os QR Codes do cartão da Dra. Sirlei para impressão.

    python gerar_qrcode.py

Saída na subpasta qrcode/: um .svg e um .pdf (vetoriais, para a gráfica)
e um .png de 300 dpi (para uso rápido), em preto e em azul-marinho.

Por que vetorial: o arquivo não tem resolução fixa, então imprime nítido em
qualquer tamanho. PNG só serve se for grande o bastante para o tamanho final.

Regras de impressão já aplicadas aqui:
  - margem branca (quiet zone) de 4 módulos em volta, exigida pelo padrão;
  - correção de erro M, que tolera 15% do código danificado ou sujo;
  - cor escura sobre fundo claro, nunca o contrário.
"""

from __future__ import annotations

from pathlib import Path

import segno

from qr_robusto import qr_mais_legivel

PASTA = Path(__file__).resolve().parent / "qrcode"

# --------------------------------------------------------------------------
# Endereços. O de domínio próprio é o recomendado: o QR impresso continua
# valendo mesmo que um dia o site saia do GitHub (ver README).
# --------------------------------------------------------------------------
DESTINOS = {
    "cartao-sirlei-github": "https://sirlei-andrade-advogados.github.io/cartao/",
    "cartao-sirlei-dominio": "https://cartao.sirleiadv.com.br",
    "cartao-alessandro-github": "https://sirlei-andrade-advogados.github.io/cartao/alessandro/",
}

#: QR já impresso não muda de desenho. O da Dra. Sirlei está na arte do
#: cartão enviada à gráfica (impressao/gerar_cartao.py lê este arquivo).
MASCARA_FIXA = {"cartao-sirlei-github": 6}

#: QR já publicado ou impresso não é regerado. Os da Dra. Sirlei estão na
#: arte do cartão enviada à gráfica.
CONGELADOS = {"cartao-sirlei-github", "cartao-sirlei-dominio"}

CORES = {
    "preto": "#000000",
    "azul": "#002060",   # azul-marinho institucional
}

#: Lado do QR no cartão impresso. 2 cm é o mínimo confortável; 2,5 cm é folgado.
LADO_CM = 2.5
DPI = 300


def main() -> None:
    PASTA.mkdir(exist_ok=True)
    # 1 módulo = N pixels, calculado para o PNG sair no tamanho físico certo
    px_total = round(LADO_CM / 2.54 * DPI)

    lado_mm = LADO_CM * 10
    lado_pt = lado_mm * 72 / 25.4          # PDF trabalha em pontos (1/72 pol.)

    for nome, url in DESTINOS.items():
        if nome in CONGELADOS:
            continue                              # já impresso: não mexer
        qr = qr_mais_legivel(url, error="m")
        modulos = qr.symbol_size(border=4)[0]
        escala = max(1, round(px_total / modulos))

        for cor_nome, cor in CORES.items():
            base = PASTA / f"{nome}-{cor_nome}"
            comum = {"dark": cor, "light": "#ffffff", "border": 4}
            # vetoriais já no tamanho físico final: a gráfica posiciona e imprime,
            # sem precisar redimensionar nem adivinhar escala
            qr.save(base.with_suffix(".svg"), scale=lado_mm / modulos, unit="mm", **comum)
            qr.save(base.with_suffix(".pdf"), scale=lado_pt / modulos, **comum)
            qr.save(base.with_suffix(".png"), scale=escala, **comum)

        lado_px = modulos * escala
        print(
            f"{nome}\n"
            f"   {url}\n"
            f"   versão {qr.version}, {modulos}x{modulos} módulos com margem\n"
            f"   SVG e PDF: {lado_mm:.0f}x{lado_mm:.0f} mm\n"
            f"   PNG {lado_px}x{lado_px}px = {lado_px / DPI * 2.54:.1f} cm a {DPI} dpi\n"
        )

    print(f"arquivos em: {PASTA}")


if __name__ == "__main__":
    main()
