#!/usr/bin/python3
'''sd-webui-lora_metadata_viewer
Extension for AUTOMATIC1111.

Version 0.0.0.1
'''
# pylint: disable=invalid-name
# pylint: disable=import-error
# pylint: disable=trailing-whitespace
# pylint: disable=line-too-long
# pylint: disable=no-member

# Import the Python modules.
import os
import json
import gradio as gr
import modules.sd_models as models
import modules.shared
from modules.ui import create_refresh_button
from modules import script_callbacks

# Get LoRA path.
LORA_PATH = getattr(modules.shared.cmd_opts, "lora_dir", os.path.join(models.paths.models_path, "Lora"))

# Create dictionary.
lora_dict = {}

# Function lora_scan().
def lora_scan(lora_dir: str, ext: list):  # lora_dir: str, ext: list
    '''File scan for LoRA models.'''
    global lora_dict
    subdirs, files = [], []
    for fn in os.scandir(lora_dir):
        if fn.is_dir():
            subdirs.append(f.path)
        if fn.is_file():
            if os.path.splitext(fn.name)[1].lower() in ext:                
                files.append(fn.name)
                lora_dict[fn.name] = fn.path
    for dirs in list(subdirs):
        sd, fn = lora_scan(dirs, ext)
        subdirs.extend(sd)
        files.extend(fn)
    files.sort(reverse=False)
    return subdirs, files

# Function get_lora_list().
def get_lora_list():
    '''Simple function for use with components.'''
    lora_list = []
    _, lora_list = lora_scan(LORA_PATH, [".safetensors"])
    return lora_list

# Function on_ui_tabs().
def on_ui_tabs():
    '''Method on_ui_tabs()'''
    # Create a new block.
    with gr.Blocks(analytics_enabled=False) as ui_component:    
        # Create a new row. 
        with gr.Row():
            input_file = gr.Dropdown(value=get_lora_list(), label="LoRA File List" )
            create_refresh_button(input_file, get_lora_list,
                                  lambda: {"choices": get_lora_list()},
                                  "metadata_utils_refresh_1")
        with gr.Row():
            json_input = gr.Code(lines=10, label="Metadata as JSON", language="json")
            input_file.change(
                fn=load_lora_metadata,
                inputs=[input_file], outputs=[json_input]
            )
    return [(ui_component, "Metadata Viewer", "metadata_viewer_tab")]

# Invoke a callback. 
script_callbacks.on_ui_tabs(on_ui_tabs)

# Function get_lora().
def get_lora(lora_file: str):
    '''Function get_lora().'''
    if not os.path.isfile(os.path.join(LORA_PATH, lora_file)):
        return None
    return os.path.join(LORA_PATH, lora_file)

# Function load_lora_metadata().
def load_lora_metadata(input_file: str):
    '''Function load_lora_metadata().'''
    if selected_model := get_lora(lora_dict.get(input_file)):
        if metadata := models.read_metadata_from_safetensors(selected_model):
            return json.dumps(metadata, indent=4, ensure_ascii=False)
        return 'No metadata'
    return 'No model'
