import re

class CodeAnalyzer:
    def extract_elements(self, language, code):
        raise NotImplementedError("Subclasses should implement this method")

class PythonAnalyzer(CodeAnalyzer):
    def extract_elements(self, code):
        functions = re.findall(r'def\s+(\w+)\s*\(.*\):', code)
        classes = re.findall(r'class\s+(\w+)\s*\(.*\):', code)
        docstrings = re.findall(r'""".*?"""|\'\'\'.*?\'\'\'', code, re.DOTALL)
        comments = re.findall(r'#.*', code)
        return {
            "functions": functions,
            "classes": classes,
            "docstrings": docstrings,
            "comments": comments
        }

class JavaAnalyzer(CodeAnalyzer):
    def extract_elements(self, code):
        functions = re.findall(r'public\s+\w+\s+(\w+)\s*\(.*\)\s*{', code)
        classes = re.findall(r'public\s+class\s+(\w+)\s*{', code)
        comments = re.findall(r'//.*|/\*.*?\*/', code, re.DOTALL)
        return {
            "functions": functions,
            "classes": classes,
            "comments": comments
        }

class CppAnalyzer(CodeAnalyzer):
    def extract_elements(self, code):
        functions = re.findall(r'\w+\s+\w+\s+(\w+)\s*\(.*\)\s*{', code)
        classes = re.findall(r'class\s+(\w+)\s*{', code)
        comments = re.findall(r'//.*|/\*.*?\*/', code, re.DOTALL)
        return {
            "functions": functions,
            "classes": classes,
            "comments": comments
        }

class GoAnalyzer(CodeAnalyzer):
    def extract_elements(self, code):
        functions = re.findall(r'func\s+(\w+)\s*\(.*\)\s*{', code)
        comments = re.findall(r'//.*|/\*.*?\*/', code, re.DOTALL)
        return {
            "functions": functions,
            "comments": comments
        }

class JavaScriptAnalyzer(CodeAnalyzer):
    def extract_elements(self, code):
        functions = re.findall(r'function\s+(\w+)\s*\(.*\)\s*{', code)
        comments = re.findall(r'//.*|/\*.*?\*/', code, re.DOTALL)
        return {
            "functions": functions,
            "comments": comments
        }

class MultiLanguageAnalyzer:
    def __init__(self):
        self.analyzers = {
            'Python': PythonAnalyzer(),
            'Java': JavaAnalyzer(),
            'C++': CppAnalyzer(),
            'Go': GoAnalyzer(),
            'JavaScript': JavaScriptAnalyzer(),
        }

    def analyze(self, language, code):
        analyzer = self.analyzers.get(language)
        if analyzer is None:
            raise ValueError(f"No analyzer available for language: {language}")
        return analyzer.extract_elements(code)

# Example usage
if __name__ == "__main__":
    sample_code = """
    def hello_world():
        \"\"\"This function prints 'Hello, world!'\"\"\"
        print("Hello, world!")  # Print hello world
    """
    analyzer = MultiLanguageAnalyzer()
    elements = analyzer.analyze('Python', sample_code)
    print(elements)
