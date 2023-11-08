function refresh() {
    fetch("/gomoku/api/"+ gameId + "/refresh")
            .then(response => response.json())
            .then(refreshScreen);
}

function renderPiece(row, column, color) {
    document.getElementsByClassName("triggers")[0].children[0]
                .children[row]
                .children[column]

                .children[0].children[0].setAttribute("src", "/static/gomoku/pieces/" + color + ".png")
}

let isMyTurn = false;
let myColor = null;

function refreshScreen(data) {
    console.log(data)
    let board = data.current_board
    isMyTurn = data.is_your_turn
    myColor = data.your_color
    currentPlayers = data.current_players

    if (data.ended) {
        alert("Game ended, " + data.won_color + " won")
        refresh()
    }

    for (let row = 0; row < 15; row++) {
        for (let column = 0; column < 15; column++) {
            let color = board[row][column]
            if (color !== null) {
                renderPiece(row, column, color)
            } else {
                renderPiece(row, column, "none")
            }
        }
    }

    for (const [color, ip] of Object.entries(currentPlayers)) {
        if (ip != null) {
            document.getElementsByClassName("player-display-property-" + color)[0].innerHTML =`
                <p>`+ ip +`</p>
                <img src="/static/gomoku/pieces/` + color +`.png" alt="Piece">
                `
        } else {
            document.getElementsByClassName("player-display-property-" + color)[0].innerHTML = `
                <a onclick="fetch('/gomoku/api/` + gameId + "/" + color + `/join')">
                    Join as ` + color + `
                </a>
            `
        }

    }
}

setInterval(
    refresh,
    500
) // online check every second

function placePiece(row, column) {
    console.log("" + row + ", " + column)
    fetch("/gomoku/api/"+ gameId + "/place_piece/" + row + "/" + column)
    // if (isMyTurn) {
    //     renderPiece(row, column, myColor)
    // }
}