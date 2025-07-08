# Plataforma de Batimento de SWAPs | Tesouraria BR Partners
Este sistema permite comparar de forma automática os dados de SWAPs entre a Tesouraria e o BackOffice.  
A plataforma realiza batimento de valores com base em imagens (OCR) e planilhas Excel, destacando eventuais divergências.
## Como acessar a plataforma
Acesse pelo link abaixo:
https://plataforma-swap-br-shto3mmq8npqjpcvzc7fnv.streamlit.app/

## Tipos de batimento disponíveis
Ao abrir a plataforma, selecione no menu:

### 1. Swap – Vencimento para vencimentos de swap 
Faça o uma cópia da aba mestre da planilha ‘Accrual swaps (version 2)’ e realize o upload no campo **planilha mestre (Excel)**.
Tire um prt sc do comprovante de vencimento da swap enviado pelo back office por email. Faça o upload do mesmo no campo **comprovante de swap (imagem)**. 
Selecione o cliente determinado no comprovante. 
A plataforma, então, compara os dados extraídos do **comprovante de swap (imagem)** com a **planilha mestre (Excel)**.
Você verá:
- Dados extraídos da imagem
- Dados da planilha
- Comparação campo a campo com status `✔️` ou `❌`

> Obs: campos como "Notional", "Taxa Pré", "Parcela CDI", "Juros CDI", "Ajuste" e datas são automaticamente comparados.
### 2. `Accrual - Último dia útil` para batimento de accrual 
1. Faça upload da **planilha da Tesouraria** (aba mestre)
2. Faça upload da **planilha do BackOffice BI Sales Accrual ** (normalmente com header a partir da 4ª linha)
3. A plataforma compara as informações dos contratos (**Ponta Dada** e **Ponta Tomada**)  com base no número de contrato e data de vencimento.
Você verá duas tabelas:
- Comparação da Ponta Dada
- Comparação da Ponta Tomada  
Cada linha mostra se o valor está `✅ Batido` ou `❌ Divergente`.
---
## Observações técnicas
- O sistema usa **OCR (Tesseract)** para extrair textos das imagens
- Os valores são convertidos automaticamente para comparação
- Pequenas diferenças de centavos (< R$ 0,50) são ignoradas
## Suporte

Caso haja dúvidas, erros ou necessidade de ajuste:
>  Fale com Isabela Haddad – Tesouraria BR Partners  (isabela.haddad@brpartners.com.br) 
>  Ou abra uma issue neste repositório

## Desenvolvido por  
**Isabela Haddad**  
Tesouraria BR Partners – 2025
