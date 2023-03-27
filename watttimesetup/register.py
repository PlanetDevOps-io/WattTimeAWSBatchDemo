import requests
register_url = 'https://api2.watttime.org/v2/register'
params = {'username': 'freddo',
         'password': 'the_frog',
         'email': 'freddo@frog.org',
         'org': 'freds world'}
rsp = requests.post(register_url, json=params)
print(rsp.text)

# check out the details here: https://www.watttime.org/api-documentation/#register-new-user