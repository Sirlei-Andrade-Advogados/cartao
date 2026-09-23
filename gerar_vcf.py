# -*- coding: utf-8 -*-
"""Gera os cartões de contato (.vcf) de cada advogado do site.

Rodar depois de alterar telefone, e-mail, endereço ou a foto:

    python gerar_vcf.py

Os dados vêm de pessoas.py. Saída, na pasta de cada um: <slug>.vcf
(português) e <slug>-en.vcf (inglês). O botão "Adicionar aos contatos"
da página aponta direto para esses arquivos, por isso eles precisam ser
publicados junto com ela.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path

PASTA = Path(__file__).resolve().parent

from pessoas import ESCRITORIO, PESSOAS

FOTO_PX = 240                 # lado da foto embutida (quanto maior, maior o arquivo)


def escapar(valor: str) -> str:
    """Escapa os caracteres que o vCard 3.0 trata como separadores."""
    return (
        str(valor)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def dobrar(linha: str, limite: int = 74) -> list[str]:
    """Quebra linhas longas no formato do RFC 2426 (continuação começa com espaço)."""
    if len(linha) <= limite:
        return [linha]
    partes = [linha[:limite]]
    resto = linha[limite:]
    while resto:
        partes.append(" " + resto[: limite - 1])
        resto = resto[limite - 1 :]
    return partes


def foto_base64(foto: Path) -> str | None:
    """Reduz a foto e devolve em base64; devolve None se não houver foto/Pillow."""
    if not foto.exists():
        return None
    try:
        from PIL import Image
    except ImportError:
        return None
    img = Image.open(foto).convert("RGB")
    lado = min(img.size)
    esq = (img.width - lado) // 2
    topo = (img.height - lado) // 2
    img = img.crop((esq, topo, esq + lado, topo + lado))
    img = img.resize((FOTO_PX, FOTO_PX), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=78, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def montar(c: dict, idioma: str, foto: str | None) -> str:
    a = ESCRITORIO
    linhas = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escapar(c['sobrenome'])};{escapar(c['nome'])};;;",
        f"FN:{escapar(c['completo'])}",
        f"ORG:{escapar(a['empresa'])}",
        f"TITLE:{escapar(c['cargo'][idioma])}",
        f"TEL;TYPE=CELL,VOICE:{c['celular']}",
        f"EMAIL;TYPE=INTERNET,WORK:{c['email']}",
        f"URL:{a['site']}",
        "ADR;TYPE=WORK:;;"
        f"{escapar(a['rua'])};{escapar(a['cidade'])};{escapar(a['uf'])};"
        f"{escapar(a['cep'])};{escapar(a['pais'])}",
    ]
    if foto:
        linhas.append(f"PHOTO;ENCODING=b;TYPE=JPEG:{foto}")
    linhas.append("END:VCARD")

    saida: list[str] = []
    for linha in linhas:
        saida.extend(dobrar(linha))
    return "\r\n".join(saida) + "\r\n"


def main() -> None:
    for slug, c in PESSOAS.items():
        if c.get("congelado"):
            continue                              # publicado: não mexer
        pasta = PASTA / c["pasta"]
        foto = foto_base64(pasta / c["foto"])
        if foto is None:
            print(f"aviso: {slug} sem foto no contato (arquivo ausente ou Pillow não instalado)")
        for idioma, arquivo in (("pt", f"{slug}.vcf"), ("en", f"{slug}-en.vcf")):
            destino = pasta / arquivo
            destino.write_text(montar(c, idioma, foto), encoding="utf-8", newline="")
            print(f"{destino.relative_to(PASTA)}: {destino.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
