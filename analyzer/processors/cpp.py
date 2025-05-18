from pathlib import Path
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain.schema import Document
from ..utils import read_file_with_fallback


class CppProcessor:
    def __init__(self, config):
        self.config = config['cpp']
        self.general_config = config['general']

        self.splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.CPP,
            chunk_size=config['general']['chunk_size'],
            chunk_overlap=config['general']['chunk_overlap'],
            length_function=lambda x: len(x.split()),  # Более точный подсчет длины
            keep_separator=False
        )

    def process(self, project_root):
        files = self._find_cpp_files(project_root)
        return self._create_documents(files)

    def _find_cpp_files(self, project_root):
        files = {}
        for path in Path(project_root).rglob('*'):
            if self._should_ignore(path):
                continue
            if path.suffix in self.config['extensions']:
                try:
                    content = read_file_with_fallback(path)
                    print(path)
                    files[path] = content
                except Exception as e:
                    logging.error(f"Error reading {path}: {e}")
        return files

    def _should_ignore(self, path):
        if any(part in self.config['ignore_dirs'] for part in path.parts):
            return True
        if any(path.match(p) for p in self.config['ignore_files']):
            return True
        return False

    def _create_documents(self, files):
        docs = []
        for path, content in files.items():
            try:
                docs.extend(self.splitter.create_documents(
                    texts=[content],
                    metadatas=[{"source": str(path)}]
                ))
            except Exception as e:
                logging.error(f"Error processing {path}: {e}")
        return docs