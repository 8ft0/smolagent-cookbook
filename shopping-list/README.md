# Shopping List App

A Python-based application for managing shopping lists with AI API integration.

## Features
- Create and manage multiple shopping lists
- Add, remove, and update items
- Mark items as purchased
- API integration for external services
- Input validation and error handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/8ft0/smolagent-cookbook.git
cd shopping-list
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example config file:
```bash
cp src/config/config.example.yaml src/config/config.yaml
```

2. Edit the config.yaml file with your API credentials and settings.

## Usage

Run the application:
```bash
python shopping.py
```

### Example Commands
- Add an item: `add milk`
- Remove an item: `remove milk`
- List items: `list`

