import asyncio
import os
from argparse import Action

from browser_use.agent.service import Agent
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr, BaseModel

# Model used to convert AI agent output into our check point/status points etc
class SiteValidationResultModel(BaseModel):
    home_page_load_status: str
    item_search_status: str
    item_select_status: str
    price_validation_status: int
    extracted_value: str


# Customise AI agent
controller = Controller(output_model=SiteValidationResultModel)

# Custom function/step
@controller.action('extract saving percentage value from site')
async def maximise_browser(browser : BrowserContext):
    page = await browser.get_current_page()
    current_url = page.url
    savings_percentage = page.locator("//span[contains(@class,'savingsPercentage')]").inner_text()
    print(current_url)
    return ActionResult(extracted_content = f"custom function values: /n{current_url} /n {savings_percentage}")



async def site_validation():
    os.environ["GEMINI_API_KEY"] = 'AIzaSyD98bAXNZp6Eh1lbaSiLV-9TiiPEjg5x6g'
    task = (
        'Important: I am an functional automation tester validating the tasks'
        'Open website https://www.amazon.in/'
        'Search watches for man in the search box'
        'scroll down until you find LOUIS DEVIN Silicone Strap Analog Wrist Watch for Men (Black/Blue/Red) | LD-BK054'
        'click LOUIS DEVIN Silicone Strap Analog Wrist Watch for Men (Black/Blue/Red) | LD-BK054'
        'Verify the price for LOUIS DEVIN Silicone Strap Analog Wrist Watch for Men (Black/Blue/Red) | LD-BK054 is ₹369'
        'extract saving percentage value from site'
    )
    api_key = os.environ["GEMINI_API_KEY"]

    # Enable when chatgpt ai model is available
    # llm = ChatOpenAI(model="gpt-4o", api_key=SecretStr(api_key))
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-pro-exp-02-05', api_key=SecretStr(api_key))

    # use_vision increase the accuracy of the AI model by taking screenshot
    agent = Agent(task = task, llm = llm, use_vision=True, controller=controller)
    history = await agent.run()
    history.save_to_file('agentResult.json')
    test_result = history.final_result()
    print(test_result)
    validated_result = SiteValidationResultModel.model_validate_json(test_result)

    assert validated_result.price_validation_status == 369

asyncio.run(site_validation())