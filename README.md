# JJJ

JJJ is the final project of Team 8 in Computer Network Lab Spring 2016 in NTU CSIE.

JJJ is a programming-based game, which contains small, cute, 8-bit pictures.
The players have to write some code, which can be interpreted by JJJInterpreter.
The interface of the code can help players to control their characters, and try their best to win the game.

To successfully run JJJ, you have to install python3, tornado, and pyparsing.

Tornado can be installed through pip
```
pip install tornado
```
Pyparsing can be installed through pip, too
```
pip install pyparsing
```
If you have already installed pyparsing, you can get the latest version by
```
pip install -U pyparsing
```

If you find some error in JJJInterpreter, you can test it by simply executing it.
```
python3 interpreter/JJJInterpreter.py
```

If you failed to install pyparsing, or you failed to run JJJInterpreter.py, please refer to [this page](http://pyparsing.wikispaces.com/Download+and+Installation).

After successfully installed the tools, just run the server
```
python3 server/server.py
```
Then you can visit localhost:8888/ to test the server.

The default port is 8888, you can modify it in server/server.py.
