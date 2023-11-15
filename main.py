from core.TKMain import TKMain

if __name__ == "__main__":
    try:
        sentimentalBot = TKMain()
        sentimentalBot.place_start_window()
    except Exception as e:
        print("O chatbot foi encerrado.")