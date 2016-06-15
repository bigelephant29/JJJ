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
            showOnScreen("Updating code...",1);
            var msg = {"code": message};
            console.log(conObj.socket.send(JSON.stringify(msg)));
            console.log(message);
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

                        showOnScreen("Waiting for more players...");
                        var msg = {"ready":1};
                        conObj.socket.send(JSON.stringify(msg));
                        break;
                    case "myname"://myname
                        myname = data[key];
                        console.log("myname " + myname);
                        break;
                    case "username"://username[]
                        username = data[key];
                        break;
                    case "userinit"://userinit[] (.x .y)
                        userinit = data[key];
                        createPlayer(username,userinit);
						$('.Loading').css("display","none");
                        BoardObj.elem.css("visibility","visible");
                        showOnScreen("Ready?");
                        break;
                    case "move"://move[]
                        move = data[key];
                        //console.log("move "+move[0].isOccupy);
                        movePlayers(move);
                        break;
                    case "score":
                        score = data[key];
                        var cnt = 1;
                        for(var id in score)
                            cnt += (score[id]>score[myname]);
                        showOnScreen("Rank #"+cnt);
                        break;
                    case "position":
                        //alert("myname: " + myname);
                        var p = new playerObj(myname,myname,data[key][0],data[key][1]);
                        
                        playerObjArr[myname] = p;
                        playerObjArr[myname].elem.css("zIndex", 90-myname);
                        moveMe(playerObjArr[myname],0,data[key][0]);
                        moveMe(playerObjArr[myname],1,data[key][1]);
                        changeFloor(myname,0,0,data[key][1],data[key][0]);
                        //alert("0x:"+data[key][1]+" 0y:"+data[key][0]);
                        //alert("x:"+playerObjArr[myname].x+" y:"+playerObjArr[myname].y);
                        var color;
                        switch(myname){
                        	case 0:
                        		color = "YELLOW";
                        		break;
                        	case 1:
                        		color = "PURPLE";
                        		break;
                        	case 2:
                        		color = "RED";
                        		break;
                        	case 3:
                        		color = "BLUE";
                        		break;
                        }
                        showOnScreen("You are team "+color+"!");

                        break;
                    case "error":
                        showOnScreen("Error: line #"+(data[key]+1));
                        break;
                    case "remaintime":
                        var t = data[key]
                        if(t == 0)
                            showOnScreen("Go!",1);
                        else
                            showOnScreen(t);
                        break;
                    default:
                        showOnScreen("Unknown message!");
                        break;
                }

            }
        }
    };

  
function showOnScreen(message,sec){
    $("#message").text(message);
    $("#message").css("opacity",1);
    if(sec != undefined)
        $("#message").delay(sec*1000).animate({opacity: 0},"slow");
}

//class
function playerObj(playerName,playerNum,x,y){
    this.playerName = playerName;
    this.playerNum = playerNum;
    this.x = 0;
    this.y = 0;

    var playerImg;
    switch(playerNum){
        case 0:
            playerImg = "platearmor";
            break;
        case 1:
            playerImg = "deathknight";
            break;
        case 2:
            playerImg = "fox";
            break;
        case 3:
        	playerImg = "leatherarmor";
        	break;
        default:
            //alert("playerNum overflow "+playerNum);
            break;
    }
    $("#board").append("<div class='Player' id='"+playerName+"'></div>");

    this.elem = $('#'+playerName);

    this.elem.css("background-image","url(../static/"+playerImg+".png)");
    this.elem.css({"top":"-24px","left":"-10px"});
}
function createPlayer(username,userinit){
    for(var i = 0; i < username.length; i++){
        if(username[i]!=myname){
            var p = new playerObj(username[i],i,0,0);
            playerObjArr[i] = p;
            playerObjArr[i].elem.css("zIndex", 90-i);
            console.log("@@@@@@@@@@userinit[i][0]: "+userinit[i][0]+" userinit[i][1]: "+userinit[i][1]);
            moveMe(playerObjArr[i],0,userinit[i][0]);
            moveMe(playerObjArr[i],1,userinit[i][1]);
            
            //moveMe(playerObjArr[i],0,15);
            //moveMe(playerObjArr[i],1,30);

            //alert(playerObjArr[i].elem.css('zIndex'));
            changeFloor(i,0,0,userinit[i][1],userinit[i][0]);
            console.log("@@@@@@@@@@");
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
                //clonePiece.style.backgroundImage="url(../static/Grass0.png)";
            }
            else if(super_Board[y][x]==1){
                clonePiece = piece[1].cloneNode(true);
                //clonePiece.style.backgroundImage="url(../static/Rock.png)";
            }
            else if(super_Board[y][x]==2){
                clonePiece = piece[2].cloneNode(true);
                //clonePiece.style.backgroundImage="url(../static/Flower.png)";
            }
            else if(super_Board[y][x]==3){
                clonePiece = piece[3].cloneNode(true);
                //clonePiece.style.backgroundImage="url(../static/Tree.png)";
            }
            else{
                
            }
            clonePiece.id = x+","+y;
            board_position[y].push(clonePiece.id);
            clonePiece.onclick = function(){
                //alert("coordinate:"+this.id);
            }
            clonePiece.style.left=x*32+"px";
            clonePiece.style.top=y*32+"px";
            boardPiece.appendChild(clonePiece);
        }
    }

}
function changeFloor(id,x,y,toX,toY){
    var board_name = toX+","+toY;
    var imgIndex = super_Board[toY][toX];
    //console.log("board_name:"+board_name);
    //console.log("imgIndex:"+imgIndex);

    //console.log(document.getElementById(board_name).src);
    var bn = document.getElementById(board_name);
    if(id==0){
        //console.log("id:"+id);
        switch(imgIndex){
            case 0:
                //bn.style.backgroundImage = "url(./static/Yellow/Yellow_Grass.png)";
                bn.className = "";
                bn.className += "YCell0";
                break;
            case 1:
                //bn.style.backgroundImage = "url(./static/Yellow/Yellow_Rock.png)";
                bn.className = "";
                bn.className += "YCell1";
                break;
            case 2:
                //bn.style.backgroundImage = "url(./static/Yellow/Yellow_Flower.png)";
                bn.className = "";
                bn.className += "YCell2";
                break;
        }
    }
    else if (id==1){
        //console.log("id:"+id);
        switch(imgIndex){
            case 0:
                //bn.style.backgroundImage = "url(./static/Purple/Purple_Grass.png)";
                bn.className = "";
                bn.className += "PCell0";
                break;
            case 1:
                //bn.style.backgroundImage = "url(./static/Purple/Purple_Rock.png)";
                bn.className = "";
                bn.className += "PCell1";
                break;
            case 2:
                //bn.style.backgroundImage = "url(./static/Purple/Purple_Flower.png)";
                bn.className = "";
                bn.className += "PCell2";
                break;
        }
    }
    else if(id==2){
        //console.log("id:"+id);
        switch(imgIndex){
            case 0:
                //bn.style.backgroundImage = "url(./static/Red/Red_Grass.png)";
                bn.className = "";
                bn.className += "RCell0";
                break;
            case 1:
                //bn.style.backgroundImage = "url(./static/Red/Red_Rock.png)";
                bn.className = "";
                bn.className += "RCell1";
                break;
            case 2:
                //bn.style.backgroundImage = "url(./static/Red/Red_Flower.png)";
                bn.className = "";
                bn.className += "RCell2";
                break;
        }
    }
    else if(id==3){
        //console.log("id:"+id);
        switch(imgIndex){
            case 0:
                //bn.style.backgroundImage = "url(./static/Blue/Blue_Grass.png)";
                bn.className = "";
                bn.className += "BCell0";
                break;
            case 1:
                //bn.style.backgroundImage = "url(./static/Blue/Blue_Rock.png)";
                bn.className = "";
                bn.className += "BCell1";
                break;
            case 2:
                //bn.style.backgroundImage = "url(./static/Blue/Blue_Flower.png)";
                bn.className = "";
                bn.className += "BCell2";
                break;
        }
    }
    else{
        console.log("changeFloor error. "+id);
    }
}
function movePlayers(move){
    //for(var i = 0; i < move.length ; i++){
    for(id in move){
        var isHold = 0;
        console.log("--------------------------player"+id+"("+playerObjArr[id].x+","+playerObjArr[id].y+")");
        console.log("move[id].direction "+move[id].direction);
        
        switch(move[id].direction){
            case "l":
                playerObjArr[id].elem.addClass("left");
                playerObjArr[id].elem.removeClass("up down right");
                break;
            case "u":
                playerObjArr[id].elem.addClass("up");
                playerObjArr[id].elem.removeClass("down left right");
                break;
            case "r":
                playerObjArr[id].elem.addClass("right");
                playerObjArr[id].elem.removeClass("up down left");
                break;
            case "d":
                playerObjArr[id].elem.addClass("down");
                playerObjArr[id].elem.removeClass("up left right");
                break;
            case "h":
                isHold = 1;
                break;
            default:
                //alert("movePlayers error");
                break;
        }
        if(isHold==0){
            var temp_l=move[id].position[1]-playerObjArr[id].x,temp_u=move[id].position[0]-playerObjArr[id].y;
            var pX = playerObjArr[id].x, pY = playerObjArr[id].y,toX = move[id].position[1], toY = move[id].position[0];
            console.log("temp_l:"+temp_l+" temp_u:"+temp_u);
            console.log("move[id].position[1]: "+move[id].position[1]+" move[id].position[0]: "+move[id].position[0]);
            console.log("playerObjArr[id].x: "+playerObjArr[id].x+ " playerObjArr[id].y:"+playerObjArr[id].y);

            if(temp_l!=0){
                moveMe(playerObjArr[id],1,temp_l);
                if(move[id].isOccupy)    changeFloor(id,pX,pY,toX,toY);
            }
            if(temp_u!=0){
                moveMe(playerObjArr[id],0,temp_u);
                if(move[id].isOccupy)    changeFloor(id,pX,pY,toX,toY);
            }
        }
        console.log("-------------------------------------------------");
    }   
}
function moveMe(me,left,mv){
    console.log(me.x+" "+me.y+"{{{{{{{moveMe}}}}}}"+left+" "+mv);
    if(left==1){
        if(me.x+mv >= 0 && me.x+mv <= 89){
            var tx = me.x;
            me.elem.animate({left:"+="+mv*32+"px"},{
            duration:'fast',start:function(){
                    console.log("[moveme]in x:"+me.x);
                    if(me.playerName == myname){
                        if(mv>0){        
                            if(((tx % 30) == 29) && ((tx / 30) < 2)){
                                moveBoard(BoardObj,1,-30);
                            }
                        }
                        else{
                            if(((tx % 30) == 0) && ((tx / 30) >= 1)){
                                moveBoard(BoardObj,1,30);
                            }
                        }
                    }
                }
            });
            me.x+=mv;
            console.log("[moveme]out x:"+me.x);
        }
    }
    else{
        if(me.y+mv >= 0 && me.y+mv <= 44){
            var ty = me.y;
            me.elem.animate({top:"+="+mv*32+"px"},{
            duration:'fast',
                start:function(){
                    console.log("[moveme]in y:"+me.y);
                    if(me.playerName == myname){
                        if(mv>0){
                            if(((ty % 15) == 14) && ((ty / 15) < 2)){
                                moveBoard(BoardObj,0,-15);
                            }
                        }
                        else{
                            if(((ty % 15) == 0) && ((ty / 15) >= 1)){
                                moveBoard(BoardObj,0,15);
                            }
                        }
                    }
                }
            });
            me.y+=mv;
            console.log("[moveme]out y:"+me.y);
        }
    }
    console.log("{{{{{{{moveMe}}}}}}");
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
    conObj.init();
    
    $(".linedtext").linedtextarea();
    $("#code").keydown(function (e) {
        if (e.ctrlKey && e.keyCode == 13) {
            // Ctrl-Enter pressed
            conObj.sendMsg($("#code").val());
            e.preventDefault();
        }
    });
    /*$( "form" ).submit(function( event ) {
        conObj.sendMsg($("textarea:first").val());
        console.log($("textarea:first").val());
        event.preventDefault();
    });
    conObj.init()*/
    
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
