import com.mongodb.MongoClient;
import com.mongodb.client.MongoDatabase;


public class Main {

	private MongoClient mongoClient;
	private MongoDatabase db;

	public Main() {
		mongoClient = new MongoClient();
		db = mongoClient.getDatabase("ripPark");
	}

	public static void main(String[] args) {

	}
}