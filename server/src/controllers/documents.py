from models.documents import DocumentsModel

documents_data = DocumentsModel()

def get_documents_data():
    documents = documents_data.get_documents()
    result = [dict(document) for document in documents]
    return result

def get_document_data(document_id):
    document = documents_data.get_document(document_id)
    if document:
        return dict(document)
    return {"error": "Document not found"}

def update_document_data(document_id, updates):
    success = documents_data.update_document(document_id, updates)
    if success:
        return {"message": "Document updated successfully"}
    return {"error": "Document not found"}

def delete_document_data(document_id):
    success = documents_data.delete_document(document_id)
    if success:
        return {"message": "Document deleted successfully"}
    return {"error": "Document not found"}


def create_document_data(document_data):
    document_id = documents_data.create_document(document_data)
    if document_id:
        return {"message": "Document created successfully", "documentId": document_id}
    return {"error": "Failed to create document"}