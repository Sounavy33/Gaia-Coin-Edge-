#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# POC CLX - reducao de bytes com reconstrucao identica, medida e repetivel.
# Projeto Gaia Coin / Sounavy. Prova de conceito; ver docs/ESTUDO_PRELIMINAR_CLX.md.
# Apenas bibliotecas padrao do Python. Corpus totalmente sintetico.
import random, zlib, hashlib, hmac, lzma
random.seed(33)

# ---------- 1. corpus ficticio de protocolo (sem dados reais) ----------
QUEIXA = ["paciente relata dor temporal","paciente relata dor muscular","paciente relata estalido",
          "paciente relata sono entrecortado","paciente relata cansaco ao acordar","paciente nega dor"]
ACHADO = ["com bruxismo noturno","com desgaste incisal compativel","com abertura bucal limitada",
          "com sensibilidade muscular presente","com palpacao dolorida","com estalido na abertura"]
CONDUTA = ["conduta placa superior","conduta placa inferior","conduta orientar higiene do sono",
           "conduta reavaliar","conduta fisioterapia","conduta manter observacao"]
RETORNO = ["retorno em quinze dias","retorno em trinta dias","retorno em sessenta dias","retorno se piorar"]
def frase():
    return " ".join([random.choice(QUEIXA),random.choice(ACHADO),random.choice(CONDUTA),random.choice(RETORNO)])
todas = set()
while len(todas) < 700: todas.add(frase())
todas = sorted(todas); random.shuffle(todas)
treino, teste = todas[:400], todas[400:]
assert not set(treino) & set(teste)

# ---------- 2. dicionario compartilhado, construído no treino ----------
from collections import Counter
cont = Counter(w for f in treino for w in f.split())
DIC = [w for w,_ in cont.most_common(250)]  # ids 1..250; 0 = escape
ID = {w:i+1 for i,w in enumerate(DIC)}

def codificar(txt):
    out = bytearray()
    for w in txt.split(" "):
        if w in ID:
            out.append(ID[w])
        else:
            b = w.encode("utf-8")
            if len(b) > 255:
                raise ValueError("palavra desconhecida excede o limite de 255 bytes")
            out += bytes([0, len(b)]) + b
    return bytes(out)

def decodificar(bs):
    i, ws = 0, []
    while i < len(bs):
        token = bs[i]
        if token == 0:
            if i + 1 >= len(bs): raise ValueError("escape truncado")
            n = bs[i+1]
            if i + 2 + n > len(bs): raise ValueError("escape incompleto")
            ws.append(bs[i+2:i+2+n].decode("utf-8")); i += 2+n
        else:
            if token > len(DIC): raise ValueError("id fora do dicionario")
            ws.append(DIC[token-1]); i += 1
    return " ".join(ws)

ZD = " ".join(DIC).encode("utf-8")
def zlib_dic(b):
    c = zlib.compressobj(9, zlib.DEFLATED, 15, 9, zlib.Z_DEFAULT_STRATEGY, zdict=ZD)
    return c.compress(b) + c.flush()

def medir(nome, textos):
    o = z = zd = x = c = ok = 0
    for t in textos:
        b = t.encode("utf-8"); enc = codificar(t); dec = decodificar(enc)
        ok += (dec == t and hashlib.sha256(dec.encode("utf-8")).digest() == hashlib.sha256(b).digest())
        o += len(b); c += len(enc)
        z += len(zlib.compress(b, 9)); zd += len(zlib_dic(b)); x += len(lzma.compress(b))
    n = len(textos)
    print(f"\n== {nome} ({n} mensagens, cada uma comprimida sozinha) ==")
    print(f"original      : {o:6d} B")
    print(f"zlib nivel 9  : {z:6d} B  ({100*(1-z/o):5.1f}% menor)")
    print(f"zlib+dicionario: {zd:5d} B  ({100*(1-zd/o):5.1f}% menor)")
    print(f"lzma          : {x:6d} B  ({100*(1-x/o):5.1f}% menor)")
    print(f"CLX dicionario: {c:6d} B  ({100*(1-c/o):5.1f}% menor)")
    print(f"reconstrucao identica (SHA-256): {ok}/{n}")
    return o, c, ok, n

# ---------- 3. teste do protocolo: frases completas ausentes do treino ----------
o1, c1, ok1, n1 = medir("TESTE 1: protocolo sintetico, frases nao vistas no treino", teste)

# ---------- 4. texto livre fora do dominio: exemplos ilustrativos ----------
livre = ["o governo anunciou hoje novas medidas para conter a inflacao no segundo semestre",
 "a selecao venceu o jogo de ontem por dois a um com gol no final da partida",
 "pesquisadores publicaram um estudo sobre o clima e o aumento das chuvas no sul do pais",
 "a empresa lancou um aplicativo novo para facilitar o pagamento de contas pelo celular",
 "o festival de musica reuniu milhares de pessoas no parque durante todo o fim de semana"]
o2, c2, ok2, n2 = medir("TESTE 2: texto livre ilustrativo, fora do dominio", livre)

# ---------- 5. teste didatico de integridade/autenticacao HMAC ----------
chave = b"chave-compartilhada-ficticia"
msg = next(t for t in teste if "dor temporal" in t)
tag = hmac.new(chave, msg.encode("utf-8"), hashlib.sha256).digest()[:4]
alterada = msg.replace("dor temporal", "febre alta")
assert alterada != msg
ok_o = hmac.compare_digest(hmac.new(chave, msg.encode("utf-8"), hashlib.sha256).digest()[:4], tag)
ok_a = hmac.compare_digest(hmac.new(chave, alterada.encode("utf-8"), hashlib.sha256).digest()[:4], tag)
print(f"\n== TESTE 3: adulteracao ==\ntexto original aceito: {ok_o} | texto alterado aceito: {ok_a}")
print("(tag didatica de 4 bytes; nao usar para proteger dados reais. HMAC nao cifra.)")

# ---------- 6. resumo limitado ao que este script testa ----------
print("\n== RESUMO DO EXPERIMENTO ==")
print(f"Protocolo: {100*(1-c1/o1):.1f}% menos bytes, reconstrucao {ok1}/{n1}.")
print(f"Texto livre: {100*(1-c2/o2):.1f}% de variacao, reconstrucao {ok2}/{n2}.")
print("O tamanho depende do dominio e do dicionario compartilhado.")
print(f"Dicionario: {len(ZD)} B, nao contabilizado por mensagem; considerar custo de distribuicao.")
