from typing import Dict, Any, Iterator, Tuple, List, Tuple, Callable

import json
import random
import inspect

import gradio as gr

import os
import time

from .utils import _async_save
from .comfyui_workflow_executor import Workflow, WorkflowExecutor, LocalWorkflowExecutor, CeleryWorkflowExecutor


class WorkflowGradioGenerator:
    DEFAULT_COMMON_ORDERS = [
        'api_positive', 'api_negative', 'api_width', 'api_height', 'api_batchsize', 'api_steps', 'api_seed'
    ]

    def __init__(self, 
                 common_orders: List[str] = [], 
                 save_dir: str = "", 
                 wf_executor: WorkflowExecutor = LocalWorkflowExecutor()
                 ):
        """
        Initializes the WorkflowGradioGenerator with an optional list of common keys.
        """
        self.common_orders = common_orders if common_orders else self.DEFAULT_COMMON_ORDERS
        self.save_dir = save_dir
        self.wf_executor = wf_executor

    def _extract_gradio_inputs(self, modifiable_keys: Dict[str, Any], hidden_params: List[str] = None) -> Tuple[List[gr.components.Component], Dict[str, Any]]:
        """
        Dynamically generate Gradio input components based on modifiable keys.
        Rearranges inputs by having the common_keys on top, sorted by their order.
        """
        hidden_params = hidden_params or []
        gr_inputs = []
        input_mapping = {}

        # Sort keys according to common_orders, with non-common keys following
        sorted_keys = sorted(
            [k for k in modifiable_keys.keys() if k not in hidden_params],
            key=lambda k: (k not in self.common_orders, self.common_orders.index(
                k) if k in self.common_orders else float('inf'))
        )

        for key in sorted_keys:
            value = modifiable_keys[key]
            if key == 'api_seed':
                # Special handling for 'api_seed'
                gr_input = gr.Slider(-1, 999999999, step=1,
                                     value=-1, label="seed")
            elif key in ['api_positive', 'api_negative']:
                # Special handling for 'api_positive' and 'api_negative'
                gr_input = gr.Textbox(
                    label=key, value=value, lines=4, placeholder=f"Enter multiple values for {key}")
            elif isinstance(value, int):
                gr_input = gr.Number(label=key, value=value)
            elif isinstance(value, float):
                gr_input = gr.Number(label=key, value=value)
            elif isinstance(value, str):
                gr_input = gr.Textbox(label=key, value=value)
            else:
                # fallback for other types
                gr_input = gr.Textbox(label=key, value=str(value))

            gr_inputs.append(gr_input)
            input_mapping[key] = gr_input

        return gr_inputs, input_mapping

    def _run_workflow_with_overrides(self, workflow: Any, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the workflow with the given overrides and return the result.
        """
        workflow.update_modifiable_keys(overrides)
        api_wf = dict(workflow)

        return self.wf_executor.run_workflow(api_wf)

    def _generate_gradio_function(self, workflow: Any, input_keys: List[str]) -> Callable:
        """
        Generates a Gradio function that accepts fixed arguments based on input_keys.
        """
        def gradio_fn(*args):
            """
            Function to be executed by Gradio with fixed arguments.
            """
            overrides = dict(zip(input_keys, args))

            # Handle random seed generation if api_seed is -1
            if 'api_seed' in overrides and overrides['api_seed'] == -1:
                overrides['api_seed'] = random.randint(0, 999999999)

            actual_seed = overrides.get('api_seed', -1)
            res = self._run_workflow_with_overrides(workflow, overrides)

            images = []
            for key, img_list in res.items():
                if isinstance(img_list, list):
                    images.extend(img_list)

            if self.save_dir:
                self._save_results(images, overrides, actual_seed)

            return images, res

        # Set the function signature to match the input keys
        sig = inspect.signature(gradio_fn)
        new_params = [inspect.Parameter(
            k, inspect.Parameter.POSITIONAL_OR_KEYWORD) for k in input_keys]
        gradio_fn.__signature__ = sig.replace(parameters=new_params)

        return gradio_fn

    def _save_results(self, images: List, overrides: Dict[str, Any], actual_seed: int):
        """
        Save the images and metadata to the specified directory.
        """
        time_str = time.strftime("%Y%m%d-%H%M%S")
        os.makedirs(self.save_dir, exist_ok=True)
        # Save images
        for i, img in enumerate(images):
            _async_save(img, os.path.join(
                self.save_dir, f"{time_str}_{i}.jpg"))

        # Save metadata
        metadata = {
            "user_input": overrides.get('api_positive', ""),
            "positive": overrides.get('api_positive', ""),
            "negative": overrides.get('api_negative', ""),
            "model": "",
            "seed": actual_seed,
            "time_str": time_str
        }

        with open(os.path.join(self.save_dir, f"{time_str}_meta.json"), 'w') as meta_file:
            json.dump(metadata, meta_file)

    def __call__(self,
                 workflow: Any,
                 hidden_params: List[str] = None,
                 title: str = "Dynamic Workflow Runner",
                 description: str = "Modify and run the workflow dynamically using Gradio.",
                 ) -> gr.Interface:
        """
        Generates a Gradio interface for the given workflow, optionally hiding certain parameters.
        """
        modifiable_keys = workflow.get_modifiable_keys()
        gr_inputs, input_mapping = self._extract_gradio_inputs(
            modifiable_keys, hidden_params=hidden_params)

        # Generate the actual function to be used in the Gradio interface
        input_keys = list(input_mapping.keys())
        gradio_fn = self._generate_gradio_function(workflow, input_keys)

        iface = gr.Interface(
            fn=gradio_fn,
            inputs=gr_inputs,
            outputs=[gr.Gallery(label="Generated Images",
                                height=900), gr.JSON(label="Raw Response")],
            title=title,
            description=description,
        )

        return iface


def workflow_to_iface(
    raw_workflow: dict,
    hidden_params: list[str] = [],
    title: str = "Dynamic Workflow Runner",
    description: str = "Modify and run the workflow dynamically using Gradio.",
    save_dir: str = ""
) -> gr.Interface:
    """
    Converts a Comfy-generated workflow to a Gradio interface.

    Parameters:
        raw_workflow (dict): The workflow to convert, using TaggedAny nodes as inputs
        hidden_params (list[str]): The parameters to hide in the interface.
    """
    workflow = Workflow(raw_workflow)
    generator = WorkflowGradioGenerator(save_dir=save_dir)
    iface = generator(workflow, hidden_params=hidden_params,
                      title=title, description=description)
    return iface



def demo():

    import unibox as ub

    wf = ub.loads(
        "/rmt/yada/dev/tr-core/notebooks/vpred_api_default_workflow_api.json")

    workflow = Workflow(wf)
    modifiable_keys = workflow.get_modifiable_keys()

    # Update the modifiable keys
    overrides = {'api_batchsize': '2',
                 'api_positive': 'new positive content',
                 'api_negative': 'new negative content',
                 'api_width': '896',
                 'api_height': '1152',
                 'api_cfg': '0.9',
                 'api_sampler_name': 'euler_cfg_pp',
                 'api_steps': 28
                 }

    workflow.update_modifiable_keys(overrides)
    api_wf = dict(workflow)  # convert to api-compatible dictionary

    executor = WorkflowExecutor()
    res = executor.run_workflow(api_wf)