from module_ollama_query import * 

url = "https://jobs.ashbyhq.com/equip/2f34e681-461b-47ef-a86a-182e3ffc39a8?src=LinkedIn+Posting"
env_variables = load_env_variables()
html = webpage_call(url, 
                    env_variables['linkedin_username'], 
                    env_variables['linkedin_password'])



if __name__ == "__main__":
    job_details = get_attributes(attributes_dict(),
                                 env_variables,
                                 html
                                 )
    print(job_details)