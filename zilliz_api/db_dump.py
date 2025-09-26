import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pymilvus import MilvusClient
from datetime import datetime

def dump_to_milvus(blog_title, blog_content, URL, company_name):
    load_dotenv()

    # ============== QWEN EMBEDDINGS ==============

    hf_client = InferenceClient(
            provider="auto",
            api_key=os.environ.get("HF_TOKEN"),
        )
    blog_title_embeddings   = hf_client.feature_extraction(blog_title,model="Qwen/Qwen3-Embedding-8B",).tolist()[0]
    blog_content_embeddings = hf_client.feature_extraction(blog_content,model="Qwen/Qwen3-Embedding-8B",).tolist()[0]

    # ============== ZILLIZ PIPELINE ==============

    milvus_client = MilvusClient(uri=os.environ.get("ZILLIZ_URI"), token=os.environ.get("ZILLIZ_TOKEN"))

    milvus_client.insert(os.environ.get("COLLECTION_NAME"), [{"title":blog_title,
                                            "title_embeddings":blog_title_embeddings, 
                                            "body":blog_content,
                                            "URL":URL,
                                            "body_embeddings":blog_content_embeddings,
                                            "timestamp":str(datetime.now()),
                                            "company_name":company_name
                                            }])

    # print(f"Dumped blog data for \033[1m{blog_title}\033[0m into Milvus successfully! ✅")