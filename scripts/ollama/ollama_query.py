from module_ollama_query import * 

url = "https://www.linkedin.com/jobs/collections/hiring-in-network/?currentJobId=4138637806&origin=SOCIAL_SEEKING_HIRING_IN_NETWORK_IN_APP_NOTIFICATION&originToLandingJobPostings=4158601156"
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