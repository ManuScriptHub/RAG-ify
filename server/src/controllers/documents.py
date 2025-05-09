from models.documents import DocumentsModel
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

documents_data = DocumentsModel()

def get_documents_data(where_conditions=None):
    response = documents_data.get_documents(where_conditions)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response

def get_document_data(document_id):
    document = documents_data.get_document(document_id)
    
    if "error" in document:
        status_code = document.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=document["error"])
    
    if not document or not document.get("results"):
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
    
    # Ensure response has a "results" key with a list value
    if "results" in document and not isinstance(document["results"], list):
        document["results"] = [document["results"]] if document["results"] is not None else []
    
    return document

def update_document_data(document_data_input, docId):
    updated_document = documents_data.update_document(docId, document_data_input)
    
    if "error" in updated_document:
        status_code = updated_document.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=updated_document["error"])
    
    if not updated_document or not updated_document.get("results"):
        raise HTTPException(status_code=404, detail=f"Document with ID {docId} not found")
    
    # Ensure response has a "results" key with a list value
    if "results" in updated_document and not isinstance(updated_document["results"], list):
        updated_document["results"] = [updated_document["results"]] if updated_document["results"] is not None else []
    
    return updated_document

def delete_document_data(document_id):
    response = documents_data.delete_document(document_id)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    if not response or not response.get("results"):
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response

def create_document_data(document_input_data):
    response = documents_data.create_document(document_input_data)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    if not response or not response.get("results"):
        raise HTTPException(status_code=500, detail="Failed to create document")
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response