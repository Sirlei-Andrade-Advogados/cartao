# -*- coding: utf-8 -*-
"""Gera os cartões de contato (.vcf) do cartão digital da Dra. Sirlei.

Rodar depois de alterar telefone, e-mail, endereço ou a foto:

    python gerar_vcf.py

Saída: sirlei.vcf (português) e sirlei-en.vcf (inglês), na mesma pasta.
O botão "Adicionar aos contatos" do index.html aponta direto para esses
arquivos — por isso eles precisam ser publicados junto com a página.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path

PASTA = Path(__file__).resolve().parent

# --------------------------------------------------------------------------
# Dados do contato. Só o celular da Dra. Sirlei entra no cartão.
# --------------------------------------------------------------------------
CONTATO = {
    "nome": "Sirlei",
    "sobrenome": "Andrade",
    "nome_completo": "Sirlei Andrade",
    "empresa": "Sirlei Andrade Advogados Associados",
    "celular": "+5511947234782",
    "email": "sirlei@sirleiadv.com.br",
    "site": "https://www.sirleiadv.com.br",
    "endereco": {
        "rua": "Rua Barão de Itaim, 83-A - Granja Julieta",
        "cidade": "São Paulo",
        "uf": "SP",
        "cep": "04720-030",
        "pais": "Brasil",
    },
}

CARGO = {"pt": "Sócia-fundadora", "en": "Founding Partner"}

FOTO = PASTA / "sirlei.jpg"   # embutida no contato; apague a linha PHOTO se não quiser
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


def foto_base64() -> str | None:
    """Reduz a foto e devolve em base64; devolve None se não houver foto/Pillow."""
    if not FOTO.exists():
        return None
    try:
        from PIL import Image
    except ImportError:
        return None
    img = Image.open(FOTO).convert("RGB")
    lado = min(img.size)
    esq = (img.width - lado) // 2
    topo = (img.height - lado) // 2
    img = img.crop((esq, topo, esq + lado, topo + lado))
    img = img.resize((FOTO_PX, FOTO_PX), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=78, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def montar(idioma: str, foto: str | None) -> str:
    c = CONTATO
    a = c["endereco"]
    linhas = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escapar(c['sobrenome'])};{escapar(c['nome'])};;;",
        f"FN:{escapar(c['nome_completo'])}",
        f"ORG:{escapar(c['empresa'])}",
        f"TITLE:{escapar(CARGO[idioma])}",
        f"TEL;TYPE=CELL,VOICE:{c['celular']}",
        f"EMAIL;TYPE=INTERNET,WORK:{c['email']}",
        f"URL:{c['site']}",
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
    foto = foto_base64()
    if foto is None:
        print("aviso: foto não embutida (arquivo ausente ou Pillow não instalado)")
    for idioma, arquivo in (("pt", "sirlei.vcf"), ("en", "sirlei-en.vcf")):
        destino = PASTA / arquivo
        destino.write_text(montar(idioma, foto), encoding="utf-8", newline="")
        print(f"{arquivo}: {destino.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
