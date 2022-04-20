import language_tool_python
def language_Check(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    return (1 - len(matches)/len(text))
