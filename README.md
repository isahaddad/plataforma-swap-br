# Plataforma de Batimento de SWAPs | Tesouraria BR Partners

Este sistema permite comparar automaticamente os dados de SWAPs entre a Tesouraria e o BackOffice.  
A plataforma realiza o batimento de valores com base em imagens (OCR) e planilhas Excel, destacando eventuais divergências.

---

## 🔗 Como acessar a plataforma

Acesse pelo link abaixo:

👉 [https://plataforma-swap-br-shto3mmq8npqjpcvzc7fnv.streamlit.app/](https://plataforma-swap-br-shto3mmqjpcvzc7fnv.streamlit.app/)

---

## 🛌 Como "acordar" o app depois de muito tempo sem uso

Se o app ficar muito tempo sem uso, ele pode "dormir" automaticamente. Nesse caso, ao tentar acessar, pode aparecer a mensagem:

> **"You do not have access to this app or it does not exist."**
>   <img width="886" height="248" alt="image" src="https://github.com/user-attachments/assets/ef9f30cd-a7ef-49a3-97a2-29c413dc3382" />

**O que fazer?**

1. Saia da página e clique novamente no link da plataforma.
2. Uma nova tela deve aparecer com a mensagem:

   > **"This app has gone to sleep due to inactivity. Would you like to wake it back up?"**
<img width="886" height="261" alt="image" src="https://github.com/user-attachments/assets/a7b83b87-6379-44dd-9062-a910efa2f568" />

3. Clique no botão **"Yes, get this app back up!"** e aguarde alguns segundos até que a aplicação esteja pronta para uso.

Se isso não funcionar:

- Acesse diretamente o site da Streamlit.
- Clique no nome do app e depois no ícone de nuvem para forçar o "acordar".

---

## 📌 Sobre as planilhas utilizadas

A plataforma oferece duas formas de batimento: **Vencimento** e **Accrual**.

- Para o **batimento de vencimento de swap**, utilize a planilha **"Accrual (versão 2)"**.  
  Ela já realiza o cálculo automático do fator CDI e do NI oficial.  
  ✅ *Não é necessário modificar a planilha.* Basta copiar a aba mestre e usá-la como input na plataforma.

- Para o **batimento de accrual**, utilize a planilha **"Accrual (para bater accrual) (versão 2)"**, também automatizada.  
  ✅ *Basta copiar a aba mestre e usá-la como input na seção "Accrual – Último dia útil" da plataforma.*
  
---

## 🧾 Ações necessárias 

Para o cálculo de CDI faz-se necessário realizar o input da taxa CDI do dia. A cada dia é preciso atualizar na aba "CDI" das planilhas (a última aba de ambos os Excel's **"Accrual (versão 2)"** e **"Accrual (para bater accrual) (versão 2)"**) para que o cálculo automático do fator CDI ocorra. 

---

## ⚙️ Tipos de Batimento Disponíveis

### 1. `Swap – Vencimento`

Para realizar o batimento de vencimentos de swap:

1. Copie a aba mestre da planilha **"Accrual (versão 2)"**
2. Faça o upload no campo **Planilha Mestre (Excel)**
3. Tire um print do comprovante de vencimento enviado pelo BackOffice e faça o upload no campo **Comprovante de Swap (imagem)**
4. Selecione o cliente mencionado no comprovante

A plataforma irá comparar os dados extraídos da imagem com os da planilha.

Você verá:

- Dados extraídos da imagem
- Dados da planilha
- Comparação campo a campo com status `✔️` (batido) ou `❌` (divergente)

> Campos como **Notional**, **Taxa Pré**, **Parcela CDI**, **Juros CDI**, **Ajuste** e **datas** são automaticamente verificados.

---

### 2. `Accrual – Último dia útil`

Para realizar o batimento de accrual no fim do mês:

1. Faça upload da planilha da tesouraria **"Accrual (para bater accrual) (versão 2)"** (aba mestre)
2. Faça upload da **Planilha do BackOffice (BI Sales Accrual)** — normalmente com header a partir da 4ª linha
3. A plataforma irá comparar os dados dos contratos (**Ponta Dada** e **Ponta Tomada**), com base no **número do contrato** e **data de vencimento**

Você verá duas tabelas:

- Comparação da **Ponta Dada**
- Comparação da **Ponta Tomada**

Cada linha indicará se o valor está `✅ Batido` ou `❌ Divergente`.

---

## 🧠 Observações Técnicas

- Utiliza **OCR (Tesseract)** para extrair os textos das imagens
- Todos os valores são automaticamente convertidos para o formato correto de comparação
- Diferenças pequenas inferiores a R$ 200,00 são ignoradas (tolerância automática)

---

## 🆘 Suporte

Em caso de dúvidas, erros ou necessidade de ajustes:

**Isabela Haddad** – Tesouraria BR Partners  
📧 isabela.haddad@brpartners.com.br  
📧 isabela.haddad@icloud.com  
📂 Ou abra uma *issue* neste repositório

---

