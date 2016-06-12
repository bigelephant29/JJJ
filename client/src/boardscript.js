var super_Board;
var myname;
var username = [];
var userinit;
var move;
var score;

var board = [];
var board_position = [];
var piece = [];
var boardPiece;
var playerObjArr = [];

//class
function playerObj(playerName,playerNum,x,y){
    this.playerName = playerName;
    this.playerNum = playerNum;
    this.x = x;
    this.y = y;

    var playerImg;
    switch(playerNum){
        case 0:
            playerImg = "vader";
            break;
        case 1:
            playerImg = "R2D2";
            break;
        case 2:
            playerImg = "trooper";
            break;
        case 3:
        	playerImg = "ewok";
        	break;
        default:
            alert("playerNum overflow "+playerNum);
            break;
    }
    $("#board").append("<div class='Player' id='"+playerName+"'><img src='./png/"+playerImg+".png'></div>");

    this.elem = $('#'+playerName);
}
function createPlayer(username,userinit){
    for(var i = 0; i < username.length; i++){
        var p = new playerObj(username[i],i,0,0);
        playerObjArr.push(p);
        playerObjArr[i].elem.css("zIndex", 90-i);
        //moveMe(playerObjArr[i],0,userinit[i].y);
        //moveMe(playerObjArr[i],1,userinit[i].x);
        moveMe(playerObjArr[i],0,15);
        moveMe(playerObjArr[i],1,30);

        alert(playerObjArr[i].elem.css('zIndex'));
    }
}


function Create2DArray(rows){
    var arr = [];

    for (var i=0;i<rows;i++) {
        arr[i] = [];
    }

  return arr;
}

function initBoard(){
    boardPiece = document.getElementById("board");
    while(boardPiece.firstChild){
        if(typeof(boardPiece.firstChild.id) != 'undefined'){
            piece.push(boardPiece.firstChild);
            //alert(boardPiece.firstChild.id);
        }
        boardPiece.removeChild(boardPiece.firstChild);
    }
    showBoard();
}

function showBoard(){
    var clonePiece;
    //boardPiece.appendChild(piece[4]);
    for(var y=0;y<45;y++){
        for(var x=0;x<90;x++){
            var ran=Math.floor((Math.random() * 9))
            /*
            if(map[y][x]==0){
                clonePiece = piece[0].cloneNode(true);
            }
            else if(map[y][x]==1){
                clonePiece = piece[0].cloneNode(true);
            }
            else if(map[y][x]==2){
                clonePiece = piece[2].cloneNode(true);
            }
            else if(map[y][x]==3){
                clonePiece = piece[3].cloneNode(true);
            }
            else{
                
            }
            */
            if(ran==2){
                clonePiece = piece[2].cloneNode(true);
            }
            else if(ran==3){
                clonePiece = piece[3].cloneNode(true);
            }
            else{
                if(ran<=6){
                    clonePiece = piece[0].cloneNode(true);
                }
                else{
                    clonePiece = piece[0].cloneNode(true);
                }
            }
            clonePiece.id = x+","+y;
            board_position[y].push(clonePiece.id);
            clonePiece.onclick = function(){
                alert("coordinate:"+this.id);
            }
            clonePiece.style.left=x*32+"px";
            clonePiece.style.top=y*32+"px";
            boardPiece.appendChild(clonePiece);
        }
    }

}
function movePlayers(move){
    for(var i = 0; i < move.length ; i++){
        switch(move[i].action){
            case "l":
                moveMe(playerObjArr[i],1,-1);
                break;
            case "u":
                moveMe(playerObjArr[i],0,-1);
                break;
            case "r":
                moveMe(playerObjArr[i],1,1);
                break;
            case "d":
                moveMe(playerObjArr[i],0,1);
                break;
            default:
                alert("movePlayers error");
                break;
        }
        if(move[i].isOccupy){
            //occupy the land
        }
    }   
}
function moveMe(me,left,mv){
    if(left==1){
        me.elem.animate({left:"+="+mv*32+"px"},'slow');
        if(mv>0){
            if((me.x % 30) == 29){
                moveBoard(BoardObj,1,-30);
            }
        }
        else{
            if((me.x % 30) == 0){
                moveBoard(BoardObj,1,30);
            }
        }
        me.x+=mv;
    }
    else{
        me.elem.animate({top:"+="+mv*32+"px"},'slow');
        if(mv>0){
            if((me.y % 15) == 14){
                moveBoard(BoardObj,0,-15);
            }
        }
        else{
            if((me.y % 15) == 0){
                moveBoard(BoardObj,0,15);
            }
        }
        me.y+=mv;
    }
}

function moveBoard(boardObj,left,mv){
    if(left==1 ){
            boardObj.elem.animate({left:"+="+mv*32+"px"},'fast');
    }
    else{
        boardObj.elem.animate({top:"+="+mv*32+"px"},'fast');
    }
}

function playerKeyDown(me,BoardObj,conObj){
    $(document).keydown(function(key) {
        switch(parseInt(key.which,10)) {
            // Left arrow key pressed
            case 37:
                if(me.x > 0){
                    me.elem.animate({left: "-=32px"}, 'fast');
                    if((me.x % 30) == 0){
                        moveBoard(BoardObj,1,30);
                    }
                    me.x -= 1;
                }
                break;
            // Up Arrow Pressed
            case 38:
                if(me.y > 0){
                    me.elem.animate({top: "-=32px"}, 'fast');
                    if((me.y % 15) == 0){
                        moveBoard(BoardObj,0,15);
                    }
                    me.y -= 1;
                }
                break;
            // Right Arrow Pressed
            case 39:
                if(me.x < 89){
                    me.elem.animate({left: "+=32px"}, 'fast');
                    if((me.x % 30) == 29){
                        moveBoard(BoardObj,1,-30);
                    }
                    me.x += 1;
                }
                break;
            // Down Arrow Pressed
            case 40:
                if(me.y < 44){
                    me.elem.animate({top: "+=32px"}, 'fast');
                    if((me.y % 15) == 14){
                        moveBoard(BoardObj,0,-15);
                    }
                    me.y += 1;
                }
                break;
        }
        conObj.sendMsg();
    });
}

$(document).ready(function() {
    board_position = Create2DArray(45);
    var BoardObj = {elem:$('#board'),x:0,y:0};

    var connectObj = {
        host: location.host,
        socket: null,

        init: function(){
            var url = "ws://" + connectObj.host + "/socket";
            connectObj.socket = new WebSocket(url);
            connectObj.socket.onmessage = function(event){
                connectObj.showMsg(event.data);
            },
            connectObj.socket.onclose = function(event){
                console.log("on close");
            },
            connectObj.socket.onerror = function(event){
                console.log("on error");
            }
        },
        sendMsg: function(){
            var msg = {playerObj:Me};
            connectObj.socket.send(JSON.stringify(msg));
        },
        showMsg: function(){
            var data = JSON.parse(message);
            $("#message").append(data.playerObj.playerName+"<br/>");
            for(key in data){
                switch(key){
                    case "map"://map[][]
                        super_Board = data[key];
                        break;
                    case "myname"://myname
                        myname = data[key];
                        break;
                    case "username"://username[]
                        username = data[key];
                        break;
                    case "userinit"://userinit[] (.x .y)
                        userinit = data[key];
                        createPlayer(username,userinit);
                        break;
                    case "move"://move[]
                        move = data[key];
                        movePlayers(move);
                        break;
                    case "score":
                        score = data[key];
                        break;
                    default:
                        alert("showMsg error!");
                        break;
                }

            }
        }
    };

    BoardObj.elem.css({"top":"-480px","left":"-960px"});
    initBoard();
    myname = 0;
    username.push("Me");
    username.push("R2D2");
    username.push("Trooper");
    username.push("Ewok");
    createPlayer(username);
    
    $(".linedtext").linedtextarea();
    $("#code").keydown(function (e) {
        if (e.ctrlKey && e.keyCode == 13) {
            // Ctrl-Enter pressed
            alert("submit code");
        }
    });
    
    //playerKeyDown(playerObjArr[myname],BoardObj,connectObj);
    moveMe(playerObjArr[1],1,15);
    moveMe(playerObjArr[2],0,7);
    moveMe(playerObjArr[3],1,15);
    moveMe(playerObjArr[3],0,7);
    moveMe(playerObjArr[3],0,-7);

});
