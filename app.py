from shiny import App, render, ui, reactive
import pandas as pd
import scripts.ollama.ollama_query as ollama  # Import the separate Python file

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text("text_input", "Enter text:", placeholder="Type something here..."),
        ui.input_action_button("go_button", "Go"),
        ui.output_text("process_result"),  # Add an output to display the result
        width=250
    ),
    ui.h1("Interactive Data Frame Table Example"),
    ui.output_data_frame("interactive_table")
)

def server(input, output, session):
    @render.data_frame
    def interactive_table():
        # Create a pandas DataFrame using the provided data dictionary
        data = pd.read_csv('data/initial_job_table.csv')
        df = pd.DataFrame(data)
        # Return the DataFrame without any additional parameters
        return df

    @render.text
    @reactive.event(input.go_button)
    async def process_result():  # ✅ Make this function async
        text_to_process = input.text_input()
        result = await ollama.ollama_response(text_to_process)
        return f"Processed: {result}"


app = App(app_ui, server)


