## User Guide

### What It Does
This chatbot allows you to interact with a chatbot and use it as a personal assistant which can connect with external applications and perform actions.

### How to install

1. Clone this repository 
```bash
git clone https://github.com/notthattal/Link.git
cd Link
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

### How to use

1. Create an account or sign-in
2. Verify your account (if first time signing in)
3. Select the gear in the top right and go to the ConnectApps page to select which apps you would like to use
4. Authenticate with the app you would like to use
5. Navigate back to the homepage and start chatting!