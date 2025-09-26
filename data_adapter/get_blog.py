from pydantic import BaseModel

class BlogSchema(BaseModel):
    Result : str

class Blog_Extraction_Prompt:
    def __init__(self, url: str):
        self.prompt = f"""Go to {url} . This is a blog page. Extract all the blog text (as it is, without summarisation) and give it in a good markdown format."""