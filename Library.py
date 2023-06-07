from pymongo import MongoClient
from torch.utils.data import Dataset, DataLoader

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
                "$group": {
                    "_id": "$_id",
                    "name": { "$first": "$name" },
                    "author": { "$first": "$author" },
                    "genre": { "$first": "$genre" },
                    "reviews": { "$push": "$reviews" }
                }
            }
        ]
        self.books_data = list(self.books.aggregate(self.pipeline))

    def __len__(self):
        return len(self.books_data)

    def __getitem__(self, idx):
        book = self.books_data[idx]
        reviews = [review['text'] for review_array in book['reviews'] for review in review_array]
        return {
            'name': book['name'],
            'author': book['author'],
            'genre': book['genre'],
            'reviews': reviews
        }

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')

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




    
""" # Get all the books
book_data = list(books.find({}))


# Get all the books and their reviews using only 2 queries
book_data = list(books.find({}))
book_ids = [book["_id"] for book in book_data]
reviews_data = list(reviews.find({"book_id": {"$in": book_ids}}))

# Loop through the books and get the reviews for each book
for book in book_data:
    reviews_data_for_book = [review for review in reviews_data if review["book_id"] == book["_id"]]
    print(f"{book['name']} has {len(reviews_data_for_book)} reviews") """



