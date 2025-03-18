from module_ollama_query import * 

url = "https://arkeabio.bamboohr.com/careers/48"
env_variables = load_env_variables()
html = webpage_call(url, 
                    env_variables['linkedin_username'], 
                    env_variables['linkedin_password'])



if __name__ == "__main__":
    job_details = get_attributes(attributes_dict(),
                                 env_variables,
                                 html
                                 )