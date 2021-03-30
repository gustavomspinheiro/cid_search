class Message():
    def __init__(self, text: str, type = None):
        self.text = text
        self.type = None

    def error(self):
        self.type = "error"
        return self

    def alert(self):
        self.type = "alert"
        return self
    
    def info(self):
        self.type = "info"
        return self
    
    def success(self):
        self.type = "success"
        return self

    def render(self):
        return f"<p class='message button button_{self.type}'>{self.text}</p>"
    

    

    

