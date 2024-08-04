from typing import Dict

class Page:
    def __init__(self, page_data:Dict):
        self.id = page_data.get("id")
        self.created_time = page_data.get("created_time")
        self.last_edited_time = page_data.get("last_edited_time")
        self.created_by = page_data.get("created_by", {}).get("id")
        self.url = page_data.get("url")
        self.public_url = page_data.get("public_url")
        
        self.properties = page_data.get("properties", {})

        try: self.title = self.properties.get('Name').get('title')[0].get('text').get('content')
        except: self.title = ''
        
        try: self.type = self.properties.get('Type').get('select').get('name')
        except: self.type = ''

        try: self.in_class = self.properties.get('Class').get('multi_select')[0].get('name')
        except: self.in_class = ""
        
        self.text = ""
        self.questions = ""

    def __repr__(self):
        return f"Page(id={self.id}) (title={self.title}) (type={self.type})"

    def set_text(self, text:str):
        self.text = text

    def set_questions(self, questions:str):
        self.questions = questions

def extract_pages(database:list[Dict]) -> list[Page]:
    pages = []

    for page_data in database:
        try: 
            page = Page(page_data)
            pages.append(page)
        except AttributeError:
            print(page_data)
            continue

    return pages