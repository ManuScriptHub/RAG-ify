from core.db import settings
import logging
import psycopg2
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DocumentsModel:
    def get_documents(self, where_conditions=None):
        conn = settings.get_db_connection()  
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            cur = conn.cursor()
            
            query = 'SELECT * FROM "Documents"'
            params = []
            
            # Add WHERE clause if conditions are provided
            if where_conditions:
                if not isinstance(where_conditions, dict):
                    logger.error(f"Invalid where_conditions format: {where_conditions}")
                    return {"error": "Where conditions must be a dictionary", "status_code": 400}
                
                try:
                    where_clauses = []
                    for key, value in where_conditions.items():
                        # Check if this is a JSON path query (key contains '.')
                        if '.' in key:
                            parts = key.split('.', 1)
                            column_name = parts[0]
                            json_path = parts[1]
                            
                            # Ensure the column name is valid to prevent SQL injection
                            if column_name in ["tags", "rawText"]:
                                # Handle different JSON query operations
                                if key.endswith('[]') and isinstance(value, str):
                                    # Array contains value (for arrays of strings)
                                    # Remove the [] suffix from the key
                                    json_path = json_path[:-2]
                                    where_clauses.append(f'"{column_name}" @> %s::jsonb')
                                    # Create a JSON array with the value
                                    json_value = f'{{"{ json_path }": ["{value}"]}}'
                                    params.append(json_value)
                                elif isinstance(value, dict) and '_op' in value:
                                    # Special operations
                                    op = value['_op']
                                    val = value['value']
                                    
                                    if op == 'contains':
                                        # Text contains operation
                                        where_clauses.append(f'"{column_name}"->>\'{json_path}\' ILIKE %s')
                                        params.append(f'%{val}%')
                                    elif op == 'startswith':
                                        where_clauses.append(f'"{column_name}"->>\'{json_path}\' ILIKE %s')
                                        params.append(f'{val}%')
                                    elif op == 'endswith':
                                        where_clauses.append(f'"{column_name}"->>\'{json_path}\' ILIKE %s')
                                        params.append(f'%{val}')
                                    elif op == 'gt':
                                        where_clauses.append(f'CAST("{column_name}"->>\'{json_path}\' AS NUMERIC) > %s')
                                        params.append(val)
                                    elif op == 'lt':
                                        where_clauses.append(f'CAST("{column_name}"->>\'{json_path}\' AS NUMERIC) < %s')
                                        params.append(val)
                                    else:
                                        logger.warning(f"Ignoring unsupported JSON operation: {op}")
                                else:
                                    # For string values in JSON
                                    where_clauses.append(f'"{column_name}"->>\'{json_path}\' = %s')
                                    params.append(value)
                            else:
                                logger.warning(f"Ignoring invalid JSON column name: {column_name}")
                        else:
                            # Regular column query
                            if key in ["docId", "documentId", "userId", "corpusId", "docType", "docName", "sourceUrl"]:
                                where_clauses.append(f'"{key}" = %s')
                                params.append(value)
                            else:
                                logger.warning(f"Ignoring invalid column name: {key}")
                    
                    if where_clauses:
                        query += " WHERE " + " AND ".join(where_clauses)
                except Exception as e:
                    logger.error(f"Error processing where conditions: {e}")
                    return {"error": f"Invalid where conditions: {str(e)}", "status_code": 400}
            
            query += ";"
            logger.info(f"Executing query: {query} with params: {params}")
            
            cur.execute(query, params)
            result = cur.fetchall()
            logger.info(f"get_documents result: {len(result)} records")
            
            # Convert result to list of dictionaries
            formatted_result = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(cur.description):
                    row_dict[col.name] = row[i]
                formatted_result.append(row_dict)
                
            return {"results": formatted_result}
            
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in get_documents: {e}")
            return {"error": "Database connection error", "status_code": 503}
        except psycopg2.ProgrammingError as e:
            logger.error(f"SQL syntax error in get_documents: {e}")
            return {"error": "Invalid SQL query", "status_code": 500}
        except psycopg2.Error as e:
            logger.error(f"Database error in get_documents: {e}")
            return {"error": f"Database error: {str(e)}", "status_code": 500}
        except Exception as e:
            logger.error(f"An error occurred in get_documents: {e}")
            return {"error": f"Failed to retrieve documents: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()

    def get_document(self, document_id):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            query = 'SELECT * FROM "Documents" WHERE "docId" = %s;'
            cur.execute(query, (document_id,))
            row = cur.fetchone()
            if row:
                columns = [desc[0] for desc in cur.description]  # Extract column names from cursor
                result = dict(zip(columns, row))
                return {"results": result}
            return {"results": None}
        except Exception as e:
            logger.error(f"An error occurred in get_document: {e}")
            return {"error": str(e), "status_code": 500}
        finally:
            if conn:
                conn.close()

    def update_document(self, docId, document_data_input):
        """
        Updates a document with the given document_data_input dictionary.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()

            if not docId:
                return {"error": "Missing docId for update."}

            set_clause = ', '.join([f'"{key}" = %s' for key in document_data_input.keys()])
            query = f'UPDATE "Documents" SET {set_clause} WHERE "docId" = %s RETURNING *;'
            params = tuple(document_data_input.values()) + (docId,)  # Combine values with docId
            cur.execute(query, params)
            conn.commit()
            row = cur.fetchone()

            if row:
                result_columns = [desc[0] for desc in cur.description]
                result = dict(zip(result_columns, row))
                logger.info(f"update_document result: {result}")
                return {
                    "results": result
                }

            return {"results": None}

        except Exception as e:
            logger.error(f"An error occurred in update_document: {e}")
            conn.rollback()
            return {"results": {"error": str(e)}}

        finally:
            if conn:
                conn.close()


    def delete_document(self, document_id):
        """
        Deletes a document by its ID.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            query = 'DELETE FROM "Documents" WHERE "docId" = %s;'
            cur.execute(query, (document_id,))
            conn.commit()
            deleted = cur.rowcount > 0  # True if a row was deleted
            
            if deleted:
                return {"results": {"message": "Document deleted successfully"}}
            return {"results": None}
        except Exception as e:
            logger.error(f"An error occurred in delete_document: {e}")
            conn.rollback()
            return {"error": str(e), "status_code": 500}
        finally:
            if conn:
                conn.close()

    def create_document(self, document_input_data):
        """
        Inserts a new document into the database.
        """
        logger.info(f"Creating document with data: {document_input_data}")
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            columns = ', '.join([f'"{key}"' for key in document_input_data.keys()]) 
            placeholders = ', '.join(['%s'] * len(document_input_data))
            query = f'INSERT INTO "Documents" ({columns}) VALUES ({placeholders}) RETURNING *;'
            cur.execute(query, tuple(document_input_data.values()))
            row = cur.fetchone()
            conn.commit()
            
            if row:
                columns = [desc[0] for desc in cur.description]  # Extract column names from cursor
                result = dict(zip(columns, row))
                return {"results": result}
            return {"results": None}
        except Exception as e:
            logger.error(f"An error occurred in create_document: {e}")
            conn.rollback()
            return {"error": str(e), "status_code": 500}
        finally:
            if conn:
                conn.close()