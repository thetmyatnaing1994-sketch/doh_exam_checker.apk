import os

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

import json
import sys
import tkinter as tk
from tkinter import filedialog
import flet as ft

# Tmn_Examdata.py မှ မေးခွန်းအဖြေ ဒေတာဘေ့စ်ကို Import ပြုလုပ်ခြင်း
try:
    from Tmn_Examdata import exam_qa_data
except ImportError:
    print(
        "Error: 'Tmn_Examdata.py' ဖိုင်ကို ရှာမတွေ့ပါ။ ၎င်းဖိုင်သည် ဤ script နှင့် Directory တစ်ခုတည်းတွင် ရှိရပါမည်။")
    sys.exit(1)


def calculate_grade(percentage):
    if percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "E"


def main(page: ft.Page):
    page.title = "လမ်းဦးစီးဌာန စာမေးပွဲ ရလဒ် စစ်ဆေးရေးစနစ်"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    selected_file_paths = []

    selected_file_text = ft.Text(
        "ဖိုင် ရွေးချယ်ထားခြင်း မရှိသေးပါ။",
        color=ft.Colors.GREY_400,
        size=15,
    )
    error_text = ft.Text("", color=ft.Colors.RED_400)

    def show_input_screen():
        nonlocal selected_file_paths
        selected_file_paths = []
        selected_file_text.value = "ဖိုင် ရွေးချယ်ထားခြင်း မရှိသေးပါ။"
        selected_file_text.color = ft.Colors.GREY_400
        error_text.value = ""

        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        title = ft.Text(
            "စာမေးပွဲ အဖြေ JSON ဖိုင်များ ရွေးချယ် စစ်ဆေးရန်",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_400,
        )

        def open_picker(e):
            nonlocal selected_file_paths
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            files_selected = filedialog.askopenfilenames(
                title="JSON ဖိုင်များကို ရွေးချယ်ပါ (Ctrl သို့မဟုတ် Shift နှိပ်၍ အများအပြား ရွေးနိုင်ပါသည်)",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            root.destroy()

            if files_selected:
                selected_file_paths = list(files_selected)
                selected_file_text.value = f"ရွေးချယ်ထားသော ဖိုင်ပေါင်း - {len(selected_file_paths)} ဖိုင်"
                selected_file_text.color = ft.Colors.GREEN_400
                error_text.value = ""
            else:
                selected_file_paths = []
                selected_file_text.value = "ဖိုင် ရွေးချယ်မှု မပြုလုပ်ခဲ့ပါ။"
                selected_file_text.color = ft.Colors.GREY_400

            page.update()

        browse_btn = ft.Button(
            content=ft.Text("📁 JSON ဖိုင်များ ရွေးချယ်မည် (Browse Multiple Files)"),
            icon=ft.Icons.FOLDER_OPEN,
            height=45,
            on_click=open_picker,
        )

        def process_json_files(e):
            if not selected_file_paths:
                error_text.value = "ကျေးဇူးပြု၍ စစ်ဆေးလိုသည့် JSON ဖိုင်(များ)ကို အရင် ရွေးချယ်ပေးပါ။"
                page.update()
                return

            all_results = []

            for fpath in selected_file_paths:
                if not os.path.exists(fpath):
                    continue

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        submission_data = json.load(f)

                    user_info = submission_data.get("user_info", {})
                    user_name = user_info.get("name", "မသိရှိရပါ")
                    roll_no = user_info.get("roll_no", "မသိရှိရပါ")

                    submissions = submission_data.get("submissions", [])
                    user_answers_map = {
                        sub.get("question_id"): sub.get("user_answer", "-")
                        for sub in submissions
                        if sub.get("question_id")
                    }

                    cat_scores = {}
                    cat_totals = {}
                    detailed_qa_by_cat_and_type = {}
                    total_score = 0
                    total_questions = 0

                    # Tmn_Examdata.py မှ မေးခွန်းအဖြေများနှင့် တိုက်ဆိုင်စစ်ဆေးခြင်း
                    for cat_key, cat_data in exam_qa_data.items():
                        c_score = 0
                        c_total = 0
                        detailed_qa_by_cat_and_type[cat_key] = {}

                        for q_type, q_list in cat_data.items():
                            type_qa_list = []
                            for item in q_list:
                                c_total += 1
                                q_id = item["id"]
                                q_text = item.get("question", "")
                                correct_ans = str(item.get("answer", "")).strip()
                                user_ans = str(user_answers_map.get(q_id, "-")).strip()

                                is_correct = False
                                if user_ans and user_ans.lower() == correct_ans.lower():
                                    c_score += 1
                                    is_correct = True

                                type_qa_list.append({
                                    "question": q_text,
                                    "user_answer": user_ans,
                                    "correct_answer": correct_ans,
                                    "is_correct": is_correct
                                })

                            detailed_qa_by_cat_and_type[cat_key][q_type] = type_qa_list

                        cat_scores[cat_key] = c_score
                        cat_totals[cat_key] = c_total
                        total_score += c_score
                        total_questions += c_total

                    percentage = (
                        (total_score / total_questions * 100)
                        if total_questions > 0
                        else 0
                    )
                    grade = calculate_grade(percentage)

                    all_results.append(
                        {
                            "name": user_name,
                            "roll_no": roll_no,
                            "score": total_score,
                            "total": total_questions,
                            "percentage": percentage,
                            "grade": grade,
                            "cat_scores": cat_scores,
                            "cat_totals": cat_totals,
                            "detailed_qa_by_cat_and_type": detailed_qa_by_cat_and_type,
                        }
                    )

                except Exception as ex:
                    print(f"Error processing {fpath}: {ex}")

            if all_results:
                show_summary_screen(all_results)
            else:
                error_text.value = "JSON ဖိုင်များ ဖတ်ရှုရာတွင် အမှားအယွင်း ရှိနေပါသည်။"
                page.update()

        check_btn = ft.Button(
            content=ft.Text("🔍 အဖြေများ စစ်ဆေးမည်"),
            bgcolor=ft.Colors.BLUE_700,
            height=45,
            width=230,
            on_click=process_json_files,
        )

        page.add(
            ft.Column(
                controls=[
                    title,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    browse_btn,
                    selected_file_text,
                    error_text,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    check_btn,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            )
        )

    # ဖြေဆိုသူ တစ်ဦးချင်းစီ၏ ကဏ္ဍနှင့် မေးခွန်းအမျိုးအစားအလိုက် မေးခွန်း/အဖြေများ ပြသသည့် Screen
    def show_detail_screen(user_res, all_results):
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.START

        title = ft.Text(
            f"📝 မေးခွန်းနှင့် အဖြေများ အသေးစိတ် - {user_res['name']} (ခုံနံပါတ် - {user_res['roll_no']})",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.LIGHT_BLUE_300,
        )

        cat_names = {
            "administrative": "အုပ်ချုပ်မှု ကဏ္ဍ",
            "finance": "ငွေစာရင်း ကဏ္ဍ",
            "technical": "နည်းပညာ ကဏ္ဍ",
        }

        q_type_names = {
            "true_false": "True / False မေးခွန်းများ",
            "multiple_choice": "Multiple Choice မေးခွန်းများ",
            "fill_in_the_blank": "Fill in the Blanks မေးခွန်းများ",
            "descriptive": "Descriptive (စာရေးဖြေ) မေးခွန်းများ",
        }

        content_controls = [
            title,
            ft.Button(
                content=ft.Text("⬅️ ရလဒ်အချုပ်သို့ ပြန်သွားမည်"),
                on_click=lambda e: show_summary_screen(all_results),
                height=40,
            ),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ]

        # ၁။ ကဏ္ဍအလိုက် ခွဲခြားခြင်း (အုပ်ချုပ်မှု၊ ငွေစာရင်း၊ နနည်းပညာ)
        for cat_key, type_dict in user_res["detailed_qa_by_cat_and_type"].items():
            cat_title_text = cat_names.get(cat_key, cat_key.capitalize())
            c_score = user_res["cat_scores"].get(cat_key, 0)
            c_tot = user_res["cat_totals"].get(cat_key, 0)

            # ကဏ္ဍကြီး ခေါင်းစဉ်
            cat_header = ft.Container(
                content=ft.Text(
                    f"📌 {cat_title_text} ({c_score} / {c_tot} မှတ်)",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.AMBER_300,
                ),
                padding=10,
            )
            content_controls.append(cat_header)

            # ၂။ မေးခွန်းအမျိုးအစားအလိုက် ထပ်မံခွဲခြားခြင်း (True/False, MCQ, Fill in Blank, Descriptive)
            for q_type_key, qa_list in type_dict.items():
                if not qa_list:
                    continue

                q_type_lbl = q_type_names.get(q_type_key, q_type_key.replace("_", " ").title())

                type_score = sum(1 for item in qa_list if item["is_correct"])
                type_tot = len(qa_list)

                qa_cards = []
                for q_idx, qa in enumerate(qa_list, start=1):
                    icon = (
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
                        if qa["is_correct"]
                        else ft.Icon(ft.Icons.CANCEL, color=ft.Colors.RED)
                    )
                    u_ans_color = ft.Colors.GREEN_400 if qa["is_correct"] else ft.Colors.RED_400

                    qa_cards.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                icon,
                                                ft.Text(
                                                    f"မေးခွန်း ({q_idx}): {qa['question']}",
                                                    weight=ft.FontWeight.BOLD,
                                                    size=15,
                                                    expand=True,
                                                ),
                                            ]
                                        ),
                                        ft.Divider(height=5, color=ft.Colors.GREY_800),
                                        ft.Text(f"• ဖြေဆိုထားသော အဖြေ : {qa['user_answer']}", color=u_ans_color,
                                                size=14),
                                        ft.Text(f"• အဖြေမှန် : {qa['correct_answer']}", color=ft.Colors.BLUE_300,
                                                size=14),
                                    ],
                                    spacing=5,
                                ),
                                padding=12,
                            )
                        )
                    )

                # ExpansionTile (initially_expanded ဖြုတ်ထားပါသည်)
                type_expansion = ft.ExpansionTile(
                    title=ft.Text(
                        f"🔹 {q_type_lbl} ({type_score} / {type_tot} မှတ်)",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.CYAN_200,
                    ),
                    controls=qa_cards,
                )

                content_controls.append(type_expansion)

            content_controls.append(ft.Divider(height=15, color=ft.Colors.GREY_800))

        back_to_summary_btn = ft.Button(
            content=ft.Text("⬅️ ရလဒ်အချုပ်သို့ ပြန်သွားမည်"),
            on_click=lambda e: show_summary_screen(all_results),
            height=40,
        )
        content_controls.append(back_to_summary_btn)

        page.add(
            ft.Column(
                controls=content_controls,
                spacing=10,
            )
        )

    # အချုပ်ဇယား + တစ်ယောက်ချင်းစီ၏ ကဏ္ဍအလိုက် အချုပ် ပြသသည့် Screen
    def show_summary_screen(results):
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.START

        title = ft.Text(
            f"🏆 စာမေးပွဲ ဖြေဆိုသူများ၏ ရလဒ် စစ်ဆေးမှု ရလဒ် ({len(results)} ဦး)",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_400,
        )

        cat_names = {
            "administrative": "အုပ်ချုပ်မှု",
            "finance": "ငွေစာရင်း",
            "technical": "နည်းပညာ",
        }

        # ၁။ ရလဒ် အချုပ် ဇယား (Summary Table)
        table_rows = []
        for idx, res in enumerate(results, start=1):
            g_color = (
                ft.Colors.GREEN_400
                if res["grade"] in ["A", "B"]
                else (ft.Colors.AMBER_400 if res["grade"] in ["C", "D"] else ft.Colors.RED_400)
            )

            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(idx))),
                        ft.DataCell(ft.Text(res["roll_no"], weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(res["name"])),
                        ft.DataCell(ft.Text(f"{res['score']} / {res['total']}")),
                        ft.DataCell(ft.Text(f"{res['percentage']:.2f}%")),
                        ft.DataCell(
                            ft.Text(
                                f"Grade {res['grade']}",
                                color=g_color,
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                    ]
                )
            )

        summary_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("စဉ်")),
                ft.DataColumn(ft.Text("ခုံနံပါတ်")),
                ft.DataColumn(ft.Text("ဖြေဆိုသူ အမည်")),
                ft.DataColumn(ft.Text("စုစုပေါင်း ရမှတ်")),
                ft.DataColumn(ft.Text("ရာခိုင်နှုန်း")),
                ft.DataColumn(ft.Text("အဆင့် (Grade)")),
            ],
            rows=table_rows,
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.GREY_700),
                bottom=ft.BorderSide(1, ft.Colors.GREY_700),
                left=ft.BorderSide(1, ft.Colors.GREY_700),
                right=ft.BorderSide(1, ft.Colors.GREY_700),
            ),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_800),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_800),
        )

        summary_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "📊 ဖြေဆိုသူများ၏ ရလဒ်အချုပ် ဇယား",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_300,
                        ),
                        ft.Divider(),
                        summary_table,
                    ]
                ),
                padding=15,
            )
        )

        # ၂။ တစ်ယောက်ချင်းစီ၏ ကဏ္ဍအလိုက် အသေးစိတ်
        detail_cards = []
        for idx, res in enumerate(results, start=1):
            cat_details = []
            for c_key, c_score in res["cat_scores"].items():
                c_tot = res["cat_totals"].get(c_key, 0)
                c_pct = (c_score / c_tot * 100) if c_tot > 0 else 0
                c_lbl = cat_names.get(c_key, c_key.capitalize())

                cat_details.append(
                    ft.Row(
                        [
                            ft.Text(f"• {c_lbl} ပိုင်း :", size=14, expand=True),
                            ft.Text(
                                f"{c_score} / {c_tot} မှတ် ({c_pct:.1f}%)",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.CYAN_300,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                )

            g_color = (
                ft.Colors.GREEN_400
                if res["grade"] in ["A", "B"]
                else (ft.Colors.AMBER_400 if res["grade"] in ["C", "D"] else ft.Colors.RED_400)
            )

            # သီးသန့် စာမျက်နှာသို့ သွားရန် ခလုတ်
            view_qa_btn = ft.Button(
                content=ft.Text("📝 မေးခွန်းနှင့် အဖြေများ အသေးစိတ် စစ်ဆေးရန်"),
                icon=ft.Icons.LIST_ALT,
                on_click=lambda e, r=res: show_detail_screen(r, results),
            )

            u_card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"👤 ({idx}) {res['name']}  [ ခုံနံပါတ် - {res['roll_no']} ]",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"Grade {res['grade']}",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=g_color,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=5),
                            ft.Text("ကဏ္ဍအလိုက် မှတ်တမ်း -", color=ft.Colors.GREY_400),
                            *cat_details,
                            ft.Divider(height=5),
                            ft.Row(
                                [
                                    ft.Text("စုစုပေါင်း ရမှတ် :", weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        f"{res['score']} / {res['total']} မှတ် ({res['percentage']:.2f}%)",
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREEN_300,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=5),
                            view_qa_btn,
                        ],
                        spacing=8,
                    ),
                    padding=15,
                )
            )
            detail_cards.append(u_card)

        back_btn = ft.Button(
            content=ft.Text("🔄 အခြား ဖိုင်များ ထပ်မံ စစ်ဆေးမည်"),
            on_click=lambda e: show_input_screen(),
        )

        page.add(
            ft.Column(
                controls=[
                    title,
                    summary_card,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Text(
                        "🔍 တစ်ယောက်ချင်းစီ၏ ကဏ္ဍအလိုက် အသေးစိတ် ရမှတ်များ",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ORANGE_300,
                    ),
                    *detail_cards,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    back_btn,
                ],
                spacing=15,
            )
        )

    show_input_screen()


if __name__ == "__main__":
    try:
        ft.run(main)
    except AttributeError:
        ft.app(target=main)