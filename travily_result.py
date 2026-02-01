from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
load_dotenv()
tool = TavilySearchResults(max_results=2)
results = tool.invoke({"query": 'ChatGPT version releases and updates from 2022 to 2026'})
results
for r in results:
    print(r['content'])