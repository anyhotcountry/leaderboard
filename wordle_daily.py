from datetime import date
import appex
import os
from wordle import html, load_chats
from ui import WebView, DatePicker, DATE_PICKER_MODE_DATE

def main():
    if not appex.is_running_extension():
        print("ERROR: This script is meant to be run from the sharing extension.")
    else:
        input_files = appex.get_attachments()
        # get first input file and check it has zip extension
        if not input_files or not input_files[0].lower().endswith(".zip"):
            print("ERROR: No zip file found in input.")
            return
        chats = load_chats(input_files[0], "_chat.txt")
        end_date = date.today()
        html_output = html(chats, end_date)
        webview = WebView(name=str(date))
        webview.load_html(html_output)
        webview.present(hide_close_button=True)

if __name__ == "__main__":
    main()

