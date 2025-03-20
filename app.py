from scripts.database.json_to_db import insert_json_into_db
from shiny import App, ui, reactive
from shiny.express import render
import json
import pandas as pd
import scripts.ollama.ollama_query as ollama  
import sqlite3

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text("text_input", "Enter URL:", placeholder="Type something here..."),
        ui.input_action_button("go_button", "Get Details"),
        ui.input_text_area("json_editor", "Edit JSON Response:", "", height="200px"),
        ui.input_action_button("save_button", "Save to Table"),
        ui.output_text("save_message_output"),
        width=250
    ),
    ui.div(
        ui.div(
            ui.h1("Job Search 2025"),
            ui.input_text("search_input", "", placeholder="Type to search...", width="250px"),
            class_="d-flex justify-content-between align-items-center w-100"
        ),
        ui.output_data_frame("interactive_table"),
        class_="container-fluid"
    )
)


def server(input, output, session):
    json_response = reactive.value("") 
    save_message = reactive.value("")
    trigger_refresh = reactive.value(0)

    @render.data_frame
    def interactive_table():
        trigger_refresh()
        conn = sqlite3.connect("data/sqlite/database.db")
        df = pd.read_sql_query(f"SELECT * FROM jobs;", conn)
        conn.close()

        # Search bar
        search_query = input.search_input().strip().lower()
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(search_query).any(), axis=1)]

        return render.DataGrid(df, editable=True)

    @reactive.effect
    @reactive.event(input.go_button)
    async def process_result():
        text_to_process = input.text_input()
        result = await ollama.ollama_response(text_to_process)  

        if isinstance(result, dict):
            result["website"] = text_to_process
        
        json_response.set(json.dumps(result))
        ui.update_text_area("json_editor", value=json_response())

    @reactive.effect
    @reactive.event(input.save_button)
    def save_json_changes():
        try:
            edited_json = json.loads(input.json_editor())
            insert_json_into_db(edited_json)
            save_message.set(f"{edited_json['job_title'].title()} from {edited_json['company_name'].title()} successfully inserted into database!")
            trigger_refresh.set(trigger_refresh() + 1)  # Increment value to trigger reactivity
        except json.JSONDecodeError:
            save_message.set("Error: Invalid JSON format")

    @render.text
    def save_message_output():
        return save_message()
    

app = App(app_ui, server)