from pymongo import MongoClient
from torch.utils.data import Dataset, DataLoader
import math

# Define a dataset class to retrieve data from MongoDB
class BooksDataset(Dataset):
    def __init__(self, db):
        self.books = db["books"]
        self.pipeline = [
            {
                "$lookup": {
                    "from": "reviews",
                    "localField": "_id",
                    "foreignField": "book_id",
                    "as": "reviews"
                }
            },
            {
                "$project": {
                    "name": 1,
                    "author": 1,
                    "genre": 1,
                    "reviews.text": 1
                }
            }
        ]
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

# Connect to MongoDB
client = MongoClient('mongodb+srv://user:root@cluster0.djza6my.mongodb.net/')

# Create the database and collections
db = client["Library"]

# Create a dataset
dataset = BooksDataset(db)

# Create a dataloader
dataloader = DataLoader(dataset, batch_size=2, shuffle=False)

# Iterate over the dataloader
for batch in dataloader:
    for name, author, genre, reviews in zip(batch['name'], batch['author'], batch['genre'], batch['reviews']):
        print(f"Book: {name} by {author} ({genre})")
        for review in reviews:
            print(f"  Review: {review}")

num_requests = math.ceil(len(dataset) / 2)
print(num_requests)
