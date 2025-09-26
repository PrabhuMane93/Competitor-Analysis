import asyncio
import json

from dotenv import load_dotenv
from browser_use import Agent, ChatGoogle, Browser
from pathlib import Path

from get_titles import TitleSchema, Title_Extraction_Prompt
from get_blog import BlogSchema, Blog_Extraction_Prompt
from milvus_connectors import dump_to_milvus, search_url_milvus

async def run_browser_agent(url: str, stage: str):
    load_dotenv()
    llm     = ChatGoogle(model='gemini-2.0-flash')
    browser = Browser(headless=False)

    if stage == "titles":
        task  = Title_Extraction_Prompt(url)
        agent = Agent(
            task=task.prompt,
            browser=browser,
            llm=llm,
            output_model_schema=TitleSchema
    )
    
    elif stage == "blog":
        task  = Blog_Extraction_Prompt(url)
        agent = Agent(
            task=task.prompt,
            browser=browser,
            llm=llm,
            output_model_schema=BlogSchema
        )

    history = await agent.run(max_steps=100)
    return history.final_result()

def scrape(url : str, company_name : str):
    result = asyncio.run(run_browser_agent(url = url, stage = "titles")) 
    scrapped_json = json.loads(result)
    scrapped_json = scrapped_json.get("Result", []) 

    # # create a folder 
    # Path(company_name).mkdir(exist_ok=True)

    # # Save only the list to blogs.json
    # out_path = Path(f"{company_name}/{company_name}.json")
    # with out_path.open("w", encoding="utf-8") as f:
    #     json.dump(scrapped_json, f, ensure_ascii=False, indent=2)

    print(f"Total of {len(scrapped_json)} blogs found for {company_name}.")

    # Scrape each blog
    for blog in scrapped_json:
        blog_title = blog["Title"]
        blog_url  =  blog["URL"]
        if search_url_milvus(blog_url):
            print(f"Blog already exists in Milvus: {blog_title} - {blog_url}")
            continue
        else:
            try:
                result = asyncio.run(run_browser_agent(url = blog_url, stage = "blog")) 
                scrapped_blog = json.loads(result)
                scrapped_blog = scrapped_blog.get("Result", []) 
                dump_to_milvus(blog_title, scrapped_blog, blog_url, company_name)
            except Exception as e:
                print(f"Error scraping blog {blog_title} - {blog_url}: {e}")
                continue

        # Save scrapped blogs 
        # out_path = Path(f"{company_name}/{blog_title}.json")
        # with out_path.open("w", encoding="utf-8") as f:
        #     json.dump(scrapped_blog, f, ensure_ascii=False, indent=2)