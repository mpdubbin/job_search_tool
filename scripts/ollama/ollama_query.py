"""
This module handles url processing functionality separate from the main Shiny app.
"""

from .module_ollama_query import * 


async def ollama_response(url: str):
    env_variables = load_env_variables()
    html = await webpage_call(url,
                        env_variables['linkedin_username'],
                        env_variables['linkedin_password'])

    return get_attributes(attributes_dict(),
                          env_variables,
                          html)




