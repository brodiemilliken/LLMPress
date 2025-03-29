from celery_client import tokenize, detokenize

def test_direct_celery():
    print("Submitting Celery tokenization task...")
    tokens = tokenize("This is a direct Celery call. Here is a bunch of random test text to tokenize. Let's see how it works with Celery!")
    print("Tokenized:", tokens)

    print("Submitting Celery detokenization task...")
    text = detokenize(tokens)
    print("Detokenized:", text)

if __name__ == "__main__":
    test_direct_celery()
