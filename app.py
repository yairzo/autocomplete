import os
from flask import Flask, request, jsonify, abort
from elasticsearch import Elasticsearch, helpers
import time

es_host = os.environ['DOCKER_MACHINE_IP']
print('Elastic host is {}'.format(es_host))

es = Elasticsearch([es_host])
app = Flask(__name__)

average_request_handle_time_ms = 0
request_handled_count = 0
words_count = 0


@app.route('/')
def health_check():
    return "OK"


@app.route('/dictionary', methods=['GET'])
def search_dictionary():
    prefix = request.args.get('prefix')
    if prefix is None:
        abort(404, "prefix param is obligatory")
    if not es.indices.exists(index="words"):
        abort(500, "'words' index does not exit")
    start_time = round(time.time() * 1000)
    query_body = {"query": {
        "query_string": {
            "query": prefix+"*",
            "fields": [
                "word"
            ]
        }
    }}
    results_size = int(os.environ.get('ES_SEARCH_RESULTS_SIZE'))
    result = es.search(index="words", body=query_body, size=results_size)
    all_hits = result['hits']['hits']
    words = []
    for hit in all_hits:
        words.append(hit['_source']['word'])

    end_time = round(time.time() * 1000)
    request_duration = end_time - start_time
    update_requests_stats(request_duration)
    return jsonify(words)


def update_requests_stats(request_duration):
    global average_request_handle_time_ms
    global request_handled_count
    average_request_handle_time_ms = (average_request_handle_time_ms * request_handled_count
                                      + request_duration) / (request_handled_count + 1)
    request_handled_count += 1


@app.route('/statistics', methods=['GET'])
def statistics():
    stats = {"averageRequestHandleTimeMs": average_request_handle_time_ms,
             "requestHandledCount": request_handled_count,
             "wordsCount": words_count
             }
    return jsonify(stats)


@app.route('/update_dictionary', methods=['POST'])
def update_dictionary():
    f = request.files['file']
    counter = 1
    words = []
    for word in f:
        words.append(
            {
                "_id": word.strip().decode(),
                "_index": "words",
                'word': word.strip().decode(),
            }
        )
        if counter % int(os.environ.get('ES_INDEX_CHUNK_SIZE')) == 0:
            print("Progress: Indexed " + str(counter) + " words", flush=True)
            helpers.bulk(es, words)
            words = []
        counter += 1

    helpers.bulk(es, words)
    global words_count
    es.indices.refresh("words")
    res = es.cat.count("words", params={"format": "json"})
    words_count = int(res[0]['count'])
    print("Progress: Indexed " + str(words_count) + " words", flush=True)
    return "Dictionary updated"


if __name__ == '__main__':
    # define the localhost ip and the port that is going to be used
    # in some future article, we are going to use an env variable instead a hardcoded port
    app.run(host='0.0.0.0', port='5001')
