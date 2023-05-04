/* global use, db */
// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

const database = '9xmovies';
const collection = 'dl_link';

// Create a new database.
use(database);

// Create a new collection.
db.createCollection(collection);

// More information on the `createCollection` command can be found at:
// https://www.mongodb.com/docs/manual/reference/method/db.createCollection/
