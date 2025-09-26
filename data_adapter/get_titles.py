from pydantic import BaseModel
from typing import List

class BlogItem(BaseModel):
    Title  :  str  
    URL    :  str

class TitleSchema(BaseModel):
    Result : List[BlogItem]

class Title_Extraction_Prompt:
    def __init__(self, url: str):
        self.prompt = f"""
        1.) go to {url} . Turn off cookies if any pop-up appears.
        2.) If the website is not in english then find an option to select english. 
        3.) Go to navigation bar or dropdownmenu or sideways drawer, whichever is available.
        4.) Now, most probably you will find categories such as “about us”, “case studies”, “projects”, “blogs”, “services” … etc. According to best of your knowledge open page that most likely contains blogs.
        5.) Scroll down the entire page give me the titles and full URLs (not relative paths) for all blogs (not just the first four, but all blos) that are there on the webpage in the format below:
        {{"Result":
        [
            {{"Title" : “Full Title of first blog”,
            "URL"    : "Full http URL of first blog"}},
            {{"Title" : “Full Title of second blog”,
            "URL"    : "Full http URL of second blog"}},
            {{"Title" : “Full Title of third blog”,
            "URL"    : "Full http URL of third blog"}},
            {{"Title" : “Full Title of fourth blog”,
            "URL"    : "Full http URL of fourth blog"}},
            .
            .
            .
            .
            {{"Title" : “Full Title of last blog”,
            "URL"    : "Full http URL of last blog"}}
        ]
        }}
        """