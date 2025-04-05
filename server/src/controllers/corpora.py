from models.corpora import CorporaModel

corpus_data = CorporaModel()

def get_corpuses_data():
    corpuses = corpus_data.get_corpuses()
    result = [dict(corpus) for corpus in corpuses]
    return result

def get_corpus_data(corpus_id):
    corpus = corpus_data.get_corpus(corpus_id)
    if corpus:
        return dict(corpus)  
    return None

def create_corpus_data(user_id, corpus_key):
    return corpus_data.create_corpus(user_id, corpus_key)

def update_corpus_data(user_id, corpus_key):
    return corpus_data.update_corpus(user_id, corpus_key)

def delete_corpus_data(corpus_id):
    return corpus_data.delete_corpus(corpus_id)