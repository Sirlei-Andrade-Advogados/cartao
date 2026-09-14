# Cartão digital — Sirlei Andrade

Página estática (um único HTML) com o cartão de visita da Dra. Sirlei Andrade,
sócia-fundadora da Sirlei Andrade Advogados Associados.

Funciona em português e inglês na mesma página, com botão para salvar o
contato no celular e QR Code para compartilhar.

## Arquivos

| Arquivo | O que é |
|---|---|
| `index.html` | A página inteira: estrutura, estilo, textos PT/EN e scripts |
| `logo.svg` | Marca do escritório (barra superior e ícone da aba) |
| `sirlei.jpg` | Foto do cartão, recorte quadrado 800×800 |
| `sirlei.vcf` / `sirlei-en.vcf` | Cartão de contato que o botão entrega, por idioma |
| `gerar_vcf.py` | Gera os dois `.vcf` a partir dos dados e da foto |

## Como alterar

**Textos em português:** edite direto no `index.html`.
**Textos em inglês:** no fim do arquivo, no bloco `I18N.en`, uma chave por texto.
**Cores e fonte:** no topo do `<style>`, no bloco `:root`.

**Telefone, e-mail ou endereço:** altere em dois lugares, porque o contato
salvo no celular vem de um arquivo separado da página:

1. no `index.html`, nas seções Contatos e Empresa;
2. em `gerar_vcf.py`, no dicionário `CONTATO`, e rode em seguida:

```bash
python gerar_vcf.py
```

**Foto:** substitua `sirlei.jpg` por um recorte quadrado e rode `gerar_vcf.py`
de novo, para a foto embutida no contato acompanhar.

## Publicação

É um site estático, sem build. Basta servir a pasta.

O servidor precisa entregar os arquivos `.vcf` como `text/vcard`. É o que faz
o botão "Adicionar aos contatos" abrir direto a tela de novo contato no
iPhone, em vez de virar um download solto.

Para testar localmente:

```bash
python -m http.server 5500
```
