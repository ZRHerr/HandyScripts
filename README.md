# HandyScripts
Misc. scripts that have proven useful during my time as a software engineer. 

___

## git_stats.sh

- Gets data 'Foreach' filename, discover lines of code, number of commits & the date of the first and last commit. 
- Then pulls that data into a spreadsheet so you can easily sort by each metric and view the data relevant to you.

```sh
    bash git_stats.sh [dir] [filetypes] > stats.csv
    open -a Numbers stats.csv
```

***For example:***

```sh
    bash git_stats.sh ../HandyScripts "sh" "py" > stats.csv
```
___

## record_generator.py

- Generates a json file with randomly generated data in `/records/{record_id}.json`
    - Takes that data and inserts a record into DynamoDB (great for testing lambda functions that perform actions on json data). 

```python
python record_generator.py <Firstname> <Lastname>
```

***For Example***

```python
python record_generator.py Zachary Herrera
```