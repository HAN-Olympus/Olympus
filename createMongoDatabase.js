/* 
 * Create Database MongoDB 
 * This script is intended to create the basic databases for Olympus to work. 
 * It will set up some indexes to allow expiring data after a certain period of time.
 */

print("Configuring MongoDB for Olympus Operations");
print("==========================================");
print("");

conn = new Mongo();
print("* Connected.");
db = conn.getDB("olympus");
print("* Selected Olympus Database.");
db.output.ensureIndex( { "_created" : 1 }, { expireAfterSeconds : 3600 } ); // Remove all output after an hour to avoid congestion
print("* Ensured index on Output.");

print("\nAll done.\n");