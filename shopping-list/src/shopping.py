#!/usr/bin/env python
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

import gradio as gr
from dotenv import load_dotenv

from exceptions import ShoppingListError
from config import ConfigLoader
from client import ShoppingListClient
from tools import GetShoppingListTool, GetItemDetailsTool, UpdateListTool
from smolagents import CodeAgent, LiteLLMModel, HfApiModel
from smolagents.prompts import CODE_SYSTEM_PROMPT
from prompts import CUSTOM_PROMPT

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('shopping_list.log')
    ]
)

logger = logging.getLogger(__name__)



# Initialize shopping list client
shopping_list_client = ShoppingListClient()


def get_model(model_name: str):
    """Factory function to get the model based on the configuration."""
    logger.debug("Initializing model: %s", model_name)
    try:
        # Load configurations from yaml file
        logger.debug("Loading model configurations")
        config_loader = ConfigLoader()
        model_configs = config_loader.load_model_configs(Path("config/config.yaml"))
        
        if model_name not in model_configs:
            error_msg = f"Model '{model_name}' not found in configurations."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        config = model_configs[model_name]
        logger.debug("Model config loaded: %s", config)
        
        model_class = globals()[config.model_class]
        logger.debug("Model class resolved: %s", model_class)
        
        # Convert dataclass to dict for model initialization
        config_dict = {
            k: v for k, v in config.__dict__.items() 
            if k != 'model_class' and v is not None
        }
        logger.debug("Model config dict: %s", config_dict)
        
        model = model_class(**config_dict)
        logger.debug("Successfully initialized model: %s", model_name)
        return model
        
    except Exception as e:
        logger.error("Error initializing model %s: %s", model_name, str(e))
        logger.debug("Stack trace:", exc_info=True)
        raise


def create_agent(model_name: str = "deepseek_coder") -> CodeAgent:
    """Create and initialize the CodeAgent with tools."""
    logger.debug("Creating agent with model: %s", model_name)
    try:
        # Initialize tools
        logger.debug("Initializing shopping list tools")
        get_shopping_list_tool = GetShoppingListTool()
        get_item_details_tool = GetItemDetailsTool()
        update_list_tool = UpdateListTool()
        logger.debug("Tools initialized successfully")

        # Initialize the model
        logger.debug("Initializing model: %s", model_name)
        model = get_model(model_name)
        logger.info("Successfully initialized model: %s", model_name)

        # Initialize the agent with secure execution environment
        logger.debug("Creating CodeAgent instance")
        agent = CodeAgent(
            tools=[get_shopping_list_tool, get_item_details_tool, update_list_tool],
            model=model,
            add_base_tools=False,
            use_e2b_executor=False,
            system_prompt=CUSTOM_PROMPT
        )
        logger.debug("Agent created successfully")
        
        return agent
        
    except Exception as e:
        logger.error("Error creating agent with model %s: %s", model_name, str(e))
        logger.debug("Stack trace:", exc_info=True)
        raise


def chat_with_model(message: str, history: list, model_name: str) -> str:
    """Handle chat interactions with the model."""
    try:
        agent = create_agent(model_name)
        response = agent.run(message)
        
        # Extract and format the final answer from the response
        if hasattr(response, 'final_answer'):
            answer = response.final_answer
        elif hasattr(response, 'content'):
            answer = response.content
        else:
            answer = str(response)
            
        logger.info("Generated response for message: %s", message[:100])
        return answer
        
    except ShoppingListError as e:
        logger.error("Shopping list error: %s", str(e))
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error("Unexpected error in chat: %s", str(e))

        return "I apologize, but I encountered an unexpected error. Please try again."


def create_chat_interface():
    """Create Gradio chat interface."""
    try:
        # Load available models from config
        config_loader = ConfigLoader()
        model_configs = config_loader.load_model_configs(Path("config/config.yaml"))
        model_choices = list(model_configs.keys())
        
        with gr.Blocks() as demo:
            gr.Markdown("# Shopping List Assistant")
            
            with gr.Row():
                model_dropdown = gr.Dropdown(
                    choices=model_choices,
                    value=model_choices[0] if model_choices else None,
                    label="Select Model"
                )
            
            chatbot = gr.ChatInterface(
                fn=chat_with_model,
                additional_inputs=[model_dropdown],
                examples=[
                    ["Get my shopping list"],
                    ["What's the price of item 101?"],
                    ["Add 2 apples to my list"],
                    ["What's the total cost of my shopping list?"]
                ]
            )
            
            # Add error handling for the chat interface
            chatbot.error = lambda msg: f"Error: {msg}"
        
        return demo
        
    except Exception as e:
        logger.error("Error creating chat interface: %s", str(e))

        raise


def main(model_name: str = "deepseek_coder") -> None:
    """Launch the Gradio interface with error handling."""
    try:
        demo = create_chat_interface()
        demo.launch(
            server_name="0.0.0.0",
            server_port=int(os.getenv('PORT', 7860)),
            debug=os.getenv('DEBUG', 'false').lower() == 'true'
        )
    except Exception as e:
        logger.error("Failed to start application: %s", str(e))

        raise


if __name__ == "__main__":
    try:
        # Example: Run the code with a specific model
        main(model_name="deepseek_coder")
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        exit(1)
