# -*- coding: utf-8 -*-
"""Escolhe, entre as 8 máscaras possíveis, o QR que mais leitores conseguem ler.

O padrão QR permite desenhar o mesmo conteúdo com 8 "máscaras" diferentes.
A biblioteca escolhe uma por uma regra de pontuação do padrão, mas alguns
leitores tropeçam em certas máscaras: o QR do Alessandro, com a máscara
automática, não era lido por um dos dois detectores testados.

A nota de cada máscara cobre as duas pontas onde leitores tropeçam: imagem
grande e nítida (8 e 5 pixels por módulo) e imagem pequena, quase no limite
(3 a 1,6 pixel por módulo), com e sem desfoque, lida por 2 detectores.
Ganha quem acerta mais; em empate fica a automática.

QR que já foi publicado ou impresso não deve mudar de desenho: passe a
máscara dele em `fixa` e a escolha é ignorada.
"""

from __future__ import annotations

import io

import segno

try:
    import cv2
    import numpy as np
    _DETECTORES = (cv2.QRCodeDetector(), cv2.QRCodeDetectorAruco())
except Exception:                                   # sem OpenCV: usa a automática
    _DETECTORES = ()

#: pixels por módulo testados: da leitura folgada até perto do limite
_PX_POR_MODULO = (8.0, 5.0, 3.0, 2.6, 2.3, 2.0, 1.8, 1.6)


def _nota(qr: segno.QRCode, conteudo: str) -> int:
    base = 10
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=base, border=4)
    img = cv2.imdecode(np.frombuffer(buf.getvalue(), np.uint8), 0)
    acertos = 0
    for ppm in _PX_POR_MODULO:
        g = cv2.resize(img, None, fx=ppm / base, fy=ppm / base, interpolation=cv2.INTER_AREA)
        for borra in (False, True):
            gg = cv2.GaussianBlur(g, (3, 3), 0.6) if borra else g
            for d in _DETECTORES:
                try:
                    acertos += d.detectAndDecode(gg)[0] == conteudo
                except Exception:
                    pass
    return acertos


def qr_mais_legivel(conteudo: str, error: str = "m", fixa: int | None = None) -> segno.QRCode:
    if fixa is not None:                          # desenho travado de propósito
        return segno.make(conteudo, error=error, mask=fixa)
    auto = segno.make(conteudo, error=error)
    if not _DETECTORES:
        return auto
    nota_auto = _nota(auto, conteudo)
    melhor, nota_melhor = auto, nota_auto
    for m in range(8):
        if m == auto.mask:
            continue
        q = segno.make(conteudo, error=error, mask=m)
        n = _nota(q, conteudo)
        if n > nota_melhor:                       # empate não troca
            melhor, nota_melhor = q, n
    return melhor


if __name__ == "__main__":                        # relatório: python qr_robusto.py
    from pessoas import PESSOAS, URL_BASE
    import gerar_contato as gc
    alvos = {f"site {s}": URL_BASE + (p["pasta"] + "/" if p["pasta"] else "")
             for s, p in PESSOAS.items()}
    alvos.update({f"contato {s}": gc.vcard(p, "pt") for s, p in PESSOAS.items()})
    total = len(_PX_POR_MODULO) * 2 * len(_DETECTORES)
    for rotulo, conteudo in alvos.items():
        auto = segno.make(conteudo, error="m")
        notas = {m: _nota(segno.make(conteudo, error="m", mask=m), conteudo) for m in range(8)}
        esc = qr_mais_legivel(conteudo)
        linha = " ".join(f"{m}:{n:2}" for m, n in notas.items())
        print(f"{rotulo:20} auto={auto.mask} escolhida={esc.mask}  (de {total})  {linha}")
