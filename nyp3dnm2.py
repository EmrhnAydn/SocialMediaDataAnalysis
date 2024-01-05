import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from collections import deque

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, key, value):
        new_node = Node(key, value)
        new_node.next = self.head
        self.head = new_node

    def search(self, key):
        current = self.head
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return None


class HashTable:
    def __init__(self, size):
        self.size = size
        self.table = [LinkedList() for _ in range(size)]

    def hash_function(self, key):
        total = 0
        for char in key:
            total += ord(char)
        return total % self.size

    def insert(self, key, value):
        index = self.hash_function(key)
        self.table[index].insert(key, value)

    def search(self, key):
        index = self.hash_function(key)
        return self.table[index].search(key)

class UserGraph:
    def __init__(self, user_table, interest_table):
        self.user_table = user_table
        self.interest_table = interest_table
        self.graph = nx.DiGraph()

    def add_relationships(self):
        for linked_list in self.user_table.table:
            current_node = linked_list.head
            while current_node:
                user = current_node.value
                following_list = user["following"]
                followers_list = user["followers"]

                for follower_username in followers_list:
                    self.graph.add_edge(follower_username, user["username"])

                for following_username in following_list:
                    self.graph.add_edge(user["username"], following_username)

                current_node = current_node.next

    def determineInterest(self):
        stop_words = set(stopwords.words('english'))
        for linked_list in self.user_table.table:
            current_node = linked_list.head
            while current_node:
                user = current_node.value
                tweets = user["tweets"]

                tweets_text = ' '.join(tweets) if isinstance(tweets, list) else tweets #String komtrolu

                tokens = word_tokenize(tweets_text.lower()) #kucuk harfe cevirip kelimeleri ayrıştırıyor

                filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words] #filtreleme işlemi

                freq_dist = FreqDist(filtered_tokens)

                user["interest_areas"] = [word for word, freq in freq_dist.items() if freq >= 7]

                for interest in user["interest_areas"]:
                    interest_users = self.interest_table.search(interest)
                    if interest_users:
                        interest_users.append(user["username"])
                    else:
                        self.interest_table.insert(interest, [user["username"]])

                current_node = current_node.next
    def draw_graph(self):
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, font_weight='bold', connectionstyle='arc3,rad=0.1')
        plt.title("User Graph")
        plt.show()

    def writeRelation(self, filename='user_relationships.txt'):

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write("Followers-followed Relationship of Users\n")
            for linked_list in self.user_table.table:
                current_node = linked_list.head
                while current_node:
                    user = current_node.value
                    username = user["username"]
                    following_list = user["following"]
                    followers_list = user["followers"]

                    file.write(f"User: {username}\n")
                    file.write("Followers:\n")
                    for follower_username in followers_list:
                        file.write(f" - {follower_username}\n")

                    file.write("Following:\n")
                    for following_username in following_list:
                        file.write(f" - {following_username}\n")

                    file.write("\n")
                    current_node = current_node.next

    def writeCommon(self, filename='interest.txt'):

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, 'a', encoding='utf-8') as file:
            for linked_list in self.interest_table.table:
                current_node = linked_list.head
                while current_node:
                    interest = current_node.key
                    users = current_node.value
                    if len(users) > 1:
                        common_users = []
                        for username in users:
                            user_interests = self.user_table.search(username)["interest_areas"]
                            if interest in user_interests:
                                common_users.append(username)

                        if len(common_users) > 1:
                            file.write(f"Interest: {interest}, \nUsers: {', '.join(common_users)}\n")
                            for username in common_users:
                                user_info = self.user_table.search(username)

                    current_node = current_node.next
    #DFS
    def dfs(self, start_user):
        keyword_input = input("Enter the keywords to search")
        keywords = [keyword.strip() for keyword in keyword_input.split(",")]

        visited = set()
        stack = [start_user]

        print(f"\nDFS: Searching for {keywords} in tweets starting from {start_user}:")

        while stack:
            current_user = stack.pop()
            if current_user not in visited:
                user_info = self.user_table.search(current_user)
                if user_info:
                    tweets = user_info["tweets"]
                    if isinstance(tweets, list):
                        for tweet in tweets:
                            if any(keyword.lower() in tweet.lower() for keyword in keywords):
                                print(f"{current_user}: {tweet}\n")

                    visited.add(current_user)
                    stack.extend(self.graph.neighbors(current_user))

    # BFS
    def bfs(self, user1, user2):
        visited = set()
        queue = deque([(user1, [])])

        print(f"\nBFS Process for Finding common interests between {user1} and {user2}\n")

        while queue:
            current_user, path = queue.popleft()
            if current_user not in visited:
                user_info = self.user_table.search(current_user)
                if user_info:
                    interests = set(user_info.get("interest_areas", []))
                    if user2 in interests:
                        print(
                            f"Common interest found: {user2} between {user1} and {current_user}, Common interests: {', '.join(interests)}")
                        return

                    visited.add(current_user)

                    for neighbor in set(self.graph.neighbors(current_user)) - visited:
                        neighbor_info = self.user_table.search(neighbor)
                        if neighbor_info:
                            neighbor_interests = set(neighbor_info.get("interest_areas", []))
                            common_interests = interests.intersection(neighbor_interests)
                            if common_interests:
                                print(
                                    f"Common interests found between {current_user} and {neighbor}: {', '.join(common_interests)}")
                                return

                            queue.append((neighbor, path + [current_user]))
    #oneuser graph
    def draw_user_graph(self, username):
        user_info = self.user_table.search(username)
        if user_info:
            user_graph = nx.DiGraph()

            followers_list = user_info["followers"]
            for follower_username in followers_list:
                user_graph.add_edge(follower_username, username)

            following_list = user_info["following"]
            for following_username in following_list:
                user_graph.add_edge(username, following_username)

            pos = nx.spring_layout(user_graph, seed=42, k=0.3)  # Adjust the 'k' parameter for spreading out
            pos = {node: (x, y - 0.05) for node, (x, y) in pos.items()}

            nx.draw(user_graph, pos, with_labels=True, font_size=7, font_weight='normal', connectionstyle='arc3,rad=0.2',
                    node_size=200, node_color='darkred', linewidths=0.3, edge_color='blue', alpha=0.7)
            plt.title(f"{username}'s Graph")
            plt.show()
        else:
            print(f"{username}'s user not found")
    def writeTrends(self, filename= 'trends.txt'):

        if os.path.exists(filename):
            os.remove(filename)

        all_interests = set()
        for linked_list in self.interest_table.table:
            current_node = linked_list.head
            while current_node:
                interest = current_node.key
                all_interests.add(interest)
                current_node = current_node.next

        # Tüm ilgi alanlarını frekanslarına göre sırala
        sorted_interests = sorted(all_interests, key=lambda x: len(self.interest_table.search(x) or []), reverse=True)

        # İlk 5 ilgi alanını dosyaya yaz
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(f"\nTop 5 Trending Interest Areas for All Regions and Locations\n")
            for i, interest in enumerate(sorted_interests[:10]):
                users = self.interest_table.search(interest) or []
                file.write(f"{i + 1}. {interest}: {len(users)} users\n")

#Main
data = pd.read_json(r'FilePath')

userDataTable = HashTable(size=100)
interestTable = HashTable(size=100) #userGraph Classının içinde doldurulacak

userGraph = UserGraph(userDataTable, interestTable)

for index, row in data.iterrows():
    theUser = {
        "username": row["username"],
        "name": row["name"],
        "followers_count": row["followers_count"],
        "following_count": row["following_count"],
        "language": row["language"],
        "region": row["region"],
        "tweets": row["tweets"],
        "following": row["following"],
        "followers": row["followers"],
        "interest_areas": row.get("interest_areas", [])
    }
    userDataTable.insert(row["username"], theUser)

userGraph.add_relationships()
userGraph.writeRelation()
userGraph.determineInterest()
userGraph.writeCommon()
userGraph.writeTrends()

#MENU

import sys

while True:
    def menu(secim):
        if secim == 1:
            girilen_kullanici_adi = input("Enter the username to draw the graph:")
            userGraph.draw_user_graph(girilen_kullanici_adi)
        elif secim == 2:
            userGraph.draw_graph()
        elif secim == 3:
            kad = input("Enter the starting user:")
            userGraph.dfs(kad)
        elif secim == 4:
            u1 = input("Enter the first user: ")
            u2 = input("Enter the second user: ")
            userGraph.bfs(u1, u2)
        elif secim == 5:
            print('Exiting')
            sys.exit()
        else:
            print('Invalid Choice')

    print('----- MENÜ -----')
    print('1.  Draw Graph for a Specific User')
    print('2. Draw All Users Relation Graph')
    print('3. DFS to Find Tweets Based on Keywords')
    print('4. BFS to Find Connection Between Two Users')
    print('5. Exit')


    kullanici_secimi = input("Select a process: ")
    try:
        kullanici_secimi = int(kullanici_secimi)
        menu(kullanici_secimi)
    except ValueError:
        print("Please enter a valid number")






