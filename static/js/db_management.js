
db.stocks.find().pretty()

// Query portfolio
db.portfolio.find({user_id: 1}).pretty()

// Query price history
db.price_history.find({symbol: "AAPL"}).sort({date: -1}).limit(10)

// Create indexes for better performance
db.stocks.createIndex({symbol: 1}, {unique: true})
db.price_history.createIndex({symbol: 1, date: -1})
db.portfolio.createIndex({user_id: 1, symbol: 1})

// Aggregation examples
db.stocks.aggregate([
    {$group: {_id: "$sector", count: {$sum: 1}, avgPrice: {$avg: "$current_price"}}}
])

// Clean up old data
db.price_history.deleteMany({date: {$lt: ISODate("2024-01-01")}})