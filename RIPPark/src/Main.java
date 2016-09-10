
import java.util.List;
import java.util.Set;

import org.bson.Document;

import com.mongodb.BasicDBObject;
import com.mongodb.Block;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.MongoClient;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.MongoIterable;

public class Main {

	private MongoClient mongoClient;
	private MongoDatabase db;
	private DBCollection table;
	private BasicDBObject searchQuery;

	public Main() {
		mongoClient = new MongoClient();
		db = mongoClient.getDatabase("ripPark");
		
		FindIterable<Document> iterable = db.getCollection("permittedParking")
				.find(new Document("Side", "B/S"));
		
		iterable.forEach(new Block<Document>() {
			@Override
			public void apply(final Document document) {
				System.out.println(document);
			}
		});
		
		
		MongoIterable<String> colls = db.listCollectionNames();
		
		MongoCursor<String> iter = colls.iterator();
		
		while(iter.hasNext()) {
			System.out.println(iter.next());
		}
		
		
		System.out.println(colls);
//		table = db.getCollection("permittedParking");
//		searchQuery = new BasicDBObject();
//		searchQuery.put("Side", "B/S");
//		DBCursor cursor = table.find(searchQuery);
//		
//		while(cursor.hasNext()) {
//			System.out.println(cursor.next());
//		}
//		
//		System.out.println(db);
	}

	public static void main(String[] args) {
		System.out.println("hiiiii");
		Main main = new Main();
	}
}