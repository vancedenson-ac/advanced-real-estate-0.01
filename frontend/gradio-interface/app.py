"""Gradio UI for direct API experimentation."""
import gradio as gr
import requests
import json
from typing import Optional

API_BASE_URL = "http://backend:8000/api"

def upload_image(file, listing_id: Optional[int] = None, async_mode: bool = False):
    """Upload image and get predictions."""
    if file is None:
        return "Please upload an image file"
    
    try:
        with open(file.name, 'rb') as f:
            files = {'file': f}
            data = {}
            if listing_id:
                data['listing_id'] = listing_id
            
            endpoint = f"{API_BASE_URL}/upload/async" if async_mode else f"{API_BASE_URL}/upload/"
            response = requests.post(endpoint, files=files, data=data)
            response.raise_for_status()
            
            result = response.json()
            return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


def query_images(query_text: str, k: int = 6, listing_id: Optional[int] = None):
    """Query similar images."""
    if not query_text:
        return "Please enter a query"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query/",
            json={
                "query": query_text,
                "k": k,
                "listing_id": listing_id if listing_id else None
            }
        )
        response.raise_for_status()
        
        result = response.json()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


def chat(message: str, conversation_id: Optional[int] = None, listing_id: Optional[int] = None):
    """Chat with RAG assistant."""
    if not message:
        return "Please enter a message"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/",
            json={
                "message": message,
                "conversation_id": conversation_id if conversation_id else None,
                "listing_id": listing_id if listing_id else None,
                "user_id": None
            }
        )
        response.raise_for_status()
        
        result = response.json()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


def get_image(image_id: int):
    """Get image metadata by ID."""
    try:
        response = requests.get(f"{API_BASE_URL}/images/{image_id}")
        response.raise_for_status()
        
        result = response.json()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Real Estate AI API Testing") as demo:
    gr.Markdown("# Real Estate AI API Testing Interface")
    gr.Markdown("Use this interface to test the API endpoints directly.")
    
    with gr.Tabs():
        with gr.Tab("Upload Image"):
            with gr.Row():
                with gr.Column():
                    upload_file = gr.File(label="Upload Image", type="filepath")
                    upload_listing_id = gr.Number(label="Listing ID (optional)", value=None)
                    upload_async = gr.Checkbox(label="Async Mode", value=False)
                    upload_btn = gr.Button("Upload", variant="primary")
                
                with gr.Column():
                    upload_output = gr.Textbox(label="Result", lines=20)
            
            upload_btn.click(
                fn=upload_image,
                inputs=[upload_file, upload_listing_id, upload_async],
                outputs=upload_output
            )
        
        with gr.Tab("Query Images"):
            with gr.Row():
                with gr.Column():
                    query_text = gr.Textbox(label="Query Text", placeholder="e.g., How can I increase resale value quickly?")
                    query_k = gr.Slider(label="Top K", minimum=1, maximum=20, value=6, step=1)
                    query_listing_id = gr.Number(label="Listing ID (optional)", value=None)
                    query_btn = gr.Button("Query", variant="primary")
                
                with gr.Column():
                    query_output = gr.Textbox(label="Results", lines=20)
            
            query_btn.click(
                fn=query_images,
                inputs=[query_text, query_k, query_listing_id],
                outputs=query_output
            )
        
        with gr.Tab("Chat"):
            with gr.Row():
                with gr.Column():
                    chat_message = gr.Textbox(label="Message", placeholder="Ask about home improvements...")
                    chat_conv_id = gr.Number(label="Conversation ID (optional)", value=None)
                    chat_listing_id = gr.Number(label="Listing ID (optional)", value=None)
                    chat_btn = gr.Button("Send", variant="primary")
                
                with gr.Column():
                    chat_output = gr.Textbox(label="Response", lines=20)
            
            chat_btn.click(
                fn=chat,
                inputs=[chat_message, chat_conv_id, chat_listing_id],
                outputs=chat_output
            )
        
        with gr.Tab("Get Image"):
            with gr.Row():
                with gr.Column():
                    image_id = gr.Number(label="Image ID", value=1)
                    get_image_btn = gr.Button("Get Image", variant="primary")
                
                with gr.Column():
                    get_image_output = gr.Textbox(label="Image Metadata", lines=20)
            
            get_image_btn.click(
                fn=get_image,
                inputs=[image_id],
                outputs=get_image_output
            )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

