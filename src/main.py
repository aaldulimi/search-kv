import tantivy
from rocksdict import Rdict

db = Rdict('data/rdict/')

# Define the schema, this is very important, and cannot change in the future.
schema_builder = tantivy.SchemaBuilder()
schema_builder.add_text_field("title", stored=False)
schema_builder.add_text_field("body", stored=False)
schema_builder.add_integer_field("id", stored=True)
schema = schema_builder.build()

index = tantivy.Index(schema, path='data/tantivy/')


if __name__ == "__main__":
    search_query = 'Capitol riots'
    results_count = 10

    searcher = index.searcher()
    query = index.parse_query(search_query, ["title", "body"])

    results = searcher.search(query, results_count).hits

    for result in results:
        score, address = result
        document = searcher.doc(address)
        doc_id = document['id'][0]
        value = db[bin(doc_id)]

        print(result)


