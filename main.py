import os
import re
from langchain_community.chat_models import ChatOpenAI
from langchain_community.agent_toolkits import load_tools
from langchain.agents import initialize
from langchain_community.tools import AIPluginTool
import json

os.environ["OPENAI_API_KEY"] = ""

tool = AIPluginTool.from_plugin_url("https://video-ai.invideo.io/.well-known/ai-plugin.json")

llm = ChatOpenAI(temperature=0.15)
tools = load_tools.load_tools(["requests_all"])
tools += [tool]

def extract_video_url(data):
    data_str = str(data)
    match = re.search(r'"video_url":\s*["\']([^"\']+)["\']', data_str)
    return match.group(1) if match else None

agent_chain = initialize.initialize_agent(
    tools, llm, verbose=True
)

# Define your video brief
video_brief = {
    "brief": "",
    "settings": "",
    "title": "",
    "description": "",
    "platforms": [""],
    "audiences": [""],
    "length_in_minutes": 0.5
}


video_brief_json = json.dumps(video_brief)
print("video brief JSON:", video_brief_json)
output = agent_chain(video_brief_json)
video_url = extract_video_url(output)

import invideo as InVideo
InVideo.login()
InVideo.create_video(video_url)
