# Social Media User Graph Analysis

This Python script performs analysis on a social media user graph, exploring relationships, interests, and providing functionality for graph visualization.


## Requirements

- Python 3.x
- pandas
- networkx
- matplotlib
- nltk

Warning, plesae paste the file path into 260th line 
data = pd.read_json(r'FilePath') 
The Data Link:
https://drive.google.com/file/d/1MF2SLC1OmNXKvkZPQD4LmjAtnsCGKz7Q/view?usp=drive_link

You can install the required packages using:

```bash
pip install pandas networkx matplotlib nltk


Data Loading:
The user data should be in JSON format. Modify the data variable with the path to your dataset.

```python
data = pd.read_json('path_to_your_data.json')


Initialization:
Create a HashTable for user data and another for interest data.
Instantiate the UserGraph class with these tables.

```python
userDataTable = HashTable(size=100)
interestTable = HashTable(size=100)
userGraph = UserGraph(userDataTable, interestTable)


Data Insertion:
Populate the user data into the user data hash table

```python
for index, row in data.iterrows():
    theUser = {
	"username": row["username"],
	# ...
    }
    userDataTable.insert(row["username"], theUser)


Graph Construction and Analysis:
Add relationships between users, determine interests, and perform various analyses.

```python
userGraph.add_relationships()
userGraph.writeRelation()
userGraph.determineInterest()
userGraph.writeCommon()
userGraph.writeTrends()


Menu-driven Interaction:
Run the script, and you'll be prompted with a menu for different actions.

```bash
python your_script_name.py


Menu Options
1.Draw Graph for a Specific User: Visualize the user graph for a specific user.

2.Draw All Users Relation Graph: Generate and display the graph representing relationships between all users.

3.DFS to Find Tweets Based on Keywords: Perform a Depth-First Search to find tweets based on specified keywords.

4.BFS to Find Connection Between Two Users: Perform a Breadth-First Search to find common interests between two users.
5.Exit: Terminate the program.


Notes
The script uses various libraries such as networkx, matplotlib, and nltk for graph visualization and natural language processing.
Feel free to customize and extend the code to suit your specific requirements.

Make sure to replace `path_to_your_data.json` and `your_script_name.py` with the actual paths and filenames used in your project.