from huggingface_hub import InferenceClient
import time
import os

import dotenv

dotenv.load_dotenv()

HF_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")
hugging_hub_token = HF_TOKEN
if hugging_hub_token is None:
    raise ValueError("Get your Hugging Hub API token from here: https://huggingface.co/docs/hub/security-tokens.\nThen, set it in llm_utils.py.")

# Initialize client without provider specification
llm_inference = InferenceClient("meta-llama/Llama-3.2-3B-Instruct", token=hugging_hub_token)


def LLM(query,
        prompt,
        stop_tokens=None,
        max_length=128,
        temperature=1.,
        return_full_text=False,
        verbose=True,
        debug=True):
    
    new_prompt = f'{prompt}\n{query}\n'
    
    # completion msg
    messages = [
        {
            "role": "system",
            "content": "You are a precise code completion assistant. Complete the code with ONLY the necessary robot commands to fulfill the specific request. Do not generate extra commands. Do not explain. Stop after completing the request."
        },
        {
            "role": "user",
            "content": new_prompt
        }
    ]
    
    params = {
        "max_tokens": max_length,
        "temperature": 0.1, 
        "top_p": 0.9,

    }
    

    if stop_tokens:
        params["stop"] = stop_tokens
    
    s = time.time()
    try:
        # Try chat_completion first
        response = llm_inference.chat_completion(messages, **params)
        response_text = response.choices[0].message.content
        
    except AttributeError:
        # If chat_completion doesn't return the expected format, try text_generation
        if verbose:
            print("Chat completion format issue, trying text_generation...")
        
        try:
            # Try text_generation with the prompt directly
            response_text = llm_inference.text_generation(
                new_prompt,
                max_new_tokens=max_length,
                temperature=0.1,
                do_sample=False,
                return_full_text=False,
                stop_sequences=stop_tokens if stop_tokens else None
            )
        except Exception as e:
            if verbose:
                print(f"text_generation failed: {e}")
            raise
            
    except Exception as e:
        if verbose:
            print(f"Chat completion failed: {e}, trying text_generation...")
        
        try:
            # Fallback to text_generation
            response_text = llm_inference.text_generation(
                new_prompt,
                max_new_tokens=max_length,
                temperature=0.1,
                do_sample=False,
                return_full_text=False,
                stop_sequences=stop_tokens if stop_tokens else None
            )
        except Exception as e2:
            raise ValueError(f"Both methods failed. Chat error: {e}, Text gen error: {e2}")
    
    proc_time = time.time() - s
    if verbose:
        print(f"Inference time {proc_time} seconds")
    
    # DEBUG: Print raw output before any processing
    if debug:
        print("\n" + "="*80)
        print("RAW LLM OUTPUT:")
        print("="*80)
        print(response_text)
        print("="*80 + "\n")
    
    # Clean up the response
    response_text = response_text.strip()
    
    # Additional stop token processing
    if stop_tokens is not None:
        if verbose:
            print('Processing stop tokens...')
        for stoken in stop_tokens:
            if stoken in response_text:
                response_text = response_text[:response_text.index(stoken)]
                response_text = response_text.strip()
    
    # Remove any explanatory text before robot commands
    lines = response_text.split('\n')
    robot_lines = [line for line in lines if line.strip().startswith('robot.')]
    
    if robot_lines:
            response_text = robot_lines[0]
    else:
            response_text = '\n'.join(robot_lines)
    
    if debug:
        print("FILTERED OUTPUT (only robot commands):")
        print("="*80)
        print(response_text)
        print("="*80 + "\n")
    
    return response_text


def LLMWrapper(query, context, verbose=False):
    query = query + ('.' if query[-1] != '.' else '') 
    resp = LLM(query, prompt=prompt_plan, stop_tokens=['#']).strip()
    resp_obj, resp_full = None, resp
    if 'parse_obj' in resp:
        steps = resp.split('\n')
        obj_query = [s for i, s in enumerate(steps) if 'parse_obj' in s][0].split('("')[1].split('")')[0]
        obj_query = context + '\n' + f'# {obj_query}.'
        resp_obj = LLM(obj_query, prompt=prompt_parse_obj, stop_tokens=['#', 'objects = [']).strip()
        resp_full = '\n'.join([resp, '\n' + obj_query, resp_obj])
    if verbose:
        print(query)
        print(resp_full)
    return resp, resp_obj


prompt_pick_and_place_detection = """
objects = ["scissors", "pear", "hammer", "mustard bottle", "tray"]
# put the bottle to the left side.
robot.pick_and_place("mustard bottle", "left side")
objects = ["banana", "foam brick", "strawberry", "tomato soup can", "pear", "tray"]
# move the fruit to the bottom right corner.
robot.pick_and_place("banana", "bottom right corner")
robot.pick_and_place("pear", "bottom right corner")
robot.pick_and_place("strawberry", "bottom right corner")
# now put the green one in the top side.
robot.pick_and_place("pear", "top side")
# undo the last step.
robot.pick_and_place("pear", "bottom right corner")
objects = ["potted meat can", "power drill", "chips can", "hammer", "tomato soup can", "tray"]
# put all cans in the tray.
robot.pick_and_place("potted meat can", "tray")
robot.pick_and_place("chips can", "tray")
robot.pick_and_place("tomato soup can", "tray")
objects = ["power drill", "strawberry", "medium clamp", "gelatin box", "tray"]
# move the clamp behind of the drill
robot.pick_and_place("medium clamp", "power drill", "behind")
# actually, I want it on the opposite side of the drill
robot.pick_and_place("medium clamp", "power drill", "front")
objects = ["chips can", "banana", "strawberry", "potted meat can", "pear", "tray"]
# put the red fruit left of the green one 
robot.pick_and_place("strawberry", "pear", "left")
""".strip()


prompt_pick_and_place_grounding = """
from robot_utils import pick_and_place
from camera_utils import find, scene_init

### start of trial
objects = scene_init()
# put the bottle to the left side.
bottle = find(objects, "bottle")[0]
pick_and_place(bottle, "left side")

### start of trial
objects = scene_init()
# move all the fruit to the bottom right corner.
fruits = find(objects, "fruit")
for fruit_instance in fruits:
    pick_and_place(fruit_instance, "bottom right corner")
# now put the small one in the right side.
small_fruit = find(fruits, "small fruit")[0]
pick_and_place(small_fruit, "right side")
# undo the last step.
pick_and_place(small_fruit, "bottom right corner")

### start of trial
objects = scene_init()
# put all cans in the tray.
cans = find(objects, "can")
for can_instance in cans:
    pick_and_place(can_instance, "tray")
""".strip()