# -*- coding: utf-8 -*-
"""Gera a tela "Meu contato" de cada advogado: um QR grande que salva o contato.

    python gerar_contato.py

Para que serve: o advogado abre essa tela no celular e mostra para a pessoa. A
pessoa aponta a câmera e o telefone já abre a ficha pronta para salvar.
Não precisa de internet do lado de quem escaneia, porque o contato inteiro
vai dentro do QR, não um endereço de site.

Os dados vêm de pessoas.py. Saída, em <pasta da pessoa>/contato/:
  index.html                 a tela (dá para adicionar à tela de início do iPhone)
  sw.js                      cache para a tela abrir sem sinal
  icone.png                  ícone do atalho na tela de início
  <Nome> QR Contato.png      imagem para guardar nas Fotos
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import segno

from qr_robusto import qr_mais_legivel

AQUI = Path(__file__).resolve().parent
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

CORES = {"fundo": "#030714", "ouro": "#c2ad83", "marfim": "#f4efe6",
         "apagado": "#8792a8"}

from pessoas import ESCRITORIO, PESSOAS

TEXTOS = {
    "pt": {"chamada": "ESCANEIE PARA SALVAR MEU CONTATO",
           "dica": "Aponte a câmera do celular para o código",
           "cartao": "Ver cartão completo"},
    "en": {"chamada": "SCAN TO SAVE MY CONTACT",
           "dica": "Point your phone camera at the code",
           "cartao": "See full card"},
}


def textos(p: dict, idioma: str) -> dict:
    return {**TEXTOS[idioma], "cargo": p["cargo"][idioma]}


def vcard(p: dict, idioma: str) -> str:
    c = {**ESCRITORIO, **p}
    esc = lambda s: str(s).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
    return "\r\n".join([
        "BEGIN:VCARD", "VERSION:3.0",
        f"N:{esc(c['sobrenome'])};{esc(c['nome'])};;;",
        f"FN:{esc(c['completo'])}",
        f"ORG:{esc(c['empresa'])}",
        f"TITLE:{esc(c['cargo'][idioma])}",
        f"TEL;TYPE=CELL:{c['celular']}",
        f"EMAIL:{c['email']}",
        f"URL:{c['site']}",
        f"ADR;TYPE=WORK:;;{esc(c['rua'])};{esc(c['cidade'])};{esc(c['uf'])};"
        f"{esc(c['cep'])};{esc(c['pais'])}",
        "END:VCARD",
    ]) + "\r\n"


def qr_svg(p: dict, idioma: str) -> tuple[str, int]:
    """QR do contato como SVG inline, sem moldura própria."""
    qr = qr_mais_legivel(vcard(p, idioma), error="m")
    import io
    buf = io.BytesIO()          # o escritor de SVG do segno trabalha em bytes
    qr.save(buf, kind="svg", scale=1, border=2, dark="#000000", light=None,
            xmldecl=False, svgns=True, omitsize=True, svgclass=None, lineclass=None)
    svg = buf.getvalue().decode("utf-8")
    lado = qr.symbol_size(border=2)[0]
    # deixa o SVG escalável: quem manda no tamanho é o CSS
    svg = re.sub(r"<svg[^>]*>", f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'viewBox="0 0 {lado} {lado}" shape-rendering="crispEdges" '
                 f'preserveAspectRatio="xMidYMid meet">', svg, count=1)
    return svg, qr.version


LOGO = """<svg viewBox="167 71 301 308" aria-hidden="true"><defs>
<linearGradient id="lo" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#6f5223"/><stop offset="38%" stop-color="#c8a86a"/><stop offset="62%" stop-color="#8a6d3b"/><stop offset="100%" stop-color="#5f4519"/></linearGradient>
<linearGradient id="lp" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#6f767c"/><stop offset="40%" stop-color="#cfd4d8"/><stop offset="65%" stop-color="#8d949a"/><stop offset="100%" stop-color="#666d73"/></linearGradient>
<clipPath id="ld" clipPathUnits="userSpaceOnUse"><rect x="330" y="0" width="300" height="500"/></clipPath>
<clipPath id="le" clipPathUnits="userSpaceOnUse"><rect x="0" y="0" width="330" height="500"/></clipPath>
<mask id="lfp" maskUnits="userSpaceOnUse" x="0" y="0" width="700" height="500"><rect width="700" height="500" fill="#fff"/><polygon points="317,86 453,244 317,308 182,244" fill="none" stroke="#000" stroke-width="27" clip-path="url(#le)"/></mask>
<mask id="lfo" maskUnits="userSpaceOnUse" x="0" y="0" width="700" height="500"><rect width="700" height="500" fill="#fff"/><polygon points="317,142 453,300 317,364 182,300" fill="none" stroke="#000" stroke-width="27" clip-path="url(#ld)"/></mask>
</defs>
<polygon points="317,142 453,300 317,364 182,300" fill="none" stroke="url(#lp)" stroke-width="15" mask="url(#lfp)"/>
<polygon points="317,86 453,244 317,308 182,244" fill="none" stroke="url(#lo)" stroke-width="15" mask="url(#lfo)"/></svg>"""


def pagina(p: dict, qr_pt: str, qr_en: str) -> str:
    t = textos(p, "pt")
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Contato — {p['completo']}</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="{CORES['fundo']}">
<!-- vira atalho de tela cheia quando adicionada à tela de início do iPhone -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Meu contato">
<link rel="apple-touch-icon" href="icone.png">
<link rel="icon" href="icone.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400&family=Inter:wght@300;400&display=swap" rel="stylesheet">
<style>
  :root{{
    --fundo:{CORES['fundo']};
    --ouro:{CORES['ouro']};
    --marfim:{CORES['marfim']};
    --apagado:{CORES['apagado']};
  }}
  *{{box-sizing:border-box}}
  html,body{{height:100%}}
  body{{
    margin:0;background:var(--fundo);color:var(--marfim);
    font-family:"Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
    -webkit-font-smoothing:antialiased;
    /* não deixa a tela rolar nem dar zoom acidental enquanto ela mostra */
    overscroll-behavior:none;-webkit-text-size-adjust:100%;
  }}
  .tela{{
    min-height:100%;display:flex;flex-direction:column;align-items:center;
    justify-content:center;gap:clamp(14px,3.2vh,26px);
    padding:calc(env(safe-area-inset-top) + 20px) 20px
            calc(env(safe-area-inset-bottom) + 20px);
    text-align:center;
  }}
  .chamada{{
    margin:0;font-size:clamp(10px,2.9vw,13px);font-weight:400;
    letter-spacing:.22em;color:var(--ouro);text-transform:uppercase;
  }}
  /* a placa branca é o que a câmera precisa enxergar: fica sempre clara,
     independente do tema do telefone */
  .placa{{
    background:#fff;border-radius:14px;padding:clamp(12px,3.2vw,20px);
    width:min(78vw,52vh,420px);aspect-ratio:1;
    box-shadow:0 10px 40px rgba(0,0,0,.5);
    display:grid;place-items:center;
  }}
  .placa svg{{width:100%;height:100%;display:block}}
  .placa svg path{{fill:#000}}
  [hidden]{{display:none!important}}
  .nome{{
    margin:0;font-family:"Cormorant Garamond",Georgia,serif;
    font-size:clamp(28px,8vw,40px);font-weight:400;line-height:1.05;
  }}
  .cargo{{margin:4px 0 0;font-size:clamp(11px,3.2vw,14px);color:var(--ouro);letter-spacing:.06em}}
  .dica{{margin:0;font-size:clamp(11px,3.1vw,13px);color:var(--apagado);font-weight:300}}
  .rodape{{
    display:flex;align-items:center;gap:14px;margin-top:2px;
    font-size:12px;color:var(--apagado);
  }}
  .rodape a,.rodape button{{
    font:inherit;color:var(--apagado);background:none;border:0;padding:6px 10px;
    border-radius:999px;cursor:pointer;text-decoration:none;
    border:1px solid rgba(135,146,168,.35);
  }}
  .rodape button[aria-pressed="true"]{{background:var(--ouro);color:#1a1408;border-color:var(--ouro)}}
  .marca{{width:34px;height:34px;opacity:.9}}
  .marca svg{{width:100%;height:100%;display:block}}
  :focus-visible{{outline:2px solid var(--ouro);outline-offset:3px}}
  @media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
</style>
</head>
<body>
<main class="tela">
  <div class="marca">{LOGO}</div>
  <p class="chamada" id="chamada">{t['chamada']}</p>

  <div class="placa">
    <div id="qr-pt">{qr_pt}</div>
    <div id="qr-en" hidden>{qr_en}</div>
  </div>

  <div>
    <h1 class="nome">{p['completo']}</h1>
    <p class="cargo" id="cargo">{t['cargo']}</p>
  </div>
  <p class="dica" id="dica">{t['dica']}</p>

  <nav class="rodape">
    <button type="button" id="b-pt" aria-pressed="true">PT</button>
    <button type="button" id="b-en" aria-pressed="false">EN</button>
    <a href="../" id="link-cartao">{t['cartao']}</a>
  </nav>
</main>

<script>
  const T = {{
    pt: {textos(p, 'pt')!r},
    en: {textos(p, 'en')!r}
  }};
  function idioma(l) {{
    const t = T[l] || T.pt;
    document.documentElement.lang = l === "pt" ? "pt-BR" : "en";
    document.getElementById("chamada").textContent = t.chamada;
    document.getElementById("cargo").textContent = t.cargo;
    document.getElementById("dica").textContent = t.dica;
    document.getElementById("link-cartao").textContent = t.cartao;
    document.getElementById("qr-pt").hidden = l !== "pt";
    document.getElementById("qr-en").hidden = l !== "en";
    document.getElementById("b-pt").setAttribute("aria-pressed", String(l === "pt"));
    document.getElementById("b-en").setAttribute("aria-pressed", String(l === "en"));
    try {{ localStorage.setItem("contato-lang", l); }} catch (e) {{}}
  }}
  document.getElementById("b-pt").addEventListener("click", () => idioma("pt"));
  document.getElementById("b-en").addEventListener("click", () => idioma("en"));
  try {{
    const s = localStorage.getItem("contato-lang");
    if (s && s !== "pt") idioma(s);
  }} catch (e) {{}}

  // guarda a tela para ela abrir mesmo sem sinal
  if ("serviceWorker" in navigator) {{
    addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {{}}));
  }}
</script>
</body>
</html>
"""


SW = """// Guarda a tela de contato para abrir sem internet.
// O nome "contato-v1" é o mesmo da tela da Dra. Sirlei, de propósito: o
// service worker dela (publicado, não muda) apaga no activate todo cache com
// outro nome. As entradas não colidem porque cada tela guarda as próprias
// URLs. Por isso este aqui também nunca apaga cache nenhum.
const CACHE = "contato-v1";
const ARQUIVOS = ["./", "./index.html", "./icone.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ARQUIVOS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(self.clients.claim());
});

// cache primeiro: abre instantâneo e funciona offline; atualiza por trás
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then((achou) => {
      const rede = fetch(e.request)
        .then((r) => {
          if (r && r.ok) caches.open(CACHE).then((c) => c.put(e.request, r.clone()));
          return r;
        })
        .catch(() => achou);
      return achou || rede;
    })
  );
});
"""


def png_por_chrome(html: str, largura: int, altura: int, destino: Path) -> bool:
    tmp = destino.parent / "_tmp.html"
    tmp.write_text(html, encoding="utf-8")
    subprocess.run(
        [str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
         f"--window-size={largura},{altura}", "--default-background-color=00000000",
         f"--screenshot={destino}", "--virtual-time-budget=6000", tmp.as_uri()],
        capture_output=True, timeout=120)
    tmp.unlink(missing_ok=True)
    return destino.exists()


def icone() -> str:
    return f"""<!DOCTYPE html><meta charset="utf-8"><style>
html,body{{margin:0;width:180px;height:180px;background:{CORES['fundo']}}}
div{{width:132px;height:132px;margin:24px}} svg{{width:100%;height:100%;display:block}}
</style><div>{LOGO}</div>"""


def imagem_fotos(p: dict, qr: str) -> str:
    return f"""<!DOCTYPE html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400&family=Inter:wght@400&display=swap" rel="stylesheet">
<style>
html,body{{margin:0;width:1200px;height:1500px;background:{CORES['fundo']};
  font-family:Inter,Arial,sans-serif;color:{CORES['marfim']}}}
.c{{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px}}
.t{{font-size:26px;letter-spacing:.22em;color:{CORES['ouro']};text-transform:uppercase;margin:0}}
.p{{background:#fff;border-radius:28px;padding:38px;width:760px;height:760px;display:grid;place-items:center}}
.p svg{{width:100%;height:100%}} .p svg path{{fill:#000}}
h1{{font-family:"Cormorant Garamond",Georgia,serif;font-weight:400;font-size:82px;margin:0}}
.g{{margin:10px 0 0;font-size:30px;color:{CORES['ouro']}}}
</style>
<div class="c">
  <p class="t">Escaneie para salvar meu contato</p>
  <div class="p">{qr}</div>
  <div style="text-align:center"><h1>{p['completo']}</h1><p class="g">{p['cargo']['pt']}</p></div>
</div>"""


def main() -> None:
    for slug, p in PESSOAS.items():
        if p.get("congelado"):
            continue                              # publicado: não mexer
        dest = AQUI / p["pasta"] / "contato"
        dest.mkdir(parents=True, exist_ok=True)
        qr_pt, v = qr_svg(p, "pt")
        qr_en, _ = qr_svg(p, "en")
        (dest / "index.html").write_text(pagina(p, qr_pt, qr_en), encoding="utf-8")
        (dest / "sw.js").write_text(SW, encoding="utf-8")
        ok_i = png_por_chrome(icone(), 180, 180, dest / "icone.png")
        ok_f = png_por_chrome(imagem_fotos(p, qr_pt), 1200, 1500,
                              dest / f"{p['completo']} QR Contato.png")
        print(f"{slug:11} vCard {len(vcard(p, 'pt').encode())} bytes · QR versão {v} · "
              f"ícone {'ok' if ok_i else 'FALHOU'} · imagem {'ok' if ok_f else 'FALHOU'}"
              f"  -> {dest.relative_to(AQUI)}")


if __name__ == "__main__":
    main()
