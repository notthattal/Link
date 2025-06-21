## User Guide

### What It Does
This chatbot allows you to interact with any persona of your choosing. From historical figures to superheros, CharacterBot is a fun and new way to interact with your favorite characters.

### How to install

1. Clone this repository 
```bash
git clone https://github.com/notthattal/AwsGenAIImplementation.git
cd AwsGenAIImplementation
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

3. Install the requirements for the backend
```bash
pip install -r requirements.txt
```

4. Start the requirements for the frontend
```bash
cd frontend
npm install
``` 

5. Start the frontend
```bash
npm run dev
```

6. Start the backend *(In a new terminal pointing to the project root directory)*
```bash
python server.py
```

7. Run tests and test for coverage *(Optional)*
```bash
pytest --cov=.
```

### How to interact with CharacterBot

1. Create an account or sign-in
2. Verify your account (if first time signing in)
3. Tell CharacterBot which persona you would like to speak to
4. Chat like you would with any other chatbot! It's that easy!