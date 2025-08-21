from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import os
import sys

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
                            loader = PyPDFLoader(tmp_path)
                        elif suffix.lower() in ['.docx', '.doc']:
                            loader = Docx2txtLoader(tmp_path)
                        elif suffix.lower() == '.txt':
                            loader = TextLoader(tmp_path)
                        else:
                            raise ValueError(f"Unsupported file type: {suffix}")

                        docs = loader.load()
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


    # def load_documents(self, sources: List[str | dict]):
    #     docs_list = []  # collect all documents in one flat list
    #     errors = []  # collect any loading errors
        
    #     for source in sources:
    #         try:
    #             # Handle file content objects (from Streamlit or API)
    #             if isinstance(source, dict) and source.get('type') == 'file':
    #                 try:
    #                     import tempfile
                        
    #                     file_content = source['content']
    #                     file_name = source['name']
                        
    #                     # Handle both base64 and binary content
    #                     if isinstance(file_content, str):
    #                         # Base64 encoded content (from Streamlit)
    #                         import base64
    #                         file_content = base64.b64decode(file_content)
    #                     elif isinstance(file_content, bytes):
    #                         # Binary content (from API upload)
    #                         pass
    #                     else:
    #                         raise ValueError(f"Unsupported content type: {type(file_content)}")
                        
    #                     # Create temporary file for processing
    #                     suffix = os.path.splitext(file_name)[1]
    #                     with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    #                         tmp.write(file_content)
    #                         tmp_path = tmp.name
                        
    #                     # Load based on file type
    #                     if suffix.lower() == '.pdf':
    #                         loader = PyPDFLoader(tmp_path)
    #                     elif suffix.lower() in ['.docx', '.doc']:
    #                         loader = Docx2txtLoader(tmp_path)
    #                     elif suffix.lower() == '.txt':
    #                         loader = TextLoader(tmp_path)
    #                     else:
    #                         raise ValueError(f"Unsupported file type: {suffix}")
                        
    #                     docs = loader.load()
    #                     if docs:
    #                         # Normalize metadata to keep original filename as source
    #                         for d in docs:
    #                             d.metadata = dict(d.metadata or {})
    #                             d.metadata["source_type"] = "file"
    #                             d.metadata["source_name"] = file_name
    #                             d.metadata["source"] = file_name
    #                         docs_list.extend(docs)
    #                         print(f"✅ Successfully loaded file: {file_name}")
    #                     else:
    #                         errors.append(f"No content extracted from file: {file_name}")
                        
    #                     # Clean up temp file
    #                     os.unlink(tmp_path)
                        
    #                 except Exception as file_error:
    #                     errors.append(f"Failed to load file {source.get('name', 'unknown')}: {str(file_error)}")
    #                     continue
                
    #             # Handle URLs
    #             elif isinstance(source, str) and (source.startswith("http://") or source.startswith("https://")):
    #                 try:
    #                     # Create WebBaseLoader with custom headers
    #                     loader = WebBaseLoader(
    #                         source,
    #                         requests_kwargs={
    #                             "headers": {
    #                                 "User-Agent": os.environ.get('USER_AGENT', 'AgenticRAG/1.0'),
    #                                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    #                                 "Accept-Language": "en-US,en;q=0.5",
    #                                 "Accept-Encoding": "gzip, deflate",
    #                                 "Connection": "keep-alive",
    #                             }
    #                         }
    #                     )
    #                     docs = loader.load()
    #                     if docs:
    #                         # Normalize metadata to keep URL as source
    #                         for d in docs:
    #                             d.metadata = dict(d.metadata or {})
    #                             d.metadata["source_type"] = "url"
    #                             d.metadata["source_name"] = source
    #                             d.metadata["source"] = source
    #                         docs_list.extend(docs)
    #                         print(f"✅ Successfully loaded URL: {source}")
    #                     else:
    #                         errors.append(f"No content extracted from URL: {source}")
    #                 except Exception as url_error:
    #                     errors.append(f"Failed to load URL {source}: {str(url_error)}")
    #                     continue
                        
    #             # Handle file paths (for backward compatibility)
    #             elif isinstance(source, str) and (source.endswith(".pdf") or source.endswith(".docx") or source.endswith(".doc") or source.endswith(".txt")):
    #                 # Check if file exists before trying to load
    #                 if not os.path.exists(source):
    #                     raise FileNotFoundError(f"File not found: {source}")
                    
    #                 # Load based on file type
    #                 if source.endswith(".pdf"):
    #                     loader = PyPDFLoader(source)
    #                 elif source.endswith(".docx") or source.endswith(".doc"):
    #                     loader = Docx2txtLoader(source)
    #                 elif source.endswith(".txt"):
    #                     loader = TextLoader(source)
                    
    #                 docs = loader.load()
    #                 if docs:
    #                     # Normalize metadata to keep original file path/name as source
    #                     for d in docs:
    #                         d.metadata = dict(d.metadata or {})
    #                         d.metadata["source_type"] = "filepath"
    #                         d.metadata["source_name"] = os.path.basename(source)
    #                         d.metadata["source"] = source
    #                     docs_list.extend(docs)
    #                     print(f"✅ Successfully loaded file: {source}")
    #                 else:
    #                     errors.append(f"No content extracted from file: {source}")
                        
    #             else:
    #                 raise ValueError(f"Unsupported source format: {source}")
                    
    #         except Exception as e:
    #             error_msg = f"Failed to load {source}: {str(e)}"
    #             errors.append(error_msg)
    #             continue
        
    #     # If we have errors, log them but continue with what we could load
    #     if errors:
    #         print(f"Warning: {len(errors)} source(s) failed to load, but continuing with {len(docs_list)} successful documents")
    #         for error in errors:
    #             print(f"  - {error}")
        
    #     return docs_list

