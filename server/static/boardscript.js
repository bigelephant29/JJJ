var super_Board;
var myname;
var username;
var userinit;
var move;
var score;
var BoardObj;
var Me;

var board = [];
var board_position = [];
var piece = [];
var boardPiece;
var playerObjArr = [];

var conObj = {
        host: location.host,
        socket: null,

        init: function(){
            var url = "ws://" + conObj.host + "/socket";
            conObj.socket = new WebSocket(url);
            conObj.socket.onmessage = function(event){
                conObj.showMsg(event.data);
            },
            conObj.socket.onclose = function(event){
                console.log("on close");
            },
            conObj.socket.onerror = function(event){
                console.log("on error");
            }
        },
        sendMsg: function(message){
            var msg = {code: message};
            console.log(conObj.socket.send(JSON.stringify(msg)));
        },
        showMsg: function(message){
            var data = JSON.parse(message);
            //$("#message").append(data.playerObj.playerName+"<br/>");
            //$("#message").append(data + "<br/>");
            for(key in data){
                switch(key){
                    case "map"://map[][]
                        super_Board = data[key];
                        BoardObj = {elem:$('#board'),x:0,y:0};
                        BoardObj.elem.css({"top":"-480px","left":"-960px"});
                        initBoard();
                        break;
                    case "myname"://myname

                        myname = data[key];
                        //alert("myname " + myname);
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
                        console.log("move "+move[0].action);
                        movePlayers(move);
                        break;
                    case "score":
                        score = data[key];
                        break;
                    case "position":
                        //alert("myname: " + myname);
                        var p = new playerObj(myname,myname,data[key][0],data[key][1]);
                        
                        playerObjArr[myname] = p;
                        playerObjArr[myname].elem.css("zIndex", 90-myname);
                        moveMe(playerObjArr[myname],0,data[key][0]);
                        moveMe(playerObjArr[myname],1,data[key][1]);
                        //alert("0x:"+data[key][1]+" 0y:"+data[key][0]);
                        //alert("x:"+playerObjArr[myname].x+" y:"+playerObjArr[myname].y);

                        break;
                    default:
                        alert("showMsg error!"+key+" "+data[key]);
                        break;
                }

            }
        }
    };

//class
function playerObj(playerName,playerNum,x,y){
    this.playerName = playerName;
    this.playerNum = playerNum;
    this.x = 0;
    this.y = 0;

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
            //alert("playerNum overflow "+playerNum);
            break;
    }
    $("#board").append("<div class='Player' id='"+playerName+"'><img src='./static/"+playerImg+".png'></div>");

    this.elem = $('#'+playerName);
}
function createPlayer(username,userinit){
    for(var i = 0; i < username.length; i++){
        if(username[i]!=myname){
            var p = new playerObj(username[i],i,0,0);
            playerObjArr[i] = p;
            playerObjArr[i].elem.css("zIndex", 90-i);
            moveMe(playerObjArr[i],0,userinit[i][0]);
            moveMe(playerObjArr[i],1,userinit[i][1]);
            //moveMe(playerObjArr[i],0,15);
            //moveMe(playerObjArr[i],1,30);

            //alert(playerObjArr[i].elem.css('zIndex'));
        }
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
            if(super_Board[y][x]==0){
                clonePiece = piece[0].cloneNode(true);
            }
            else if(super_Board[y][x]==1){
                clonePiece = piece[1].cloneNode(true);
            }
            else if(super_Board[y][x]==2){
                clonePiece = piece[2].cloneNode(true);
            }
            else if(super_Board[y][x]==3){
                clonePiece = piece[3].cloneNode(true);
            }
            else{
                
            }
            /*
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
            }*/
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
    console.log("move.length"+move.length);
    //for(var i = 0; i < move.length ; i++){
    for(id in move){
        switch(move[id].action){
            case "l":
                moveMe(playerObjArr[id],1,-1);
                break;
            case "u":
                moveMe(playerObjArr[id],0,-1);
                break;
            case "r":
                moveMe(playerObjArr[id],1,1);
                break;
            case "d":
                moveMe(playerObjArr[id],0,1);
                break;
            default:
                //alert("movePlayers error");
                break;
        }
        if(move[id].isOccupy){
            //occupy the land
            console.log("occupy");
        }
    }   
}
function moveMe(me,left,mv){
    if(left==1){
        me.elem.animate({left:"+="+mv*32+"px"},'fast');
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
        //alert("me.x:"+me.x);
    }
    else{
        me.elem.animate({top:"+="+mv*32+"px"},'fast');
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
        //alert("me.y:"+me.y);
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

function playerKeyDown(me,BoardObj){
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
    
    $( "form" ).submit(function( event ) {
        conObj.sendMsg($("#code").val());
        event.preventDefault();
    });
    conObj.init();
    
    $(".linedtext").linedtextarea();
    $("#code").keydown(function (e) {
        if (e.ctrlKey && e.keyCode == 13) {
            // Ctrl-Enter pressed
            conObj.sendMsg($("#code").val());
            e.preventDefault();
        }
    });
    
    /*myname = 0;
    username.push("Me");
    username.push("R2D2");
    username.push("Trooper");
    username.push("Ewok");
    createPlayer(username);
    
    //playerKeyDown(playerObjArr[myname],BoardObj,conObj);
    moveMe(playerObjArr[1],1,15);
    moveMe(playerObjArr[2],0,7);
    moveMe(playerObjArr[3],1,15);
    moveMe(playerObjArr[3],0,7);
    moveMe(playerObjArr[3],0,-7);*/

});
