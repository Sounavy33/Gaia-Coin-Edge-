# Nota técnica preliminar: CLX para codificação reversível em protocolo controlado

**Projeto:** Gaia Coin / processamento de borda  
**Autor do projeto:** Antônio Alberto Lopes Elias (Sounavy)  
**Estado:** prova de conceito exploratória; resultados requerem execução e reprodução independente  
**Corpus:** sintético, sem dados clínicos reais

## Resumo

Esta nota descreve uma prova de conceito de codificação baseada em dicionário para mensagens curtas geradas por um protocolo clínico fictício. Cada palavra conhecida é substituída por um identificador de um byte; palavras fora do vocabulário são representadas por um escape com comprimento e bytes UTF-8. O decodificador reconstrói a mensagem e o script verifica igualdade textual e igualdade de hash SHA-256. A implementação também compara comprimentos com zlib, zlib com dicionário compartilhado e LZMA.

O resultado positivo que o desenho permite testar é delimitado: **reconstrução sem perda no corpus sintético** e possível redução do número de bytes para mensagens que usam o vocabulário instalado. A taxa efetiva deve ser lida na saída de uma execução reproduzível. Este material não afirma redução de tráfego ou energia em redes reais, desempenho clínico, segurança adequada para produção, nem validação econômica da Gaia Coin.

## Pergunta

Para mensagens curtas geradas por um protocolo de vocabulário controlado, a codificação CLX pode reduzir o número de bytes por mensagem e permitir reconstrução exata quando codificador e decodificador compartilham o mesmo dicionário?

## Método

O script `experiments/clx_poc.py`:

1. Gera frases fictícias a partir de listas fixas de queixas, achados, condutas e retornos, com semente aleatória definida.
2. Separa 400 frases para construir o vocabulário e usa frases distintas como teste; as frases completas de teste não aparecem no treino, embora compartilhem a gramática e os termos do corpus.
3. Codifica palavras do dicionário em um byte e palavras desconhecidas com um marcador de escape, comprimento e bytes UTF-8.
4. Decodifica e verifica igualdade textual e SHA-256.
5. Compara tamanhos individuais com zlib, zlib usando o mesmo dicionário, LZMA e CLX.
6. Inclui cinco exemplos de texto livre fora do domínio e um exemplo didático de verificação HMAC.

A comparação apresentada contabiliza os bytes de cada mensagem codificada, mas não inclui o custo de distribuir o dicionário compartilhado. O código imprime o tamanho do dicionário; estudos seguintes devem informar a política de versão e o ponto de equilíbrio do custo amortizado.

## Resultados que o script mede

Ao executar o código, a saída informa, para cada conjunto:

- total de bytes originais e codificados por método;
- percentual de redução ou aumento relativo ao texto original;
- número de reconstruções idênticas entre o total de mensagens;
- tamanho do dicionário compartilhado;
- aceitação do texto original e rejeição da mensagem alterada no exemplo HMAC.

**Não foram inseridos números de execução nesta nota.** Eles devem ser copiados da saída real do script, junto com a versão de Python e ambiente, para evitar apresentar valores não reproduzidos.

## Limitações e interpretação

- O corpus é sintético e deriva de uma gramática restrita; não representa prontuários ou linguagem clínica real.
- As frases de teste não são frases de treino, mas usam os mesmos componentes e a mesma estrutura. Portanto, o teste avalia combinações dentro do protocolo, não generalização para um domínio independente.
- O corpus de texto livre tem somente cinco exemplos e é ilustrativo, não uma amostra estatística representativa.
- O dicionário precisa existir e corresponder exatamente nos dois lados. Seu custo de distribuição e manutenção deve ser amortizado em cenários realistas.
- O campo de comprimento do escape tem um byte; o código atual não é adequado a palavras desconhecidas com mais de 255 bytes UTF-8 sem uma extensão de formato.
- SHA-256 é usado como verificação adicional de igualdade no experimento, não como autenticação.
- O exemplo HMAC usa chave fictícia e tag truncada de quatro bytes apenas para demonstração. Não deve ser reutilizado para proteger dados reais; HMAC não cifra o conteúdo.
- Tamanho em bytes não equivale automaticamente a economia de energia, latência ou custo de rede. Isso exigiria medições no dispositivo e no transporte, incluindo dicionário, cabeçalhos, metadados e condições de rede.

## Estudos e instrumentos prévios

Resultados de instrumentos ou simulações anteriores que não tenham protocolo completo, dados, código executável, parâmetros e saída verificável são registrados como **exploratórios e ainda não confirmados**. Não se atribuem a eles conclusões quantitativas ou validação independente nesta nota. O passo seguinte é preservar cada instrumento, descrever seu propósito e suas limitações e tornar possível a reprodução antes de comparar resultados.

## Próximos passos de teste

1. Executar o script sem alterações e arquivar a saída completa, versão de Python e sistema operacional.
2. Repetir em outra instalação Python e comparar a saída determinística.
3. Adicionar testes para palavras desconhecidas, pontuação, Unicode, comprimentos longos, entradas malformadas e versionamento do dicionário.
4. Comparar CLX com formatos e configurações adequados a mensagens curtas, incluindo o custo amortizado do dicionário.
5. Medir tempo e energia em dispositivos de borda, se a hipótese de eficiência energética for investigada.
6. Fazer avaliação independente com corpus autorizado, minimizado e sem dados pessoais desnecessários.

## Conclusão

O CLX é uma prova de conceito testável de codificação reversível com dicionário compartilhado. O script foi estruturado para demonstrar reconstrução idêntica e medir a variação de tamanho em um protocolo controlado. A positividade do resultado deve ser limitada ao que a execução confirmar. As hipóteses maiores sobre eficiência de borda, economia verde, saúde ou Gaia Coin permanecem perguntas de pesquisa separadas.

## Referências técnicas

- Deutsch, P. (1996). *DEFLATE Compressed Data Format Specification*, RFC 1951. https://www.rfc-editor.org/rfc/rfc1951
- Deutsch, P., & Gailly, J.-L. (1996). *ZLIB Compressed Data Format Specification*, RFC 1950. https://www.rfc-editor.org/rfc/rfc1950
- Krawczyk, H., Bellare, M., & Canetti, R. (1997). *HMAC: Keyed-Hashing for Message Authentication*, RFC 2104. https://www.rfc-editor.org/rfc/rfc2104
