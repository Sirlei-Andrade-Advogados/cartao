# -*- coding: utf-8 -*-
"""Gera o cartão digital de cada advogado a partir do da Dra. Sirlei.

    python gerar_paginas.py

A página da raiz (index.html) é a matriz. Para cada pessoa de pessoas.py
com pasta própria, este script copia a matriz e troca só o que é dela:
nome, cargo, bio, áreas, contatos, foto e arquivos de contato.

Cada troca confere quantas vezes o trecho aparece na matriz. Se alguém
editar a matriz e um trecho mudar, o script para com o nome da troca que
falhou, em vez de gerar uma página pela metade.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from pessoas import PESSOAS, telefone_br

AQUI = Path(__file__).resolve().parent
MATRIZ = PESSOAS["sirlei"]
#: bios com menos caracteres que isto aparecem inteiras, sem "Ver mais"
BIO_CURTA = 300

#: Só nas páginas derivadas (a da Dra. Sirlei está congelada): esconde o
#: "Ver mais" quando a bio cabe inteira ou é marcada como curta.
AJUSTE_VER_MAIS = """

  // Bio que cabe inteira não precisa de "Ver mais": o botão some.
  function ajustarVerMais() {
    if ("semCorte" in bio.dataset) {                // bio curta: sempre inteira
      bio.classList.remove("clamped");
      toggle.style.display = "none";
      bio.style.marginBottom = "22px";            // o respiro que o botão dava
      return;
    }
    if (toggle.getAttribute("aria-expanded") === "true") return;  // leitor já abriu
    bio.classList.add("clamped");
    const cabe = bio.scrollHeight <= bio.clientHeight + 2;
    bio.classList.toggle("clamped", !cabe);
    toggle.style.display = cabe ? "none" : "";
    bio.style.marginBottom = cabe ? "22px" : "";
  }
  ajustarVerMais();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(ajustarVerMais);
  addEventListener("resize", ajustarVerMais);
  document.querySelectorAll(".lang button").forEach((b) =>
    b.addEventListener("click", ajustarVerMais));"""


class TrocaFalhou(SystemExit):
    pass


def troca(s: str, velho: str, novo: str, vezes: int = 1, nome: str = "") -> str:
    achou = s.count(velho)
    if achou != vezes:
        raise TrocaFalhou(f"[{nome or velho[:40]}] esperava {vezes}x, achou {achou}x")
    return s.replace(velho, novo)


def troca_re(s: str, padrao: str, novo: str, vezes: int = 1, nome: str = "") -> str:
    achou = len(re.findall(padrao, s, flags=re.S))
    if achou != vezes:
        raise TrocaFalhou(f"[{nome}] esperava {vezes}x, achou {achou}x")
    return re.sub(padrao, lambda _m: novo, s, flags=re.S)


def derivar(p: dict, slug: str) -> str:
    s = (AQUI / "index.html").read_text(encoding="utf-8")
    m = MATRIZ
    nome, cargo = p["completo"], p["cargo"]
    titulo = {l: f"{nome} — {cargo[l]} · Sirlei Andrade Advogados Associados" for l in ("pt", "en")}
    tel_m, tel_p = m["celular"].lstrip("+"), p["celular"].lstrip("+")

    # ---- cabeçalho e metadados -------------------------------------------
    s = troca(s, f'<title data-i18n="title">{m["completo"]} — {m["cargo"]["pt"]} · '
                 'Sirlei Andrade Advogados Associados</title>',
              f'<title data-i18n="title">{titulo["pt"]}</title>', nome="title")
    s = troca_re(s, r'<meta name="description" content="[^"]*">',
                 f'<meta name="description" content="Cartão digital de {nome}, '
                 f'{cargo["pt"].lower()} da Sirlei Andrade Advogados Associados'
                 + (f' (OAB/SP {p["oab"]})' if p.get("oab") else "") + '.">',
                 nome="meta description")
    s = troca(s, f'<meta property="og:title" content="{m["completo"]} — {m["cargo"]["pt"]}">',
              f'<meta property="og:title" content="{nome} — {cargo["pt"]}">', nome="og:title")
    # a página mora numa subpasta: a marca fica na raiz
    s = troca(s, 'href="logo.svg"', 'href="../logo.svg"', nome="favicon")
    s = troca(s, '<img class="logo" src="logo.svg"', '<img class="logo" src="../logo.svg"', nome="logo")

    # ---- herói ----------------------------------------------------------
    s = troca(s, f'<!-- Foto: arquivo "{m["foto"]}" nesta pasta -->',
              f'<!-- Foto: arquivo "{p["foto"]}" nesta pasta -->', nome="comentário foto")
    s = troca(s, f'<img class="photo" alt="{m["completo"]}" src="{m["foto"]}"',
              f'<img class="photo" alt="{nome}" src="{p["foto"]}"', nome="foto")
    s = troca(s, "%3ESA%3C/text", f'%3E{p.get("iniciais", "")}%3C/text', nome="iniciais")
    s = troca(s, f"<h1>{m['completo']}</h1>", f"<h1>{nome}</h1>", nome="h1")
    s = troca(s, f'<p class="role" data-i18n="role">{m["cargo"]["pt"]}</p>',
              f'<p class="role" data-i18n="role">{cargo["pt"]}</p>', nome="cargo")

    paras = {l: "\n".join(f"<p>{html.escape(t, quote=False)}</p>" for t in p["bio"][l])
             for l in ("pt", "en")}
    # bio de poucas linhas aparece inteira, sem "Ver mais"
    curta = max(sum(len(t) for t in p["bio"][l]) for l in ("pt", "en")) < BIO_CURTA
    abre = ('<div class="bio" id="bio" data-i18n-html="bio" data-sem-corte>' if curta
            else '<div class="bio clamped" id="bio" data-i18n-html="bio">')
    s = troca_re(s, r'(<div class="bio clamped" id="bio" data-i18n-html="bio">).*?(\s*</div>)',
                 abre + "\n        " + paras["pt"].replace("\n", "\n        ") + "\n      </div>",
                 nome="bio html")

    # ---- contato -------------------------------------------------------
    slug_m = "sirlei"
    s = troca(s, f"O href troca para {slug_m}-en.vcf", f"O href troca para {slug}-en.vcf", nome="comentário vcf")
    s = troca(s, f'href="{slug_m}.vcf"', f'href="{slug}.vcf"', nome="href vcf")
    s = troca(s, tel_m, tel_p, vezes=3, nome="celular (wa.me x2, tel x1)")
    s = troca(s, telefone_br(m["celular"]), telefone_br(p["celular"]), vezes=2, nome="celular exibido")
    s = troca(s, m["email"], p["email"], vezes=3, nome="e-mail")

    # ---- áreas ---------------------------------------------------------
    chips = "\n".join(f'        <span class="chip" data-i18n="{k}">{pt}</span>'
                      for k, pt, _ in p["areas"])
    s = troca_re(s, r'<div class="chips">.*?</div>',
                 f'<div class="chips">\n{chips}\n      </div>', nome="chips")

    # ---- OAB (a da matriz é da Dra. Sirlei) ----------------------------
    linha_oab = (r'      <div class="row">\s*<svg class="ico"[^>]*>'
                 r'<path d="M12 3 4 6v6c0 5[^"]*"/><path d="m9 12 2 2 4-4"/></svg>\s*'
                 r'<div class="body">OAB/SP nº 225\.531<small>Sirlei de Souza Andrade</small></div>\s*</div>\n')
    if p.get("oab"):
        s = troca(s, "OAB/SP nº 225.531<small>Sirlei de Souza Andrade</small>",
                  f"OAB/SP nº {p['oab']}<small>{nome}</small>", nome="oab")
    else:
        s = troca_re(s, linha_oab, "", nome="linha OAB")

    # ---- textos em JS (PT e EN) ----------------------------------------
    for l, en_titulo in (("pt", titulo["pt"]), ("en", titulo["en"])):
        s = troca(s, f'      title: "{m["completo"]} — {m["cargo"][l]} · Sirlei Andrade Advogados Associados",',
                  f'      title: "{en_titulo}",', nome=f"i18n title {l}")
        s = troca(s, f'      role: "{m["cargo"][l]}",', f'      role: "{cargo[l]}",', nome=f"i18n role {l}")

    bios = re.findall(r"      bio: `.*?`,\n", s, flags=re.S)
    if len(bios) != 2:
        raise TrocaFalhou(f"[i18n bio] esperava 2 blocos, achou {len(bios)}")
    s = s.replace(bios[0], f"      bio: `{paras['pt']}`,\n", 1)
    s = s.replace(bios[1], f"      bio: `{paras['en']}`,\n", 1)

    areas_pt = "      " + " ".join(f'{k}: "{pt}",' for k, pt, _ in p["areas"]) + "\n"
    areas_en = "      " + " ".join(f'{k}: "{en}",' for k, _, en in p["areas"]) + "\n"
    s = troca_re(s, r'      area_civil: "Direito Civil",.*?area_trabalhista: "Direito Trabalhista",\n',
                 areas_pt, nome="i18n áreas pt")
    s = troca_re(s, r'      area_civil: "Civil Law",.*?area_trabalhista: "Labor Law",\n',
                 areas_en, nome="i18n áreas en")

    s = troca(s, f'vcard: "{slug_m}.vcf"', f'vcard: "{slug}.vcf"', nome="i18n vcard pt")
    s = troca(s, f'vcard: "{slug_m}-en.vcf"', f'vcard: "{slug}-en.vcf"', nome="i18n vcard en")
    s = troca(s, f"arquivos {slug_m}.vcf / {slug_m}-en.vcf", f"arquivos {slug}.vcf / {slug}-en.vcf",
              nome="comentário js vcf")
    s = troca(s, f'"{m["completo"]}.vcf"', f'"{nome}.vcf"', nome="nome do arquivo no Android")

    fim_ver_mais = """    toggle.querySelector("span").textContent = open ? I18N[LANG].less : I18N[LANG].more;
  });"""
    s = troca(s, fim_ver_mais, fim_ver_mais + AJUSTE_VER_MAIS, nome="ajuste do Ver mais")

    # nada da Dra. Sirlei pode ter sobrado, fora a marca do escritório
    sobra = [t for t in (m["email"], tel_m, "Sócia-fundadora", "Founding Partner",
                         "sirlei.jpg", "sirlei.vcf", "225.531") if t in s]
    if sobra:
        raise TrocaFalhou(f"sobrou dado da matriz: {sobra}")
    return s


def main() -> None:
    for slug, p in PESSOAS.items():
        if not p["pasta"]:
            continue                         # a matriz não se gera
        destino = AQUI / p["pasta"] / "index.html"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(derivar(p, slug), encoding="utf-8")
        print(f"{slug:12} -> {destino.relative_to(AQUI)}")


if __name__ == "__main__":
    main()
