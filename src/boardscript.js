var board = [];
var board_position = [];
var piece = [];
var boardPiece;

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
    boardPiece.appendChild(piece[4]);
    for(var y=0;y<45;y++){
        for(var x=0;x<90;x++){
            var ran=Math.floor((Math.random() * 9))
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
                    clonePiece = piece[1].cloneNode(true);
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

function moveMe(me,left,mv){
    if(left==1){
        me.elem.animate({left:"+="+mv+"px"},'fast');
    }
    else{
        me.elem.animate({top:"+="+mv+"px"},'fast');
    }
}

function moveBoard(boardObj,left,mv){
    if(left==1 ){
            boardObj.elem.animate({left:"+="+mv+"px"},'fast');
    }
    else{
        boardObj.elem.animate({top:"+="+mv+"px"},'fast');
    }
}

function playerKeyDown(me,conObj){
    $(document).keydown(function(key) {
        switch(parseInt(key.which,10)) {
            // Left arrow key pressed
            case 37:
                if(me.x > 0){
                    me.elem.animate({left: "-=32px"}, 'fast');
                    me.x -= 1;
                }
                break;
            // Up Arrow Pressed
            case 38:
                if(me.y > 0){
                    me.elem.animate({top: "-=32px"}, 'fast');
                    me.y -= 1;
                }
                break;
            // Right Arrow Pressed
            case 39:
                if(me.x < 29){
                    me.elem.animate({left: "+=32px"}, 'fast');
                    me.x += 1;
                }
                break;
            // Down Arrow Pressed
            case 40:
                if(me.y < 14){
                    me.elem.animate({top: "+=32px"}, 'fast');
                    me.y += 1;
                }
                break;
        }
        conObj.sendMsg();
    });
}

$(document).ready(function() {
    board_position = Create2DArray(45);
    var Me = {elem:$('#me'),playerName:"test",x:0,y:0};
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
        }
    };

    moveBoard(BoardObj,0,-960);
    moveBoard(BoardObj,1,-480);
    moveMe(Me,0,960);
    moveMe(Me,1,480);
    initBoard();
    playerKeyDown(Me,connectObj);
});




/*
map: 2dArray


*/