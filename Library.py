from pymongo import MongoClient
from bson import ObjectId
from torch.utils.data import Dataset, DataLoader

class BooksDataset(Dataset):
    def __init__(self, db):
        self.books = db["books"]
        self.reviews = db["reviews"] 

        self.pipeline = [
            {
                "$lookup": {
                    "from": "reviews",
                    "localField": "_id",
                    "foreignField": "book_id",
                    "as": "book_reviews"
                }
            },
            {
                "$unwind": "$book_reviews"
            }
        ]

        self.books_data = list(self.books.aggregate(self.pipeline))

    def __len__(self):
        return len(self.books_data)

    def __getitem__(self, idx):
        book = self.books_data[idx]
        review = book['book_reviews']
       
        return {
            'name': book['name'],
            'author': book['author'],
            'genre': book['genre'],
            'review': review['text']
        }

client = MongoClient('mongodb+srv://user:root@cluster0.djza6my.mongodb.net/')

db = client["Library"]

dataset = BooksDataset(db)

dataloader = DataLoader(dataset, batch_size=2)

for batch in dataloader:
    for name, author, genre, review in zip(batch['name'], batch['author'], batch['genre'], batch['review']):
        print(f"Book: {name} by {author} ({genre})")
        print(f"  Review: {review}")
