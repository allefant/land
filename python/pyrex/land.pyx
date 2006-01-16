class LandException(Exception):
    def __init__(self, text):
        self.text = text
    def __str__(self):
        return self.text

def version():
    return (0, 0, 0, "SVN", "0.0.0 (SVN Revision 41)")
