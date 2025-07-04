# Script DAT → Callbacks DAT
# Uses onCook only: pressing the Send pulse will cook the DAT and trigger the API call.
# System message is read from a Text DAT named 'system_message'.

def onSetupParameters(scriptOp):
    page = scriptOp.appendCustomPage('Settings')
    # OpenAI API key
    p_key = page.appendStr('Apikey', label='OpenAI API Key')
    p_key.default = ''
    # Model selector
    models = ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo']
    p_model_group = page.appendMenu('Model', label='Model')
    # p_model_group is a ParGroup; grab the actual par at index 0
    p_model = p_model_group[0]
    p_model.menuNames = models
    p_model.menuLabels = models
    p_model.default = models[0]
    # Pulse to trigger send
    page.appendPulse('Send', label='Send to GPT')
    return

def onCook(scriptOp):
    # only run when Send is pressed
    if not scriptOp.par.Send.eval():
        return

    # read API key
    api_key = scriptOp.par.Apikey.eval().strip()
    if not api_key:
        scriptOp.text = "Error: No API key provided"
        return

    # read model choice
    model = scriptOp.par.Model.eval()

    # read system message
    sys_dat = op('system_message')
    if not sys_dat:
        scriptOp.text = "Error: Text DAT named 'system_message' not found"
        return
    system_message = sys_dat.text

    # read input prompt
    inp = op('input')
    if not inp:
        scriptOp.text = "Error: Text DAT named 'input' not found"
        return
    user_prompt = inp.text

    # call OpenAI Chat API
    try:
        import requests
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_message},
                {'role': 'user',   'content': user_prompt}
            ]
        }
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        reply = r.json()['choices'][0]['message']['content']
    except Exception as e:
        reply = f"Error during API call: {e}"

    # write to output DAT
    out = op('output')
    if out:
        out.text = reply
    else:
        scriptOp.text = "Error: Text DAT named 'output' not found"
    return
