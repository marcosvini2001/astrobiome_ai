from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 3
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR_NAME = "faiss_botany_minilm"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _knowledge_dir() -> Path:
    return _project_root() / "knowledge" / "botany_manuals"


def _vectorstore_dir() -> Path:
    return _project_root() / "knowledge" / ".vectorstore" / VECTORSTORE_DIR_NAME


def _format_source(metadata: dict[str, object]) -> str:
    source = metadata.get("source", "fonte desconhecida")
    source_path = Path(str(source))
    page = metadata.get("page")
    if page is not None:
        return f"{source_path.name} (pagina {int(page) + 1})"
    return source_path.name


def _format_retrieved_documents(documents: list[Document]) -> str:
    if not documents:
        return (
            "Nenhum trecho relevante encontrado na literatura botanica indexada. "
            "Prossiga com base no relatorio de telemetria e conhecimento geral."
        )

    sections: list[str] = []
    for index, document in enumerate(documents, start=1):
        source_label = _format_source(document.metadata)
        content = document.page_content.strip()
        sections.append(f"[Trecho {index} | Fonte: {source_label}]\n{content}")

    return "\n\n---\n\n".join(sections)


def _load_pdf_documents(knowledge_dir: Path) -> list[Document]:
    if not knowledge_dir.is_dir():
        raise FileNotFoundError(
            f"Diretorio de manuais botanicos nao encontrado: {knowledge_dir}"
        )

    pdf_files = list(knowledge_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(
            f"Nenhum PDF encontrado em {knowledge_dir}. "
            "Adicione artigos cientificos antes de consultar a literatura."
        )

    loader = PyPDFDirectoryLoader(str(knowledge_dir))
    return loader.load()


def _split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def _build_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def _build_vectorstore(knowledge_dir: Path, embeddings: Embeddings) -> FAISS:
    documents = _load_pdf_documents(knowledge_dir)
    chunks = _split_documents(documents)
    return FAISS.from_documents(chunks, embeddings)


def _save_vectorstore(vectorstore: FAISS, vectorstore_dir: Path) -> None:
    vectorstore_dir.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(vectorstore_dir))


def _load_vectorstore(vectorstore_dir: Path, embeddings: Embeddings) -> FAISS:
    return FAISS.load_local(
        str(vectorstore_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def _is_vectorstore_stale(vectorstore_dir: Path, knowledge_dir: Path) -> bool:
    if not vectorstore_dir.is_dir():
        return True

    index_file = vectorstore_dir / "index.faiss"
    if not index_file.exists():
        return True

    index_mtime = index_file.stat().st_mtime
    for pdf_file in knowledge_dir.glob("*.pdf"):
        if pdf_file.stat().st_mtime > index_mtime:
            return True

    return False


@lru_cache(maxsize=1)
def get_botany_retriever() -> VectorStoreRetriever:
    """Build or load the FAISS retriever for botany manuals (cached per process)."""
    knowledge_dir = _knowledge_dir()
    vectorstore_dir = _vectorstore_dir()
    embeddings = _build_embeddings()

    if _is_vectorstore_stale(vectorstore_dir, knowledge_dir):
        vectorstore = _build_vectorstore(knowledge_dir, embeddings)
        _save_vectorstore(vectorstore, vectorstore_dir)
    else:
        vectorstore = _load_vectorstore(vectorstore_dir, embeddings)

    return vectorstore.as_retriever(search_kwargs={"k": TOP_K})


class BotanyLiteratureSearchInput(BaseModel):
    """Input schema for the botany literature RAG tool."""

    query: str = Field(
        ...,
        description=(
            "Consulta em linguagem natural sobre diagnostico botanico, tratamentos "
            "hidroponicos, nutricao vegetal, estresse foliar ou cultivo em ambientes fechados."
        ),
    )


class BotanyLiteratureSearchTool(BaseTool):
    """CrewAI tool that retrieves relevant excerpts from indexed botany PDFs."""

    name: str = "botany_literature_search"
    description: str = (
        "Consulta a literatura cientifica indexada em knowledge/botany_manuals/ "
        "para recuperar trechos relevantes sobre diagnostico botanico, tratamentos "
        "hidroponicos, nutricao vegetal, estresse hidrico/foliar e cultivo em "
        "ambientes controlados. Use esta ferramenta antes de prescrever tratamentos."
    )
    args_schema: Type[BaseModel] = BotanyLiteratureSearchInput

    def _run(self, query: str) -> str:
        try:
            retriever = get_botany_retriever()
            documents = retriever.invoke(query)
            return _format_retrieved_documents(documents)
        except FileNotFoundError as error:
            return str(error)
        except Exception as error:
            return (
                "Erro ao consultar a literatura botanica indexada: "
                f"{error}. Prossiga com cautela usando o relatorio de telemetria."
            )
