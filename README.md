# Check-Mate: An LLM powered approximate computing solution for Battryless-IoT

- add application you want to approximate into target folder.
- You need to make a .env file. Instructions below
- run main.py to run!
- run clean.py before next run.

### Requiered installs
You gonna need to install the following:

- sudo apt install graphviz
- perl (https://www.perl.org/get.html) you most likly have this already installed by default.
- egypt installation guide here (https://www.gson.org/egypt/egypt.html)
- clangd (us should already have this with base debian or ubuntu)

### .env
Create a .env file and add the following:

```
OPENAI_API_KEY="API-KEY"
LLM_MODEL = "gpt-4o"
```