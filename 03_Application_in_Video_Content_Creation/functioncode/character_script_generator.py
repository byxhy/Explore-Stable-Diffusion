import os, shutil
from typing import List

import chatgpt
from freepd import MusicCategory

def clear_folder(path_to_folder):
    for filename in os.listdir(path_to_folder):
        file_path = os.path.join(path_to_folder, filename)
        try:
            # 如果是文件或者链接则删除
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # 如果是文件夹则递归删除
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def generate_script(characters: List[dict] | None, prompt) -> dict:
    """Uses AI to generate a script matching the prompt.
    
    If characters are passed in, the resulting dialog is constrained to those characters.
    Otherwise, it prompts the user to select the appropriate characters unless full_auto is specified."""

    clear_folder('./tmp/')

    # keep generating scripts until user approves
    approved = False
    while not approved:
        script = generate_script_draft(prompt, characters, 2048, 20)
        # TODO: show the image_prompt in the validation
        print("Style: ", script.get('global_image_style', '(no global style)'))
        print("\nScript:\n", '\n'.join([f'{line["character"]}: ({line.get("image_prompt", "")}) {line["speech"]}' for line in script['lines']]))
        if(True):
            validated = None
            while validated not in ["y", "n", "q"]:
                validated = input("Do you approve this script? (y/n/q): ").lower()
                if validated == "y": approved = True
                elif validated == "n": approved = False
                elif validated == "q": exit()
                else: print("Unrecognized input. Try again.")
        else:
            break
    return script

def generate_script_draft(
        prompt: str,
        characters: List[dict],
        max_tokens: int,
        max_lines: int,
        temperature: float=0.5,
        full_auto:bool=False,
        high_quality_audio:bool=False
        ) -> dict:

    print("Generating script draft...")

    def character_string(name, voice) -> str:
        model_token = ("'" + voice['model_token'] + "'") if 'model_token' in voice else 'n/a'
        return f"- {name} (voice_token = {model_token})"

    available_characters_str = "\n".join(character_string(name, voice) for name, voice in characters.items())

    chatgpt_prompt = f"""
    Write a script for a funny YouTube Short in which {prompt}.
    No more than {max_lines} lines of dialog.
    Your output should be TOML, with the following values. Values are required by default.

    title (title of the video)
    description (youtube description for the video)
    global_image_style (the visual style for the AI-generated images in the video)
    bgm_category (genre of background music. Available categories are {", ".join(MusicCategory.values())})
    characters (list of characters with the following attributes)
    \t- name
    \t- default_image_prompt (default visual prompt for the AI image generator)
    \t- voice_token (provided for you)
    lines (list of each line of dialog with the following attributes)
    \t- character (the name of the character talking)
    \t- speech (the words the character is saying - no asterisks or parentheticals)
    \t- image_prompt (prompt for the AI image generator. Gets combined with global_image_style)

    Image prompts should only depict one character at a time, to make it easier for the AI image generator.

    Example:
    title = "Mario slaps Luigi with a breadstick"
    global_style = "photograph, in a living room from the sitcom how I met your mother (1993)"

    [[characters]]
    name = "Mario"
    default_image_prompt = "Mario with red cap and mustache"
    voice_token="TM:c7j599fz0pbg"

    ... more characters.

    [[lines]]
    character="Mario"
    speech="Hey Luigi, think fast!"
    image_prompt="close up photo of Mario with red cap and mustache, swinging breadstick aggressively with evil smirk"

    ... more lines.
    
    The characters at your disposal are:
    {available_characters_str}
    
    Do not use any other characters, including narrators.
    Filter out innappropriate, irrelelvant, or duplicate characters.
    Make sure all images are appropriate.
    Do not output anything after the TOML."""

    return chatgpt.generate_script(chatgpt_prompt, temperature=temperature, max_tokens=max_tokens)