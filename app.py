from scripts.database.json_to_db import insert_json_into_db
from shiny import App, render, ui, reactive
import json
import pandas as pd
import scripts.ollama.ollama_query as ollama  
import sqlite3

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text("text_input", "Enter text:", placeholder="Type something here..."),
        ui.input_action_button("go_button", "Go"),
        ui.input_text_area("json_editor", "Edit JSON Response:", "", height="200px"),
        ui.input_action_button("save_button", "Save Changes"),
        ui.output_text("save_message_output"),
        width=250
    ),
    ui.h1("Interactive Data Frame Table Example"),
    ui.output_data_frame("interactive_table")
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
        return df

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