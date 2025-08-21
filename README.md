# 🤖 Agentic RAG Application

A sophisticated **Retrieval-Augmented Generation (RAG)** application built with Streamlit that combines document processing, intelligent question answering, and workflow visualization. This application uses advanced AI techniques to provide context-aware responses based on uploaded documents and web content.

## 🚀 Features

### **Core Functionality**
- **📚 Document Processing**: Support for PDF, DOCX, and TXT files
- **🌐 URL Processing**: Extract and process content from web URLs
- **🧠 Intelligent RAG**: Advanced retrieval and generation pipeline
- **💾 Memory Retention**: Conversation history and context preservation
- **📊 Analytics Dashboard**: Usage statistics and performance metrics
- **🔄 Workflow Visualization**: Interactive graph representation of the RAG process

### **Advanced Capabilities**
- **Agentic Workflow**: Multi-node decision-making process
- **Document Grading**: Automatic relevance assessment
- **Question Rewriting**: Intelligent query refinement
- **Fallback Mechanisms**: Graceful degradation when advanced features fail
- **Real-time Streaming**: Word-by-word response generation

## 🏗️ Architecture

### **System Components**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   Document      │    │   Document      │
│   Processor     │───▶│   Splitter      │───▶│   Retriever     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAG Workflow  │◀───│   Graph Nodes   │◀───│   MixRAG Graph  │
│   Engine        │    │   (Decision     │    │   (Orchestrator)│
└─────────────────┘    │   Logic)        │    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Streamlit UI  │
                       │   (User Interface)│
                       └─────────────────┘
```

### **Workflow Nodes**
1. **Generate Query or Respond**: Determines if document retrieval is needed
2. **Retrieve Documents**: Fetches relevant document chunks
3. **Grade Documents**: Evaluates relevance of retrieved content
4. **Rewrite Question**: Refines queries for better results
5. **Generate Answer**: Produces final response based on context

## 🛠️ Technology Stack

### **Backend**
- **Python 3.11**: Core programming language
- **LangChain**: LLM framework and tools
- **LangGraph**: Workflow orchestration
- **OpenAI**: GPT models for text generation
- **Pydantic**: Data validation and serialization

### **Frontend**
- **Streamlit**: Web application framework
- **Graphviz**: Workflow visualization
- **BeautifulSoup4**: Web scraping capabilities

### **Document Processing**
- **PyPDF**: PDF text extraction
- **python-docx**: DOCX file processing
- **Text Splitters**: Intelligent document chunking

## 📋 Prerequisites

### **Required**
- **Python 3.11+**
- **Docker** (for containerized deployment)
- **OpenAI API Key** (required for AI functionality)

### **Optional**
- **Git** (for version control)
- **Virtual Environment** (recommended for development)

## 🚀 Installation & Setup

### **Option 1: Docker (Recommended)**

#### **Quick Start**
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd agentic_rag_app

# 2. Create environment file
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env

# 3. Build and run with Docker
docker build -t agentic_rag_app .
docker run -p 8505:8505 --env-file .env agentic_rag_app
```

#### **Access the Application**
Open your browser and navigate to: `http://localhost:8505`

### **Option 2: Local Development**

#### **Environment Setup**
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd agentic_rag_app

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set environment variable
export OPENAI_API_KEY="your_actual_api_key_here"
# On Windows:
set OPENAI_API_KEY=your_actual_api_key_here

# 6. Run the application
streamlit run st_app.py --server.port 8505
```

## 🔧 Configuration

### **Environment Variables**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes | - |
| `LOG_LEVEL` | Application logging level | ❌ No | `INFO` |

### **Configuration File**
The application uses `src/config/config.yaml` for:
- **Model Configuration**: OpenAI model selection and parameters
- **Document Processing**: Chunk size and overlap settings
- **RAG Parameters**: Retrieval thresholds and context limits
- **Prompt Templates**: Customizable AI prompts

## 📖 Usage Guide

### **1. Getting Started**
1. **Upload Documents**: Use the sidebar to upload PDF, DOCX, or TXT files
2. **Add URLs**: Paste web URLs (comma-separated) for web content
3. **Build Knowledge Base**: Click "🔨 Build Knowledge Base" to process sources
4. **Start Chatting**: Begin asking questions in the chat interface

### **2. Document Upload**
- **Supported Formats**: PDF, DOCX, TXT
- **File Size**: Recommended under 50MB per file
- **Processing**: Automatic text extraction and chunking

### **3. URL Processing**
- **Format**: `https://example.com, https://another-site.com`
- **Content**: Automatic web scraping and text extraction
- **Limitations**: Some sites may block automated access

### **4. Asking Questions**
- **Natural Language**: Ask questions in plain English
- **Context Awareness**: The AI considers uploaded documents
- **Follow-up**: Reference previous conversation context

### **5. Understanding Responses**
- **Source Citations**: View which documents informed the answer
- **Confidence Levels**: Assess answer reliability
- **Fallback Information**: See when simple RAG was used instead of advanced workflow

## 🔍 Troubleshooting

### **Common Issues**

#### **1. "OPENAI_API_KEY environment variable is required"**
```bash
# Solution: Set your API key
export OPENAI_API_KEY="your_key_here"
# Or create .env file
echo "OPENAI_API_KEY=your_key_here" > .env
```

#### **2. "Connection refused" error**
```bash
# Check if container is running
docker ps

# View container logs
docker logs <container_id>

# Ensure port 8505 is available
netstat -an | grep 8505
```

#### **3. "Failed to load config" error**
```bash
# Verify config file exists
ls -la src/config/config.yaml

# Check file permissions
chmod 644 src/config/config.yaml
```

#### **4. Document processing fails**
- **File Format**: Ensure file is PDF, DOCX, or TXT
- **File Size**: Check if file is too large
- **File Corruption**: Verify file isn't corrupted
- **Permissions**: Ensure read access to file

### **Debug Commands**
```bash
# Check container status
docker ps -a

# View container logs
docker logs <container_id>

# Access container shell
docker exec -it <container_id> bash

# Check environment variables
docker exec <container_id> env
```

## 📊 Performance & Scaling

### **Resource Requirements**
- **Memory**: 500MB - 2GB (depending on document size)
- **CPU**: 1-2 cores for typical usage
- **Storage**: 100MB - 1GB (depending on document volume)
- **Network**: Stable internet connection for OpenAI API calls

### **Optimization Tips**
- **Document Chunking**: Optimal chunk size is 1000 characters
- **Batch Processing**: Process multiple documents together
- **Caching**: Reuse knowledge base for multiple questions
- **Model Selection**: Use appropriate OpenAI model for your use case

## 🔒 Security Considerations

### **Data Privacy**
- **Local Processing**: Documents are processed locally
- **API Calls**: Only question content is sent to OpenAI
- **No Storage**: Documents are not permanently stored
- **Session-based**: Data exists only during active session

### **Best Practices**
- **API Key Security**: Never commit API keys to version control
- **Document Sensitivity**: Avoid uploading highly sensitive documents
- **Network Security**: Use HTTPS in production environments
- **Access Control**: Implement user authentication if needed

## 🧪 Testing

### **Running Tests**
```bash
# Execute test script
python app_test.py

# Test specific functionality
python -m pytest tests/ -v
```

### **Test Coverage**
- **Document Processing**: File upload and text extraction
- **RAG Workflow**: End-to-end question answering
- **Error Handling**: Graceful failure scenarios
- **Performance**: Response time and resource usage

## 📈 Monitoring & Analytics

### **Built-in Analytics**
- **Conversation Stats**: Message counts and types
- **Performance Metrics**: Response times and success rates
- **Usage Patterns**: Document types and question frequency
- **Error Tracking**: Failed operations and error rates

### **Custom Monitoring**
```bash
# View application logs
docker logs -f <container_id>

# Monitor resource usage
docker stats <container_id>

# Check health status
curl http://localhost:8505/_stcore/health
```

## 🚀 Deployment

### **Production Considerations**
- **Environment Variables**: Secure API key management
- **Resource Limits**: Set appropriate Docker resource constraints
- **Logging**: Configure centralized logging
- **Monitoring**: Implement health checks and alerting
- **Backup**: Regular configuration and data backups

### **Docker Compose (Optional)**
```yaml
version: '3.8'
services:
  agentic-rag:
    build: .
    ports:
      - "8505:8505"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
```

## 🤝 Contributing

### **Development Setup**
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** and test thoroughly
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**

### **Code Standards**
- **Python**: Follow PEP 8 style guidelines
- **Documentation**: Include docstrings for all functions
- **Testing**: Add tests for new functionality
- **Type Hints**: Use Python type annotations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI**: For providing the GPT models and API
- **LangChain**: For the excellent LLM framework
- **Streamlit**: For the intuitive web application framework
- **Community**: For contributions and feedback

## 📞 Support

### **Getting Help**
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check this README and inline code comments
- **Community**: Join relevant AI/ML communities for support

### **Contact Information**
- **Repository**: [GitHub Repository URL]
- **Issues**: [GitHub Issues Page]
- **Email**: [Your Contact Email]

---

**Made with ❤️ for the AI/ML community**

*Last updated: [Current Date]*
