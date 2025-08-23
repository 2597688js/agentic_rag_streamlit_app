from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import os
import sys
from src.ocr_mistral import process_pdf, get_combined_markdown

# Set USER_AGENT to avoid warnings
os.environ['USER_AGENT'] = 'AgenticRAG/1.0 (https://github.com/your-repo)'

class DocumentProcessor:
    def __init__(self):
        try:
            from src.config import ConfigManager
            self.config = ConfigManager()._config
        except Exception as e:
            print(f"Failed to load config in document_processor.py: {e}, using defaults")
            self.config = {}

    def load_documents(self, sources: list):
        """
        Load documents from multiple sources:
        - Uploaded files (dict with 'type': 'file', 'name', 'content')
        - URLs (str starting with http/https)
        - Local file paths (str ending with .pdf/.docx/.txt)
        Returns a flat list of loaded documents.
        """
        import os
        import tempfile
        import base64
        from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, WebBaseLoader

        docs_list = []
        errors = []

        for source in sources:
            try:
                # ----------------- Uploaded files -----------------
                if isinstance(source, dict) and source.get('type') == 'file':
                    try:
                        file_content = source['content']  # bytes
                        file_name = source['name']
                        suffix = os.path.splitext(file_name)[1]

                        # Create temp file for loader
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(file_content)
                            tmp_path = tmp.name

                        # Choose loader based on file type
                        if suffix.lower() == '.pdf':
                            pdf_response = process_pdf(file_content, file_name) 
                            # Convert OCR response to LangChain Document objects with metadata
                            
                            # Extract markdown content from OCR response
                            markdown_content = get_combined_markdown(pdf_response)
                            
                            # Create a single document with the combined content
                            pdf_doc = Document(
                                page_content=markdown_content,
                                metadata={
                                    "source_type": "file",
                                    "source_name": file_name,
                                    "source": file_name,
                                    "file_type": "pdf",
                                    "processing_method": "ocr"
                                }
                            )
                            docs_list.append(pdf_doc)
                            print(f"✅ Loaded PDF file: {file_name}")
                            
                        elif suffix.lower() in ['.docx', '.doc']:
                            loader = Docx2txtLoader(tmp_path)
                            docs = loader.load()
                        elif suffix.lower() == '.txt':
                            loader = TextLoader(tmp_path)
                            docs = loader.load()
                        else:
                            raise ValueError(f"Unsupported file type: {suffix}")

                        # docs = loader.load()
                        if docs:
                            for d in docs:
                                d.metadata = dict(d.metadata or {})
                                d.metadata.update({
                                    "source_type": "file",
                                    "source_name": file_name,
                                    "source": file_name
                                })
                            docs_list.extend(docs)
                            print(f"✅ Loaded file: {file_name}")
                        else:
                            errors.append(f"No content in file: {file_name}")

                        os.unlink(tmp_path)
                    except Exception as e:
                        errors.append(f"Failed to load file {source.get('name')}: {str(e)}")
                        continue

                # ----------------- URLs -----------------
                elif isinstance(source, str) and source.startswith(("http://", "https://")):
                    try:
                        loader = WebBaseLoader(
                            source,
                            requests_kwargs={
                                "headers": {
                                    "User-Agent": os.environ.get('USER_AGENT', 'AgenticRAG/1.0')
                                }
                            }
                        )
                        docs = loader.load()
                        if docs:
                            for d in docs:
                                d.metadata = dict(d.metadata or {})
                                d.metadata.update({
                                    "source_type": "url",
                                    "source_name": source,
                                    "source": source
                                })
                            docs_list.extend(docs)
                            print(f"✅ Loaded URL: {source}")
                        else:
                            errors.append(f"No content in URL: {source}")
                    except Exception as e:
                        errors.append(f"Failed to load URL {source}: {str(e)}")
                        continue

                # ----------------- Local file paths -----------------
                elif isinstance(source, str) and os.path.exists(source):
                    try:
                        suffix = os.path.splitext(source)[1]
                        if suffix.lower() == '.pdf':
                            loader = PyPDFLoader(source)
                        elif suffix.lower() in ['.docx', '.doc']:
                            loader = Docx2txtLoader(source)
                        elif suffix.lower() == '.txt':
                            loader = TextLoader(source)
                        else:
                            raise ValueError(f"Unsupported file type: {suffix}")

                        docs = loader.load()
                        if docs:
                            for d in docs:
                                d.metadata = dict(d.metadata or {})
                                d.metadata.update({
                                    "source_type": "filepath",
                                    "source_name": os.path.basename(source),
                                    "source": source
                                })
                            docs_list.extend(docs)
                            print(f"✅ Loaded local file: {source}")
                        else:
                            errors.append(f"No content in file: {source}")
                    except Exception as e:
                        errors.append(f"Failed to load file {source}: {str(e)}")
                        continue

                else:
                    errors.append(f"Unsupported source format: {source}")

            except Exception as e:
                errors.append(f"Unexpected error with source {source}: {str(e)}")
                continue

        if errors:
            print(f"⚠️ {len(errors)} source(s) failed to load:")
            for e in errors:
                print(f"  - {e}")

        return docs_list
