# -*- coding: utf-8 -*-
import os
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

# Token do bot vem da variável de ambiente
TOKEN = os.getenv("TOKEN")

fila = []
modo = {}

# IDs dos funcionários autorizados
ATENDENTES = [1610344, 203122]  # substitua pelos IDs reais

# Variáveis de configuração (link ou descricao)
MODO_BIBLIOTECA = "link"        # "link" ou "descricao"
MODO_CALENDARIO = "link"        # "link" ou "descricao"
MODO_CARDAPIO = "descricao"     # "link" ou "descricao"
MODO_MANUAL = "link"            # "link" ou "descricao"
MODO_CERTIFICADOS = "descricao" # "link" ou "descricao"

def dentro_do_horario():
    agora = datetime.datetime.now().time()
    inicio = datetime.time(7, 0)
    fim = datetime.time(18, 0)
    return inicio <= agora <= fim

def start(update: Update, context: CallbackContext):
    if not dentro_do_horario():
        update.message.reply_text("⏰ Atendimento automático funciona apenas das 07h às 18h.")
        return

    keyboard = [
        [InlineKeyboardButton("🎓 Sou Aluno(a)", callback_data='aluno')],
        [InlineKeyboardButton("👨‍👩‍👧 Sou Pai ou Responsável", callback_data='pai')],
        [InlineKeyboardButton("🧑‍💼 Sou Servidor(a)", callback_data='servidor')],
        [InlineKeyboardButton("🌐 Público Externo", callback_data='externo')],
        [InlineKeyboardButton("🏫 Secretaria Escolar", callback_data='secretaria')],
        [InlineKeyboardButton("📎 Outros Serviços", callback_data='outros')],
        [InlineKeyboardButton("💬 Falar com Atendente", callback_data='fila')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Bem-vindo ao atendimento automático! Escolha uma opção:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    opcao = query.data
    usuario = query.from_user.id

    if opcao == 'aluno':
        modo[usuario] = 'aluno'
        query.edit_message_text(
            text="📚 Opções para Aluno:\n"
                 "1 - Achados e Perdidos\n"
                 "2 - Biblioteca\n"
                 "3 - Cardápio da Merenda\n"
                 "4 - Manual do Aluno\n"
                 "5 - Monitoria Disciplinar\n\n"
                 "Digite o número da opção:"
        )
    elif opcao == 'pai':
        modo[usuario] = 'pai'
        query.edit_message_text(
            text="👨‍👩‍👧 Opções para Pais:\n"
                 "1 - Calendário Escolar\n"
                 "2 - Contatos da Escola\n"
                 "3 - Direção Pedagógica\n"
                 "4 - Supervisão Pedagógica\n\n"
                 "Digite o número da opção:"
        )
    elif opcao == 'fila':
        nome = query.from_user.username or query.from_user.first_name
        if nome not in fila:
            fila.append(nome)
            posicao = len(fila)
            query.edit_message_text(text=f"💬 Você entrou na fila de atendimento.\nSua posição é: {posicao}")
        else:
            posicao = fila.index(nome) + 1
            query.edit_message_text(text=f"💬 Você já está na fila.\nSua posição é: {posicao}")

def resposta(update: Update, context: CallbackContext):
    usuario = update.message.from_user.id
    escolha = update.message.text.strip()

    if usuario in modo:
        categoria = modo[usuario]

        if categoria == 'aluno':
            if escolha == "2":  # Biblioteca
                if MODO_BIBLIOTECA == "link":
                    update.message.reply_text("📖 Biblioteca - Lista de devedores:\nhttps://escola.com/lista.pdf")
                else:
                    update.message.reply_text("📖 Biblioteca - Consulte diretamente na secretaria.")
                return
            elif escolha == "3":  # Cardápio
                if MODO_CARDAPIO == "link":
                    update.message.reply_text("🍽️ Cardápio da Merenda:\nhttps://escola.com/cardapio.pdf")
                else:
                    update.message.reply_text("🍽️ Cardápio disponível na escola.")
                return
            elif escolha == "4":  # Manual
                if MODO_MANUAL == "link":
                    update.message.reply_text("📘 Manual do Aluno:\nhttps://escola.com/manual.pdf")
                else:
                    update.message.reply_text("📘 Manual disponível na secretaria.")
                return

        elif categoria == 'pai':
            if escolha == "1":  # Calendário
                if MODO_CALENDARIO == "link":
                    update.message.reply_text("📅 Calendário Escolar:\nhttps://escola.com/calendario.pdf")
                else:
                    update.message.reply_text("📅 Calendário disponível na secretaria.")
                return

        elif categoria == 'secretaria':
            if escolha == "1":  # Certificados
                if MODO_CERTIFICADOS == "link":
                    update.message.reply_text("📜 Certificados:\nhttps://escola.com/certificados.pdf")
                else:
                    update.message.reply_text("📜 Certificados disponíveis na secretaria.")
                return

        update.message.reply_text("❌ Opção inválida, digite um número válido.")

def chamar_proximo(update: Update, context: CallbackContext):
    usuario = update.message.from_user.id
    if usuario not in ATENDENTES:
        update.message.reply_text("❌ Você não tem permissão para chamar a fila.")
        return

    if fila:
        proximo = fila.pop(0)
        update.message.reply_text(f"✅ O próximo da fila é: {proximo}")
    else:
        update.message.reply_text("📭 Não há ninguém na fila.")

def ver_fila(update: Update, context: CallbackContext):
    usuario = update.message.from_user.id
    if usuario not in ATENDENTES:
        update.message.reply_text("❌ Você não tem permissão para ver a fila.")
        return

    if fila:
        update.message.reply_text(f"👥 Há {len(fila)} pessoas na fila:\n" + "\n".join(fila))
    else:
        update.message.reply_text("📭 Não há ninguém na fila.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("proximo", chamar_proximo))
    dp.add_handler(CommandHandler("fila", ver_fila))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, resposta))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
