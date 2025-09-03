from datetime import date
import appex
import os
from wordle import (
    load_chats,
    clean_chats,
    parse_plays,
    group_plays_by_date_and_game,
    assign_medals,
    day_results_per_player,
)
from ui import WebView
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

start_date = date(2025, 8, 1)
end_date = (start_date + timedelta(days=32)).replace(day=1)


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
        chats = clean_chats(chats)
        plays = parse_plays(chats)
        grouped = group_plays_by_date_and_game(plays)
        assign_medals(grouped)
        persons = day_results_per_player(grouped)

        df = pd.DataFrame(persons)
        df["Won"] = df["position"]

        month = df[(df["day"] >= start_date) & (df["day"] < end_date)]

        aggs = {
            "Won": pd.NamedAgg(column="position", aggfunc=lambda x: (x == 1).sum()),
            "W": pd.NamedAgg(column="wordleMedal", aggfunc=lambda x: (x == "G").sum()),
            "🌀": pd.NamedAgg(
                column="obsessieMedal", aggfunc=lambda x: (x == "G").sum()
            ),
            "🥕": pd.NamedAgg(column="wortelMedal", aggfunc=lambda x: (x == "G").sum()),
            "N": pd.NamedAgg(column="nerdleMedal", aggfunc=lambda x: (x == "G").sum()),
            "O": pd.NamedAgg(
                column="octordleMedal", aggfunc=lambda x: (x == "G").sum()
            ),
            "SO": pd.NamedAgg(
                column="sequenceOctordleMedal", aggfunc=lambda x: (x == "G").sum()
            ),
            "Q": pd.NamedAgg(column="quordleMedal", aggfunc=lambda x: (x == "G").sum()),
            "SQ": pd.NamedAgg(
                column="sequenceQuordleMedal", aggfunc=lambda x: (x == "G").sum()
            ),
            "5G": pd.NamedAgg(column="golds", aggfunc=lambda x: (x == 5).sum()),
            "6G": pd.NamedAgg(column="golds", aggfunc=lambda x: (x == 6).sum()),
            "7G": pd.NamedAgg(column="golds", aggfunc=lambda x: (x == 7).sum()),
        }

        per_game_stats = month.groupby("name", as_index=False).agg(
            **{k: v for k, v in aggs.items() if v.column in df.columns}
        )

        month_wins = (
            month.groupby("name")
            .agg(
                {
                    "Won": lambda x: (x == 1).sum(),
                }
            )
            .sort_values(by=["Won"], ascending=False)
        )
        month_wins.plot(kind="bar", rot=0)
        plt.xlabel("")
        plt.show()

        TEMPLATE = """
        <!doctype html>
        <html>
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width">
        <title>Results</title>
        <link rel="stylesheet" href="https://cdn.jupyter.org/notebook/5.1.0/style/style.min.css">
        </head>
        <body class="rendered_html">{{CONTENT}}</body>
        </html>
        """

        html = TEMPLATE.replace("{{CONTENT}}", per_game_stats.to_html(index=False))

        webview = WebView(name=str(date))
        webview.load_html(html)
        webview.present(hide_close_button=True)


if __name__ == "__main__":
    main()
