# Message split algorithm

Python test task.


## Description

There is a script that can split mixed (raw text + HTML tags) message into
several parts not exceeding the specified size, with preservation of HTML semantics.

`msg_split.py` - main logic
`main.py` - command-line interface


## Usage

To split a message from HTML file: `python3 main.py sourse.html --max-len=4096`
