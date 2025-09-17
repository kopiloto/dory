# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-17

### Initial Release

First public release of Dory - AI Memory & Conversation Management Library.

### Features

#### Messages Service

- **Conversation Management**: Automatic conversation reuse within 2-week window
- **Message Persistence**: Store user messages and AI responses with full async support
- **LangChain/LangGraph Integration**: Export chat history in compatible format
- **MongoDB Adapter**: Production-ready MongoDB integration with proper indexing
- **In-Memory Adapter**: For testing and development
- **Type Safety**: Full type hints and Pydantic models

#### Embeddings Service (NEW)

- **Memory Storage**: Store and retrieve contextual memories with LLM processing
- **Vector Search**: Semantic similarity search for relevant information
- **Raw Embeddings**: Store unprocessed content for retrieval tasks
- **Multiple Backends**:
  - Chroma (local vector store)
  - MongoDB Atlas (with vector search)
  - In-memory (for testing)
- **Powered by Mem0**: Built on top of the robust Mem0 library
- **OpenAI Integration**: Default embedding provider with configurable options

### Acknowledgments

- Built on top of [Mem0](https://github.com/mem0ai/mem0) for embeddings

---

This is the first public release. We welcome feedback and contributions!

[0.1.0]: https://github.com/kopiloto/dory/releases/tag/v0.1.0
