import tantivy
from src.load import load
from rocksdict import Rdict

db = Rdict('data/rdict/')

# Define the schema, this is very important, and cannot change in the future.
schema_builder = tantivy.SchemaBuilder()
schema_builder.add_text_field("title", stored=False)
schema_builder.add_text_field("body", stored=False)
schema_builder.add_integer_field("id", stored=True)
schema = schema_builder.build()

index = tantivy.Index(schema , path='data/tantivy/')
writer = index.writer()

count = 1
for document in load('data/data.xml'):
    writer.add_document(tantivy.Document(
    title=[document.title],
    body=[document.body],
    id=[count],
    ))

    db[bin(count)] = document.title
    count += 1

writer.commit()










index.reload()
# config = index.config_reader(num_searchers=4)
searcher = index.searcher()
query = index.parse_query("Donald Trump Covid19", ["title", "body"])


results = searcher.search(query, 5).hits



for result in results:
    score, address = result
    doc = searcher.doc(address)
    doc_id = doc['id'][0]
    print(doc)
    result = db[bin(doc_id)]
    print(result)

