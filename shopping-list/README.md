# Shopping List App

A Python-based application for managing shopping lists with API integration.

## Features
- Create and manage multiple shopping lists
- Add, remove, and update items
- Mark items as purchased
- API integration for external services
- Input validation and error handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shopping-list.git
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
python -m src.shopping
```

### Example Commands
- Add an item: `add milk`
- Remove an item: `remove milk`
- List items: `list`
- Mark item as purchased: `buy milk`

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
flake8 src/
black src/
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

## License
MIT
