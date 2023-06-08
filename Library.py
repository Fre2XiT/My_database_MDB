from pymongo import MongoClient
from torch.utils.data import Dataset, DataLoader

class BooksDataset(Dataset):
    def __init__(self, db):
        self.books = db["books"]

        self.pipeline = [
            {
                "$lookup": {
                    "from": "reviews",
                    "let": { "bookId": "$_id" },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": { "$eq": ["$book_id", "$$bookId"] }
                            }
                        },
                        {
                            "$project": { "text": 1 }
                        }
                    ],
                    "as": "reviews"
                }
            }
        ]
       # print(self.pipeline)

        self.books_data = list(self.books.aggregate(self.pipeline))

    def __len__(self):
        return len(self.books_data)

    def __getitem__(self, idx):
        book = self.books_data[idx]
        reviews = [review['text'] for review in book['reviews']]
        return {
            'name': book['name'],
            'author': book['author'],
            'genre': book['genre'],
            'reviews': reviews
        }

client = MongoClient('mongodb+srv://user:root@cluster0.djza6my.mongodb.net/')

db = client["Library"]

dataset = BooksDataset(db)

dataloader = DataLoader(dataset, batch_size=2, shuffle=False)

for batch in dataloader:
    for name, author, genre, reviews in zip(batch['name'], batch['author'], batch['genre'], batch['reviews']):
        print(f"Book: {name} by {author} ({genre})")
        for review in reviews:
            print(f"  Review: {review}")
