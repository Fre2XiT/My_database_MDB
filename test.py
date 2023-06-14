import asyncio
import motor.motor_asyncio
from torch.utils.data import Dataset, DataLoader

class BooksDataset(Dataset):
    def __init__(self, db):
        self.books = db["books"]

    async def fetch_books_data(self):
        pipeline = [
            {
                "$lookup": {
                    "from": "reviews",
                    "let": { "bookId": { "$toObjectId": "$_id" } },
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
                    "as": "book_reviews"
                }
            },
            {
                "$unwind": "$book_reviews"
            },
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "author": 1,
                    "genre": 1,
                    "review": "$book_reviews.text"
                }
            }
        ]
        books_data = []
        async for book in self.books.aggregate(pipeline):
            books_data.append(book)
        return books_data

    async def get_data(self):
        books_data = await self.fetch_books_data()
        return books_data

    def __len__(self):
        return len(self.books_data)

    def __getitem__(self, idx):
        book = self.books_data[idx]
        return {
            'name': book['name'],
            'author': book['author'],
            'genre': book['genre'],
            'review': book['review']
        }

async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://user:root@cluster0.djza6my.mongodb.net/')
    db = client["Library"]
    dataset = BooksDataset(db)

    books_data = await dataset.get_data()
    dataset.books_data = books_data

    dataloader = DataLoader(dataset, batch_size=2)

    for batch in dataloader:
        for name, author, genre, review in zip(batch['name'], batch['author'], batch['genre'], batch['review']):
            print(f"Book: {name} by {author} ({genre})")
            print(f"  Review: {review}")

if __name__ == "__main__":
    asyncio.run(main())
