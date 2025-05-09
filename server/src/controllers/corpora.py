from models.corpora import CorporaModel
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

corpus_data = CorporaModel()

def get_corpuses_data(where_conditions=None):
    response = corpus_data.get_corpuses(where_conditions)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response

def get_corpus_data(corpusId):
    response = corpus_data.get_corpus(corpusId)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response

def create_corpus_data(corpus_data_input):
    response = corpus_data.create_corpus(corpus_data_input)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response

def update_corpus_data(corpus_data_input, corpusId):
    response = corpus_data.update_corpus(corpus_data_input, corpusId)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response

def delete_corpus_data(corpusId):
    response = corpus_data.delete_corpus(corpusId)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response