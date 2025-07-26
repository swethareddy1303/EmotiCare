import os
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline

def load_rag_chain():
    # ✅ Step 1: Check file path
    print("📁 Current Directory:", os.getcwd())
    print("📄 File Exists?", os.path.exists("data/mental_health_tips.pdf"))

    # ✅ Step 2: Load PDF
    loader = PyPDFLoader("data/mental_health_tips.pdf")
    docs = loader.load()

    # ✅ Step 3: Split content into chunks
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    # ✅ Step 4: Create embeddings & FAISS vector DB
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db = FAISS.from_documents(split_docs, embedding=embeddings)
    retriever = vector_db.as_retriever()

    # ✅ Step 5: Load FLAN-T5 model safely (no meta tensors)
    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    local_pipeline = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=512
    )

    # ✅ Step 6: Wrap in LangChain LLM wrapper
    llm = HuggingFacePipeline(pipeline=local_pipeline)

    # ✅ Step 7: Create RAG chain
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa_chain
