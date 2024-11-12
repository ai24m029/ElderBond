from DataBase import DataBaseAccess


# Initialize the Database
with DataBaseAccess() as db:
    # Add some posts
    db.add_post("image1.jpg", "First post text", "User1")
    db.add_post("image2.jpg", "Second post text", "User2")
    db.add_post("image3.jpg", "Third post text", "User3")

   
    # Retrieve and print the latest post
    latest_post = db.get_latest_post()
    if latest_post:
        print("Latest Post:")
        print("Image:", latest_post[1])
        print("Text:", latest_post[2])
        print("User:", latest_post[3])
        print("Timestamp:", latest_post[4])
    else:
        print("No posts available.")
        # Retrieve and print all posts to see their timestamps
        
    