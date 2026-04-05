import csv
import math
import os
import logging
from collections import defaultdict

# ================= FILE PATHS =================
BOOK_FILE = r"C:\30 days\Python\p11\books_clean.csv"
USER_FILE = r"C:\30 days\Python\p11\users_clean.csv"
INTERACTION_FILE = r"C:\30 days\Python\p11\interactions_clean.csv"

# ================= LOGGING =================
logging.basicConfig(
    filename="errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(message)s"
)

def log_error(error, row=None):
    logging.error(f"{error} | Row: {row}")


# ================= SAFE CSV READER =================
def safe_reader(file):
    try:
        f = open(file, "r", encoding="utf-8-sig")
        reader = csv.DictReader(f, skipinitialspace=True)

        if reader.fieldnames:
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

        return reader
    except Exception as e:
        log_error(e)
        return []


# ================= LOAD BOOKS =================
def load_books():
    books = {}
    genres = {}

    reader = safe_reader(BOOK_FILE)

    for row in reader:
        try:
            bid = int(float(row.get("book_id", 0)))
            title = row.get("title", "Unknown").strip()
            genre = row.get("genre", "Unknown").strip()

            books[bid] = title
            genres[bid] = genre

        except Exception as e:
            log_error(e, row)

    return books, genres


# ================= LOAD USERS =================
def load_users():
    users = {}

    if not os.path.exists(USER_FILE):
        return users

    reader = safe_reader(USER_FILE)

    for row in reader:
        try:
            username = row.get("username", "").strip()
            password = row.get("password", "").strip()

            if username and password:
                users[username] = password

        except Exception as e:
            log_error(e, row)

    return users


# ================= LOAD INTERACTIONS =================
def load_interactions():
    data = defaultdict(dict)

    if not os.path.exists(INTERACTION_FILE):
        return data

    reader = safe_reader(INTERACTION_FILE)

    for row in reader:
        try:
            user = row.get("user_id", "").strip()
            book = int(float(row.get("book_id", 0)))
            rating = float(row.get("rating", 0))

            if user:
                data[user][book] = rating

        except Exception as e:
            log_error(e, row)

    return data


# ================= SAVE FUNCTIONS =================
def save_user(username, password):
    file_exists = os.path.exists(USER_FILE)

    with open(USER_FILE, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["username", "password"])
        writer.writerow([username, password])


def save_interaction(user, book_id, rating):
    file_exists = os.path.exists(INTERACTION_FILE)

    with open(INTERACTION_FILE, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user_id", "book_id", "rating"])
        writer.writerow([user, book_id, rating])


# ================= AUTH =================
def register(users):
    username = input("Enter username: ")

    if username in users:
        print("❌ User already exists!")
        return None

    password = input("Enter password: ")
    save_user(username, password)

    users[username] = password  # IMPORTANT FIX

    print("✅ Registered successfully!")
    return username


def login(users):
    username = input("Username: ")
    password = input("Password: ")

    if users.get(username) == password:
        print("✅ Login successful!")
        return username

    print("❌ Invalid credentials!")
    return None


# ================= COSINE SIMILARITY =================
def cosine(u1, u2):
    common = set(u1) & set(u2)

    if not common:
        return 0

    dot = sum(u1[i] * u2[i] for i in common)
    norm1 = math.sqrt(sum(v**2 for v in u1.values()))
    norm2 = math.sqrt(sum(v**2 for v in u2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0

    return dot / (norm1 * norm2)


# ================= RECOMMEND =================
def recommend(user, data, books):
    if user not in data:
        return popular(data, books)

    scores = defaultdict(float)

    for other in data:
        if other == user:
            continue

        sim = cosine(data[user], data[other])

        for book, rating in data[other].items():
            if book not in data[user]:
                scores[book] += rating * sim

    sorted_books = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [(bid, books.get(bid, "Unknown")) for bid, _ in sorted_books[:5]]


# ================= POPULAR =================
def popular(data, books):
    count = defaultdict(int)

    for user in data:
        for book in data[user]:
            count[book] += 1

    sorted_books = sorted(count.items(), key=lambda x: x[1], reverse=True)

    return [(bid, books.get(bid, "Unknown")) for bid, _ in sorted_books[:5]]


# ================= MOOD =================
def mood_recommend(genres, books, data):
    print("\n1. Happy 😄")
    print("2. Sad 😢")
    print("3. Motivated 💪")

    choice = input("Enter: ")

    mood_map = {
        "1": ["comedy", "romance"],
        "2": ["drama", "tragedy", "emotional"],
        "3": ["self-help", "biography", "inspiration"]
    }

    selected = mood_map.get(choice, [])

    results = []

    for bid, genre in genres.items():
        if any(m in genre.lower() for m in selected):
            results.append((bid, books[bid]))

    if not results:
        print("⚠️ No mood-based books found. Showing popular books instead.")
        return popular(data, books)

    return results[:5]


# ================= SEARCH =================
def search_books(books):
    keyword = input("Enter keyword: ").lower()

    results = []
    for bid, title in books.items():
        if keyword in title.lower():
            results.append((bid, title))

    return results[:5]


# ================= MAIN =================
def main():
    books, genres = load_books()
    users = load_users()
    data = load_interactions()

    current_user = None

    print("\n📚 BOOK RECOMMENDATION SYSTEM")

    while True:
        if not current_user:
            print("\n1. Login")
            print("2. Register")
            print("3. Exit")

            ch = input("Enter: ")

            if ch == "1":
                current_user = login(users)
            elif ch == "2":
                current_user = register(users)
            elif ch == "3":
                break

        else:
            print(f"\nWelcome {current_user}")
            print("1. Recommend")
            print("2. Mood Based")
            print("3. Search")
            print("4. Rate Book")
            print("5. Logout")

            ch = input("Enter: ")

            if ch == "1":
                recs = recommend(current_user, data, books)
                print("\n🎯 Recommendations:")
                for _, title in recs:
                    print("-", title)

            elif ch == "2":
                recs = mood_recommend(genres, books, data)
                print("\n😊 Mood Books:")
                for _, title in recs:
                    print("-", title)

            elif ch == "3":
                recs = search_books(books)
                print("\n🔍 Results:")
                for _, title in recs:
                    print("-", title)

            elif ch == "4":
                try:
                    bid = int(input("Book ID: "))
                    rating = float(input("Rating (1-5): "))
                    save_interaction(current_user, bid, rating)

                    # update memory instantly
                    data[current_user][bid] = rating

                    print("✅ Saved!")

                except Exception as e:
                    log_error(e)

            elif ch == "5":
                current_user = None


if __name__ == "__main__":
    main()