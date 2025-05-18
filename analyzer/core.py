import logging
from pathlib import Path

from chromadb import Settings

from .processors.cpp import CppProcessor
from .processors.cmake import CMakeProcessor
from .utils import configure_logger
from .config import load_config

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"


class CodeAnalyzer:
    def __init__(self, project_path: str):
        self.project_root = Path(project_path).resolve()
        self.config = load_config(self.project_root)
        configure_logger(self.config['logging'])
        self.vector_db = self._init_vector_db()

    def _init_vector_db(self):
        embeddings = OllamaEmbeddings(
            model=self.config['general']['model']        )

        return Chroma(
            persist_directory=self.config['general']['db_path'],
            embedding_function=embeddings,
            client_settings=Settings(
                persist_directory=self.config['general']['db_path']
            )
        )

    def analyze_project(self):
        processor = CppProcessor(self.config)
        docs = processor.process(self.project_root)

        if self.config['cmake']['analyze_cmake']:
            cmake_docs = CMakeProcessor(self.config).process(self.project_root)
            docs.extend(cmake_docs)

        # Разбиваем документы на батчи
        batch_size = self.config['general']['max_batch_size']
        logging.info(f"documents count: {len(docs)}")
        # Можно регулировать в зависимости от размера документов
        for batch_num, i in enumerate(range(0, len(docs), batch_size), 1):
            batch = docs[i:i + batch_size]
            try:
                self.vector_db.add_documents(batch)
                logging.info(f"Added batch {i // batch_size + 1} with {len(batch)} documents")
            except Exception as e:
                logging.error(f"Error adding batch {i // batch_size + 1}: {str(e)}")

        logging.info("All documents added successfully")

    def query(self, question: str) -> dict:
        llm = ChatOllama(
            model=self.config['general']['model'],
            temperature=0.8,
            num_ctx=8192        )

        prompt = ChatPromptTemplate.from_template(
            "Context:\n{context}\n\nQuery: {question}"
        )

        chain = (
                RunnableParallel({
                    "context": self.vector_db.as_retriever(search_kwargs={"k": 5}),
                    "question": RunnablePassthrough()
                })
                | prompt
                | llm
                | StrOutputParser()
        )

        return {'result':chain.invoke(question)}