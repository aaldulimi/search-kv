import tantivy
import time
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
    results_count = 5

    searcher = index.searcher()
    query = index.parse_query(search_query, ["title", "body"])

    results = searcher.search(query, results_count).hits

    for result in results:
        score, address = result
        document = searcher.doc(address)
        doc_id = document['id'][0]
        value = db[bin(doc_id)]

        print(result)







index.reload()
# config = index.config_reader(num_searchers=4)
searcher = index.searcher()
query = index.parse_query("Donald Trump Covid19", ["title", "body"])


start_time = time.time()
results = searcher.search(query, 5).hits
print(time.time() - start_time)


start_time = time.time()

for result in results:
    score, address = result
    doc = searcher.doc(address)
    doc_id = doc['id'][0]
    print(doc)
    result = db[bin(doc_id)]
    print(result)

print(time.time() - start_time)
